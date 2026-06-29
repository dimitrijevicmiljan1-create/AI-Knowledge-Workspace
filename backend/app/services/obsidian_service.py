import logging
import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.obsidian_sync_job import ObsidianSyncJob
from app.models.obsidian_vault import ObsidianVault, ObsidianVaultSyncStatus
from app.models.source import SourceType
from app.models.user import User
from app.obsidian.filters import should_index_obsidian_path
from app.obsidian.sync import ObsidianSyncService, ObsidianVaultFile
from app.repositories.chunk_repository import ChunkRepository
from app.repositories.document_repository import DocumentRepository
from app.repositories.embedding_repository import EmbeddingRepository
from app.repositories.obsidian_vault_repository import ObsidianVaultRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.obsidian import (
    ObsidianIndexStatsResponse,
    ObsidianSyncJobResponse,
    ObsidianVaultCreateRequest,
    ObsidianVaultListResponse,
    ObsidianVaultResponse,
    ObsidianVaultSyncResponse,
    ObsidianVectorChunkSample,
    ObsidianVectorStoreDebugResponse,
)

logger = logging.getLogger(__name__)


class ObsidianService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.vault_repository = ObsidianVaultRepository(db)
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)
        self.document_repository = DocumentRepository(db)
        self.chunk_repository = ChunkRepository(db)
        self.embedding_repository = EmbeddingRepository(db)
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

        logger.info(
            "Obsidian upload accepted vault_id=%s markdown_files=%d paths=%s",
            vault_id,
            len(parsed_files),
            [item.relative_path for item in parsed_files[:5]],
        )

        job = self.sync_service.start_sync(vault_id, user, parsed_files)
        return ObsidianVaultSyncResponse(
            job_id=job.id,
            vault_id=vault_id,
            status=job.status.value,
        )

    def get_index_stats(self, user: User, vault_id: uuid.UUID) -> ObsidianIndexStatsResponse:
        vault = self._get_owned_vault(user, vault_id)
        source = vault.source
        documents = self.document_repository.list_by_source(vault.source_id)
        total_chunks = sum(self.chunk_repository.count_by_document(document.id) for document in documents)
        embeddings_stored = self.embedding_repository.count_by_source(vault.source_id)
        vector_chunks = self.embedding_repository.count_by_metadata_source(
            vault.workspace_id,
            metadata_source="obsidian",
        )
        latest_job = self.sync_service.get_latest_job(vault_id)

        logger.info(
            "Obsidian index stats vault_id=%s documents=%d chunks=%d embeddings=%d vector_chunks=%d paths=%s",
            vault_id,
            len(documents),
            total_chunks,
            embeddings_stored,
            vector_chunks,
            [document.path for document in documents[:10]],
        )

        return ObsidianIndexStatsResponse(
            vault_id=vault.id,
            source_id=vault.source_id,
            workspace_id=vault.workspace_id,
            source_status=source.status.value if source else "unknown",
            markdown_files_discovered=latest_job.files_scanned if latest_job else 0,
            documents_indexed=len(documents),
            chunks_created=total_chunks,
            embeddings_stored=embeddings_stored,
            vector_chunks_for_source=vector_chunks,
        )

    def get_vector_store_debug(
        self,
        user: User,
        workspace_id: uuid.UUID,
    ) -> ObsidianVectorStoreDebugResponse:
        self._ensure_workspace_owner(user, workspace_id)
        total_documents = self.embedding_repository.count_documents_by_metadata_source(
            workspace_id,
            metadata_source="obsidian",
        )
        total_chunks = self.embedding_repository.count_by_metadata_source(
            workspace_id,
            metadata_source="obsidian",
        )
        sample_rows = self.embedding_repository.list_sample_chunks_by_metadata_source(
            workspace_id,
            metadata_source="obsidian",
            limit=5,
        )
        documents = [
            document
            for document in self.document_repository.list_by_workspace(workspace_id)
            if (document.document_metadata or {}).get("source") == "obsidian"
        ]
        indexed_paths = sorted(document.path for document in documents)

        logger.info(
            "Obsidian vector store debug workspace_id=%s documents=%d chunks=%d sample_paths=%s",
            workspace_id,
            total_documents,
            total_chunks,
            indexed_paths,
        )

        return ObsidianVectorStoreDebugResponse(
            workspace_id=workspace_id,
            total_documents=total_documents,
            total_chunks=total_chunks,
            sample_chunks=[
                ObsidianVectorChunkSample(
                    chunk_id=row["chunk_id"],
                    document_id=row["document_id"],
                    document_title=row["document_title"],
                    document_path=row["document_path"],
                    chunk_content=row["chunk_content"],
                    metadata=row["metadata"],
                    source_type=row["source_type"],
                )
                for row in sample_rows
            ],
            indexed_paths=indexed_paths,
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
        skipped: list[str] = []

        for relative_path, content_bytes in files:
            if not relative_path.lower().endswith(".md"):
                skipped.append(f"{relative_path}: not markdown")
                continue

            try:
                content = content_bytes.decode("utf-8")
            except UnicodeDecodeError:
                content = content_bytes.decode("utf-8", errors="replace")

            normalized_path = self._normalize_relative_path(relative_path, vault_name)
            if not content.strip():
                skipped.append(f"{normalized_path}: empty content")
                continue
            if not should_index_obsidian_path(normalized_path):
                skipped.append(f"{normalized_path}: excluded path")
                continue

            parsed.append(ObsidianVaultFile(relative_path=normalized_path, content=content))

        logger.info(
            "Obsidian file discovery vault_name=%s markdown_files=%d skipped=%d paths=%s",
            vault_name,
            len(parsed),
            len(skipped),
            [item.relative_path for item in parsed[:10]],
        )
        if skipped:
            logger.info("Obsidian skipped files (first 10): %s", skipped[:10])

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
