import uuid

from sqlalchemy.orm import Session

from app.models.source import Source, SourceStatus, SourceType
from app.repositories.source_repository import SourceRepository

# Knowledge integrations that participate in workspace chat retrieval.
RETRIEVAL_SOURCE_TYPES: tuple[SourceType, ...] = (
    SourceType.github,
    SourceType.local_files,
    SourceType.obsidian,
    SourceType.manual,
)


class RetrievalSourceService:
    """Resolve which workspace sources are eligible for RAG retrieval."""

    def __init__(self, db: Session) -> None:
        self.source_repository = SourceRepository(db)

    def list_retrieval_source_ids(self, workspace_id: uuid.UUID) -> list[uuid.UUID]:
        searchable = self.source_repository.list_searchable_source_ids(
            workspace_id,
            source_types=RETRIEVAL_SOURCE_TYPES,
        )
        if searchable:
            return searchable

        # Fall back to ready sources so newly synced integrations are included
        # even before embedding counts are visible in the same transaction.
        return [
            source.id
            for source in self.source_repository.list_retrieval_ready_by_workspace(
                workspace_id,
                source_types=RETRIEVAL_SOURCE_TYPES,
            )
        ]

    def list_retrieval_sources(self, workspace_id: uuid.UUID) -> list[Source]:
        return self.source_repository.list_retrieval_ready_by_workspace(
            workspace_id,
            source_types=RETRIEVAL_SOURCE_TYPES,
        )
