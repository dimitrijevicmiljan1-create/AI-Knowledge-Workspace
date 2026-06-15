import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.search_history import SearchHistory
from app.models.source import Source
from app.models.user import User
from app.repositories.github_connection_repository import GitHubConnectionRepository
from app.repositories.user_settings_repository import UserSettingsRepository
from app.schemas.settings import (
    IntegrationStatusResponse,
    UsageStatsResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
)
from app.services.workspace_service import WorkspaceService


class SettingsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.settings_repository = UserSettingsRepository(db)
        self.workspace_service = WorkspaceService(db)
        self.github_connection_repository = GitHubConnectionRepository(db)

    def get_settings(self, user: User) -> UserSettingsResponse:
        settings = self.settings_repository.get_or_create(user.id)
        return UserSettingsResponse.model_validate(settings)

    def update_settings(self, user: User, settings_in: UserSettingsUpdate) -> UserSettingsResponse:
        settings = self.settings_repository.get_or_create(user.id)
        update_data = settings_in.model_dump(exclude_unset=True)
        updated = self.settings_repository.update(settings, **update_data)
        return UserSettingsResponse.model_validate(updated)

    def get_integrations(self, user: User) -> IntegrationStatusResponse:
        connection = self.github_connection_repository.get_by_user_id(user.id)
        return IntegrationStatusResponse(
            github_connected=connection is not None,
            github_username=connection.github_username if connection else None,
            notion_connected=False,
            google_drive_connected=False,
        )

    def get_usage(self, user: User) -> UsageStatsResponse:
        workspace = self.workspace_service.get_user_workspace(user)
        document_count = self._count_documents(workspace.id)
        chunk_count = self._count_chunks(workspace.id)
        storage_bytes = self._sum_document_sizes(workspace.id)
        query_count = self._count_queries(user.id, workspace.id)
        return UsageStatsResponse(
            documents=document_count,
            chunks=chunk_count,
            storage_bytes=storage_bytes,
            queries=query_count,
        )

    def _count_documents(self, workspace_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Document)
            .join(Source, Document.source_id == Source.id)
            .where(Source.workspace_id == workspace_id)
        )
        return self.db.scalar(statement) or 0

    def _count_chunks(self, workspace_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Chunk)
            .join(Document, Chunk.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
            .where(Source.workspace_id == workspace_id)
        )
        return self.db.scalar(statement) or 0

    def _sum_document_sizes(self, workspace_id: uuid.UUID) -> int:
        documents = (
            self.db.scalars(
                select(Document)
                .join(Source, Document.source_id == Source.id)
                .where(Source.workspace_id == workspace_id)
            ).all()
        )
        total = 0
        for document in documents:
            size = document.document_metadata.get("size")
            if isinstance(size, int):
                total += size
        return total

    def _count_queries(self, user_id: uuid.UUID, workspace_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(SearchHistory)
            .where(
                SearchHistory.user_id == user_id,
                SearchHistory.workspace_id == workspace_id,
            )
        )
        return self.db.scalar(statement) or 0
