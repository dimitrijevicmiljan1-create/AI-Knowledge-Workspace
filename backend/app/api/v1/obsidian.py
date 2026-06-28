from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, Query, Response, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.obsidian import (
    ObsidianIndexStatsResponse,
    ObsidianSyncJobResponse,
    ObsidianVaultCreateRequest,
    ObsidianVaultListResponse,
    ObsidianVaultResponse,
    ObsidianVaultSyncResponse,
)
from app.services.obsidian_service import ObsidianService

router = APIRouter(prefix="/obsidian", tags=["obsidian"])


@router.get(
    "/vaults",
    response_model=ObsidianVaultListResponse,
    summary="List Obsidian vaults for a workspace",
)
def list_obsidian_vaults(
    workspace_id: UUID = Query(..., description="Workspace identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ObsidianVaultListResponse:
    return ObsidianService(db).list_vaults(current_user, workspace_id)


@router.post(
    "/vaults",
    response_model=ObsidianVaultResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register an Obsidian vault",
)
def create_obsidian_vault(
    vault_in: ObsidianVaultCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ObsidianVaultResponse:
    return ObsidianService(db).create_vault(current_user, vault_in)


@router.post(
    "/vaults/{vault_id}/sync",
    response_model=ObsidianVaultSyncResponse,
    summary="Sync markdown notes from an uploaded vault folder",
)
async def sync_obsidian_vault(
    vault_id: UUID,
    files: list[UploadFile] = File(..., description="Markdown files from the vault folder"),
    relative_paths: list[str] = Form(default=[]),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ObsidianVaultSyncResponse:
    file_payloads: list[tuple[str, bytes]] = []
    for index, upload in enumerate(files):
        content = await upload.read()
        relative_path = relative_paths[index] if index < len(relative_paths) else (upload.filename or "note.md")
        file_payloads.append((relative_path, content))
    return ObsidianService(db).start_sync(current_user, vault_id, file_payloads)


@router.get(
    "/vaults/{vault_id}/index-stats",
    response_model=ObsidianIndexStatsResponse,
    summary="Get Obsidian vault indexing pipeline statistics",
)
def get_obsidian_index_stats(
    vault_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ObsidianIndexStatsResponse:
    return ObsidianService(db).get_index_stats(current_user, vault_id)


@router.get(
    "/vaults/{vault_id}/status",
    response_model=ObsidianSyncJobResponse,
    summary="Get latest Obsidian vault sync status",
)
def get_obsidian_sync_status(
    vault_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> ObsidianSyncJobResponse:
    return ObsidianService(db).get_sync_status(current_user, vault_id)


@router.delete(
    "/vaults/{vault_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete an Obsidian vault",
)
def delete_obsidian_vault(
    vault_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    ObsidianService(db).delete_vault(current_user, vault_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
