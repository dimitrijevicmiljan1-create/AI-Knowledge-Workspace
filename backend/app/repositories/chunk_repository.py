import uuid

from sqlalchemy import delete, func, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk


class ChunkRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create_batch(
        self,
        *,
        document_id: uuid.UUID,
        chunks: list[dict],
    ) -> list[Chunk]:
        created_chunks: list[Chunk] = []
        for chunk_data in chunks:
            chunk = Chunk(
                document_id=document_id,
                chunk_index=chunk_data["chunk_index"],
                content=chunk_data["content"],
                token_count=chunk_data.get("token_count"),
                embedding_model=chunk_data.get("embedding_model"),
            )
            self.db.add(chunk)
            created_chunks.append(chunk)
        self.db.commit()
        for chunk in created_chunks:
            self.db.refresh(chunk)
        return created_chunks

    def delete_by_document(self, document_id: uuid.UUID) -> None:
        statement = delete(Chunk).where(Chunk.document_id == document_id)
        self.db.execute(statement)
        self.db.commit()

    def list_by_document(self, document_id: uuid.UUID) -> list[Chunk]:
        statement = (
            select(Chunk)
            .where(Chunk.document_id == document_id)
            .order_by(Chunk.chunk_index.asc())
        )
        return list(self.db.scalars(statement).all())

    def count_by_document(self, document_id: uuid.UUID) -> int:
        statement = select(func.count()).select_from(Chunk).where(Chunk.document_id == document_id)
        return self.db.scalar(statement) or 0

    def get_by_id(self, chunk_id: uuid.UUID) -> Chunk | None:
        return self.db.get(Chunk, chunk_id)

    def list_unembedded_by_document(
        self,
        document_id: uuid.UUID,
        *,
        embedding_model: str | None = None,
    ) -> list[Chunk]:
        from app.models.embedding import Embedding

        statement = (
            select(Chunk)
            .outerjoin(Embedding, Chunk.id == Embedding.chunk_id)
            .where(Chunk.document_id == document_id, Embedding.id.is_(None))
            .order_by(Chunk.chunk_index.asc())
        )
        if embedding_model is not None:
            statement = statement.where(
                (Chunk.embedding_model.is_(None)) | (Chunk.embedding_model != embedding_model)
            )
        return list(self.db.scalars(statement).all())

    def list_by_document_ids(self, document_ids: list[uuid.UUID]) -> list[Chunk]:
        if not document_ids:
            return []
        statement = (
            select(Chunk)
            .where(Chunk.document_id.in_(document_ids))
            .order_by(Chunk.document_id.asc(), Chunk.chunk_index.asc())
        )
        return list(self.db.scalars(statement).all())

    def update_embedding_model(self, chunk: Chunk, embedding_model: str) -> Chunk:
        chunk.embedding_model = embedding_model
        self.db.commit()
        self.db.refresh(chunk)
        return chunk

    def update_embedding_models(self, chunk_ids: list[uuid.UUID], embedding_model: str) -> None:
        if not chunk_ids:
            return
        statement = select(Chunk).where(Chunk.id.in_(chunk_ids))
        chunks = self.db.scalars(statement).all()
        for chunk in chunks:
            chunk.embedding_model = embedding_model
        self.db.commit()
