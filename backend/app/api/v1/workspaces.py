from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListResponse,
    WorkspaceResponse,
    WorkspaceStatsResponse,
    WorkspaceUpdate,
)
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create workspace",
    responses={
        201: {
            "description": "Workspace created successfully",
            "content": {
                "application/json": {
                    "example": {
                        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "name": "Research Hub",
                        "description": "Primary workspace for AI research documents",
                        "owner_id": "3fa85f64-5717-4562-b3fc-2c963f66afa7",
                        "created_at": "2026-06-12T12:00:00Z",
                        "updated_at": "2026-06-12T12:00:00Z",
                    }
                }
            },
        }
    },
)
def create_workspace(
    workspace_in: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceResponse:
    return WorkspaceService(db).create_workspace(current_user, workspace_in)


@router.get(
    "",
    response_model=WorkspaceListResponse,
    summary="List user workspaces",
)
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceListResponse:
    return WorkspaceService(db).list_workspaces(current_user)


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get workspace details",
    responses={
        404: {"description": "Workspace not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def get_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceResponse:
    return WorkspaceService(db).get_workspace(current_user, workspace_id)


@router.patch(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Update workspace",
    responses={
        404: {"description": "Workspace not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def update_workspace(
    workspace_id: UUID,
    workspace_in: WorkspaceUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceResponse:
    return WorkspaceService(db).update_workspace(current_user, workspace_id, workspace_in)


@router.delete(
    "/{workspace_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete workspace",
    responses={
        404: {"description": "Workspace not found"},
        403: {"description": "User is not the workspace owner"},
    },
)
def delete_workspace(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> Response:
    WorkspaceService(db).delete_workspace(current_user, workspace_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get(
    "/{workspace_id}/stats",
    response_model=WorkspaceStatsResponse,
    summary="Get workspace statistics",
    responses={
        404: {"description": "Workspace not found"},
        403: {"description": "User is not the workspace owner"},
        200: {
            "description": "Workspace statistics",
            "content": {
                "application/json": {
                    "example": {
                        "workspace_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                        "document_count": 12,
                        "source_count": 3,
                        "chat_count": 5,
                        "created_at": "2026-06-12T12:00:00Z",
                    }
                }
            },
        },
    },
)
def get_workspace_stats(
    workspace_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> WorkspaceStatsResponse:
    return WorkspaceService(db).get_workspace_stats(current_user, workspace_id)
