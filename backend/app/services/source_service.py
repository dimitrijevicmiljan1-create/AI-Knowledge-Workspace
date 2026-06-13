import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.source import Source, SourceStatus, SourceType
from app.models.user import User
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.source import (
    SourceCreate,
    SourceListResponse,
    SourceResponse,
    SourceStatsResponse,
    SourceUpdate,
    SourceValidationResult,
)
from app.services.source_validators import validate_source_config


class SourceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)

    def create_source(self, user: User, source_in: SourceCreate) -> SourceResponse:
        self._ensure_workspace_owner(user, source_in.workspace_id)
        validation = self.validate_source(source_in.source_type, source_in.config)
        self._raise_if_invalid(validation)

        source = self.source_repository.create(
            workspace_id=source_in.workspace_id,
            name=source_in.name,
            source_type=source_in.source_type,
            config=source_in.config,
            status=SourceStatus.pending,
        )
        return SourceResponse.model_validate(source)

    def get_source(self, user: User, source_id: uuid.UUID) -> SourceResponse:
        source = self._get_owned_source(user, source_id)
        return SourceResponse.model_validate(source)

    def list_sources(self, user: User, workspace_id: uuid.UUID) -> SourceListResponse:
        self._ensure_workspace_owner(user, workspace_id)
        sources = self.source_repository.list_by_workspace(workspace_id)
        items = [SourceResponse.model_validate(source) for source in sources]
        return SourceListResponse(items=items, total=len(items))

    def update_source(
        self,
        user: User,
        source_id: uuid.UUID,
        source_in: SourceUpdate,
    ) -> SourceResponse:
        source = self._get_owned_source(user, source_id)
        update_data = source_in.model_dump(exclude_unset=True)

        if "config" in update_data:
            validation = self.validate_source(source.source_type, update_data["config"])
            self._raise_if_invalid(validation)

        updated_source = self.source_repository.update(source, **update_data)
        return SourceResponse.model_validate(updated_source)

    def delete_source(self, user: User, source_id: uuid.UUID) -> None:
        source = self._get_owned_source(user, source_id)
        self.source_repository.delete(source)

    def get_source_stats(self, user: User, source_id: uuid.UUID) -> SourceStatsResponse:
        source = self._get_owned_source(user, source_id)
        return SourceStatsResponse(
            source_id=source.id,
            document_count=self.source_repository.count_documents(source.id),
            chunk_count=self.source_repository.count_chunks(source.id),
            last_sync_at=source.last_sync_at,
            status=source.status,
        )

    def validate_source(self, source_type: SourceType, config: dict) -> SourceValidationResult:
        return validate_source_config(source_type, config)

    def _get_owned_source(self, user: User, source_id: uuid.UUID) -> Source:
        source = self.source_repository.get_by_id(source_id)
        if source is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Source not found",
            )
        self._ensure_workspace_owner(user, source.workspace_id)
        return source

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

    def _raise_if_invalid(self, validation: SourceValidationResult) -> None:
        if validation.valid:
            return
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "message": "Source configuration validation failed",
                "errors": [error.model_dump() for error in validation.errors],
            },
        )
