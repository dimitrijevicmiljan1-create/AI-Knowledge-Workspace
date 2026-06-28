import uuid

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.source import Source, SourceStatus, SourceType


class SourceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        workspace_id: uuid.UUID,
        name: str,
        source_type: SourceType,
        config: dict,
        status: SourceStatus = SourceStatus.pending,
    ) -> Source:
        source = Source(
            workspace_id=workspace_id,
            name=name,
            source_type=source_type,
            config=config,
            status=status,
        )
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_by_id(self, source_id: uuid.UUID) -> Source | None:
        return self.db.get(Source, source_id)

    def get_local_files_source(self, workspace_id: uuid.UUID) -> Source | None:
        statement = select(Source).where(
            Source.workspace_id == workspace_id,
            Source.source_type == SourceType.local_files,
        )
        return self.db.scalar(statement)

    def list_by_workspace(self, workspace_id: uuid.UUID) -> list[Source]:
        statement = (
            select(Source)
            .where(Source.workspace_id == workspace_id)
            .order_by(Source.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def list_retrieval_ready_by_workspace(
        self,
        workspace_id: uuid.UUID,
        *,
        source_types: tuple[SourceType, ...],
    ) -> list[Source]:
        statement = (
            select(Source)
            .where(
                Source.workspace_id == workspace_id,
                Source.status == SourceStatus.ready,
                Source.source_type.in_(source_types),
            )
            .order_by(Source.created_at.asc())
        )
        return list(self.db.scalars(statement).all())

    def update(self, source: Source, **fields: object) -> Source:
        for field, value in fields.items():
            if value is not None:
                setattr(source, field, value)
        self.db.commit()
        self.db.refresh(source)
        return source

    def delete(self, source: Source) -> None:
        self.db.delete(source)
        self.db.commit()

    def exists(self, source_id: uuid.UUID) -> bool:
        statement = select(Source.id).where(Source.id == source_id)
        return self.db.scalar(statement) is not None

    def count_documents(self, source_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(Document).where(Document.source_id == source_id)
        return self.db.scalar(statement) or 0

    def count_chunks(self, source_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Chunk)
            .join(Document, Chunk.document_id == Document.id)
            .where(Document.source_id == source_id)
        )
        return self.db.scalar(statement) or 0
