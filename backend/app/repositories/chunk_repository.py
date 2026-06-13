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
