import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.workspace import Workspace
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.workspace import (
    WorkspaceCreate,
    WorkspaceListResponse,
    WorkspaceResponse,
    WorkspaceStatsResponse,
    WorkspaceUpdate,
)


class WorkspaceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.workspace_repository = WorkspaceRepository(db)

    def ensure_user_workspace(self, user: User) -> Workspace:
        workspace = self.workspace_repository.get_primary_by_owner(user.id)
        if workspace is None:
            workspace = self.workspace_repository.create(
                name=self._default_workspace_name(user),
                description="Personal knowledge workspace",
                owner_id=user.id,
            )
        return workspace

    def get_user_workspace(self, user: User) -> Workspace:
        return self.ensure_user_workspace(user)

    def get_owned_workspace(self, user: User, workspace_id: uuid.UUID) -> Workspace:
        return self._get_owned_workspace(user, workspace_id)

    def create_workspace(self, user: User, workspace_in: WorkspaceCreate) -> WorkspaceResponse:
        existing = self.workspace_repository.get_primary_by_owner(user.id)
        if existing is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User already has a workspace",
            )
        workspace = self.workspace_repository.create(
            name=workspace_in.name,
            description=workspace_in.description,
            owner_id=user.id,
        )
        return WorkspaceResponse.model_validate(workspace)

    def get_workspace(self, user: User, workspace_id: uuid.UUID) -> WorkspaceResponse:
        workspace = self._get_owned_workspace(user, workspace_id)
        return WorkspaceResponse.model_validate(workspace)

    def list_workspaces(self, user: User) -> WorkspaceListResponse:
        workspaces = self.workspace_repository.get_all_by_owner(user.id)
        items = [WorkspaceResponse.model_validate(workspace) for workspace in workspaces]
        return WorkspaceListResponse(items=items, total=len(items))

    def update_workspace(
        self,
        user: User,
        workspace_id: uuid.UUID,
        workspace_in: WorkspaceUpdate,
    ) -> WorkspaceResponse:
        workspace = self._get_owned_workspace(user, workspace_id)
        update_data = workspace_in.model_dump(exclude_unset=True)
        updated_workspace = self.workspace_repository.update(workspace, **update_data)
        return WorkspaceResponse.model_validate(updated_workspace)

    def delete_workspace(self, user: User, workspace_id: uuid.UUID) -> None:
        workspace = self._get_owned_workspace(user, workspace_id)
        self.workspace_repository.delete(workspace)

    def get_workspace_stats(self, user: User, workspace_id: uuid.UUID) -> WorkspaceStatsResponse:
        workspace = self._get_owned_workspace(user, workspace_id)
        return WorkspaceStatsResponse(
            workspace_id=workspace.id,
            document_count=self.workspace_repository.count_documents(workspace.id),
            source_count=self.workspace_repository.count_sources(workspace.id),
            chat_count=self.workspace_repository.count_chats(workspace.id),
            created_at=workspace.created_at,
        )

    def _default_workspace_name(self, user: User) -> str:
        if user.full_name:
            return user.full_name
        return user.email.split("@")[0]

    def _get_owned_workspace(self, user: User, workspace_id: uuid.UUID) -> Workspace:
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
        return workspace
