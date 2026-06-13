from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.source import (
    SourceCreate,
    SourceListResponse,
    SourceResponse,
    SourceStatsResponse,
    SourceUpdate,
)
from app.services.source_service import SourceService

router = APIRouter(prefix="/sources", tags=["sources"])

_GITHUB_CREATE_EXAMPLE = {
    "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Engineering Docs",
    "source_type": "github",
    "config": {
        "repository_url": "https://github.com/owner/repo",
        "branch": "main",
    },
}

_OBSIDIAN_CREATE_EXAMPLE = {
    "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Research Vault",
    "source_type": "obsidian",
    "config": {
        "vault_name": "Research Notes",
        "vault_path": "/data/vaults/research",
    },
}

_LOCAL_FILES_CREATE_EXAMPLE = {
    "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Local Documentation",
    "source_type": "local_files",
    "config": {
        "directory_path": "/data/documents",
    },
}

_MANUAL_CREATE_EXAMPLE = {
    "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    "name": "Curated References",
    "source_type": "manual",
    "config": {
        "description": "Hand-picked articles and notes",
    },
}


@router.post(
    "",
    response_model=SourceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create knowledge source",
    responses={
        201: {
            "description": "Source created successfully",
            "content": {
                "application/json": {
                    "examples": {
                        "github": {
                            "summary": "GitHub repository source",
                            "value": {
                                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                                "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                                "name": "Engineering Docs",
                                "source_type": "github",
                                "config": {
                                    "repository_url": "https://github.com/owner/repo",
                                    "branch": "main",
                                },
                                "status": "pending",
                                "last_sync_at": None,
                                "created_at": "2026-06-13T12:00:00Z",
                                "updated_at": "2026-06-13T12:00:00Z",
                            },
                        }
                    }
                }
            },
        },
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Workspace not found"},
        422: {"description": "Source configuration validation failed"},
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {
                        "github": {
                            "summary": "GitHub repository",
                            "value": _GITHUB_CREATE_EXAMPLE,
                        },
                        "obsidian": {
                            "summary": "Obsidian vault",
                            "value": _OBSIDIAN_CREATE_EXAMPLE,
                        },
                        "local_files": {
                            "summary": "Local files directory",
                            "value": _LOCAL_FILES_CREATE_EXAMPLE,
                        },
                        "manual": {
                            "summary": "Manual source",
                            "value": _MANUAL_CREATE_EXAMPLE,
                        },
                    }
                }
            }
        }
    },
)
def create_source(
    source_in: SourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SourceResponse:
    return SourceService(db).create_source(current_user, source_in)


@router.get(
    "",
    response_model=SourceListResponse,
    summary="List workspace knowledge sources",
    responses={
        403: {"description": "User is not the workspace owner"},
        404: {"description": "Workspace not found"},
    },
)
def list_sources(
    workspace_id: UUID = Query(..., description="Workspace identifier"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SourceListResponse:
    return SourceService(db).list_sources(current_user, workspace_id)


@router.get(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Get knowledge source details",
    responses={
        404: {"description": "Source or workspace not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def get_source(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SourceResponse:
    return SourceService(db).get_source(current_user, source_id)


@router.patch(
    "/{source_id}",
    response_model=SourceResponse,
    summary="Update knowledge source",
    responses={
        404: {"description": "Source or workspace not found"},
        403: {"description": "User is not the workspace owner"},
        422: {"description": "Source configuration validation failed"},
    },
)
def update_source(
    source_id: UUID,
    source_in: SourceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SourceResponse:
    return SourceService(db).update_source(current_user, source_id, source_in)


@router.delete(
    "/{source_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete knowledge source",
    responses={
        404: {"description": "Source or workspace not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def delete_source(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    SourceService(db).delete_source(current_user, source_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{source_id}/stats",
    response_model=SourceStatsResponse,
    summary="Get knowledge source statistics",
    responses={
        404: {"description": "Source or workspace not found"},
        403: {"description": "User is not the workspace owner"},
        200: {
            "description": "Source statistics",
            "content": {
                "application/json": {
                    "example": {
                        "source_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "document_count": 8,
                        "chunk_count": 42,
                        "last_sync_at": None,
                        "status": "pending",
                    }
                }
            },
        },
    },
)
def get_source_stats(
    source_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> SourceStatsResponse:
    return SourceService(db).get_source_stats(current_user, source_id)
