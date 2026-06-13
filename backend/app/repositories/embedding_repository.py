import uuid
from datetime import datetime

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.embedding import Embedding
from app.models.source import Source


class EmbeddingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, chunk_id: uuid.UUID, vector: list[float]) -> Embedding:
        embedding = Embedding(chunk_id=chunk_id, vector=vector)
        self.db.add(embedding)
        self.db.commit()
        self.db.refresh(embedding)
        return embedding

    def create_batch(self, embeddings: list[dict]) -> list[Embedding]:
        created: list[Embedding] = []
        for item in embeddings:
            embedding = Embedding(chunk_id=item["chunk_id"], vector=item["vector"])
            self.db.add(embedding)
            created.append(embedding)
        self.db.commit()
        for embedding in created:
            self.db.refresh(embedding)
        return created

    def get_by_chunk_id(self, chunk_id: uuid.UUID) -> Embedding | None:
        statement = select(Embedding).where(Embedding.chunk_id == chunk_id)
        return self.db.scalar(statement)

    def delete_by_document(self, document_id: uuid.UUID) -> int:
        chunk_ids = select(Chunk.id).where(Chunk.document_id == document_id)
        statement = delete(Embedding).where(Embedding.chunk_id.in_(chunk_ids))
        result = self.db.execute(statement)
        self.db.commit()
        return result.rowcount or 0

    def delete_by_chunk_ids(self, chunk_ids: list[uuid.UUID]) -> int:
        if not chunk_ids:
            return 0
        statement = delete(Embedding).where(Embedding.chunk_id.in_(chunk_ids))
        result = self.db.execute(statement)
        self.db.commit()
        return result.rowcount or 0

    def count_all(self) -> int:
        statement = select(func.count()).select_from(Embedding)
        return self.db.scalar(statement) or 0

    def count_by_document(self, document_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Embedding)
            .join(Chunk, Embedding.chunk_id == Chunk.id)
            .where(Chunk.document_id == document_id)
        )
        return self.db.scalar(statement) or 0

    def get_last_created_at(self) -> datetime | None:
        statement = select(func.max(Embedding.created_at))
        return self.db.scalar(statement)

    def get_total_tokens_embedded(self) -> int:
        statement = (
            select(func.coalesce(func.sum(Chunk.token_count), 0))
            .select_from(Embedding)
            .join(Chunk, Embedding.chunk_id == Chunk.id)
        )
        return int(self.db.scalar(statement) or 0)

    def count_by_workspace(self, workspace_id: uuid.UUID) -> int:
        statement = (
            select(func.count())
            .select_from(Embedding)
            .join(Chunk, Embedding.chunk_id == Chunk.id)
            .join(Document, Chunk.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
            .where(Source.workspace_id == workspace_id)
        )
        return self.db.scalar(statement) or 0

    def get_last_created_at_by_workspace(self, workspace_id: uuid.UUID) -> datetime | None:
        statement = (
            select(func.max(Embedding.created_at))
            .select_from(Embedding)
            .join(Chunk, Embedding.chunk_id == Chunk.id)
            .join(Document, Chunk.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
            .where(Source.workspace_id == workspace_id)
        )
        return self.db.scalar(statement)

    def get_total_tokens_embedded_by_workspace(self, workspace_id: uuid.UUID) -> int:
        statement = (
            select(func.coalesce(func.sum(Chunk.token_count), 0))
            .select_from(Embedding)
            .join(Chunk, Embedding.chunk_id == Chunk.id)
            .join(Document, Chunk.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
            .where(Source.workspace_id == workspace_id)
        )
        return int(self.db.scalar(statement) or 0)
