import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.obsidian_sync_job import ObsidianSyncJob
from app.models.obsidian_vault import ObsidianVault, ObsidianVaultSyncStatus
from app.models.source import SourceType
from app.models.user import User
from app.obsidian.sync import ObsidianSyncService, ObsidianVaultFile
from app.repositories.obsidian_vault_repository import ObsidianVaultRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.obsidian import (
    ObsidianSyncJobResponse,
    ObsidianVaultCreateRequest,
    ObsidianVaultListResponse,
    ObsidianVaultResponse,
    ObsidianVaultSyncResponse,
)


class ObsidianService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.vault_repository = ObsidianVaultRepository(db)
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)
        self.sync_service = ObsidianSyncService(db)

    def list_vaults(self, user: User, workspace_id: uuid.UUID) -> ObsidianVaultListResponse:
        self._ensure_workspace_owner(user, workspace_id)
        vaults = self.vault_repository.list_by_workspace(workspace_id)
        items = [ObsidianVaultResponse.model_validate(vault) for vault in vaults]
        return ObsidianVaultListResponse(items=items, total=len(items))

    def create_vault(
        self,
        user: User,
        vault_in: ObsidianVaultCreateRequest,
    ) -> ObsidianVaultResponse:
        self._ensure_workspace_owner(user, vault_in.workspace_id)
        existing = self.vault_repository.get_by_workspace_and_name(
            vault_in.workspace_id,
            vault_in.vault_name,
        )
        if existing is not None:
            return ObsidianVaultResponse.model_validate(existing)

        source = self.source_repository.create(
            workspace_id=vault_in.workspace_id,
            name=f"obsidian/{vault_in.vault_name}",
            source_type=SourceType.obsidian,
            config={
                "vault_name": vault_in.vault_name,
                "vault_path": "",
            },
        )
        vault = self.vault_repository.create(
            workspace_id=vault_in.workspace_id,
            source_id=source.id,
            vault_name=vault_in.vault_name,
            sync_status=ObsidianVaultSyncStatus.pending,
        )
        return ObsidianVaultResponse.model_validate(vault)

    def start_sync(
        self,
        user: User,
        vault_id: uuid.UUID,
        files: list[tuple[str, bytes]],
    ) -> ObsidianVaultSyncResponse:
        vault = self._get_owned_vault(user, vault_id)
        parsed_files = self._parse_uploaded_files(files, vault.vault_name)
        if not parsed_files:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="No markdown files found in the selected vault folder",
            )

        job = self.sync_service.start_sync(vault_id, user, parsed_files)
        return ObsidianVaultSyncResponse(
            job_id=job.id,
            vault_id=vault_id,
            status=job.status.value,
        )

    def get_sync_status(self, user: User, vault_id: uuid.UUID) -> ObsidianSyncJobResponse:
        self._get_owned_vault(user, vault_id)
        job = self.sync_service.get_latest_job(vault_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sync job found for vault",
            )
        return self._to_sync_job_response(job)

    def delete_vault(self, user: User, vault_id: uuid.UUID) -> None:
        vault = self._get_owned_vault(user, vault_id)
        source = vault.source
        self.vault_repository.delete(vault)
        if source is not None:
            self.source_repository.delete(source)

    def _get_owned_vault(self, user: User, vault_id: uuid.UUID) -> ObsidianVault:
        vault = self.vault_repository.get_by_id_for_user(vault_id, user.id)
        if vault is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Obsidian vault not found",
            )
        return vault

    def _parse_uploaded_files(
        self,
        files: list[tuple[str, bytes]],
        vault_name: str,
    ) -> list[ObsidianVaultFile]:
        parsed: list[ObsidianVaultFile] = []
        for filename, content_bytes in files:
            if not filename.lower().endswith(".md"):
                continue

            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = content_bytes.decode("utf-8", errors="replace")

            relative_path = self._normalize_relative_path(filename, vault_name)
            parsed.append(ObsidianVaultFile(relative_path=relative_path, content=content))
        return parsed

    def _normalize_relative_path(self, filename: str, vault_name: str) -> str:
        normalized = filename.replace("\\", "/").strip("/")
        if normalized.startswith(f"{vault_name}/"):
            return normalized[len(vault_name) + 1 :]
        return normalized

    def _ensure_workspace_owner(self, user: User, workspace_id: uuid.UUID) -> None:
        workspace = self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        if workspace.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this workspace",
            )

    def _to_sync_job_response(self, job: ObsidianSyncJob) -> ObsidianSyncJobResponse:
        return ObsidianSyncJobResponse(
            id=job.id,
            vault_id=job.vault_id,
            status=job.status.value,
            started_at=job.started_at,
            completed_at=job.completed_at,
            files_scanned=job.files_scanned,
            documents_created=job.documents_created,
            documents_updated=job.documents_updated,
            documents_deleted=job.documents_deleted,
            error_message=job.error_message,
            created_at=job.created_at,
        )
