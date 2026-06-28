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
        sources = self.source_repository.list_retrieval_ready_by_workspace(
            workspace_id,
            source_types=RETRIEVAL_SOURCE_TYPES,
        )
        return [source.id for source in sources]

    def list_retrieval_sources(self, workspace_id: uuid.UUID) -> list[Source]:
        return self.source_repository.list_retrieval_ready_by_workspace(
            workspace_id,
            source_types=RETRIEVAL_SOURCE_TYPES,
        )
