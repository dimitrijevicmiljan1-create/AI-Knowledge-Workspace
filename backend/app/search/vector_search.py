from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.models.chunk import Chunk
from app.models.document import Document
from app.models.embedding import Embedding
from app.models.source import Source
from app.search.filters import SearchFilters
from app.search.ranking import SearchHit, rank_hits


@dataclass
class VectorSearchEngine:
    """pgvector-backed semantic search engine."""

    db: Session

    def search(
        self,
        query_vector: list[float],
        *,
        filters: SearchFilters,
        top_k: int,
    ) -> list[SearchHit]:
        distance_expr = Embedding.vector.cosine_distance(query_vector)
        similarity_expr = (1 - distance_expr).label("similarity_score")

        statement: Select = (
            select(
                Chunk.id.label("chunk_id"),
                Document.id.label("document_id"),
                Document.title.label("document_title"),
                Chunk.content.label("chunk_content"),
                Source.id.label("source_id"),
                Source.workspace_id.label("workspace_id"),
                similarity_expr,
            )
            .select_from(Embedding)
            .join(Chunk, Embedding.chunk_id == Chunk.id)
            .join(Document, Chunk.document_id == Document.id)
            .join(Source, Document.source_id == Source.id)
        )

        statement = self._apply_filters(statement, filters)
        statement = statement.order_by(distance_expr.asc()).limit(top_k)

        rows = self.db.execute(statement).all()
        hits = [
            SearchHit(
                chunk_id=row.chunk_id,
                document_id=row.document_id,
                document_title=row.document_title,
                chunk_content=row.chunk_content,
                similarity_score=float(row.similarity_score),
                source_id=row.source_id,
                workspace_id=row.workspace_id,
            )
            for row in rows
        ]
        return rank_hits(hits)

    def similar_to_chunk(
        self,
        chunk_id: UUID,
        *,
        filters: SearchFilters,
        top_k: int,
    ) -> list[SearchHit]:
        embedding = self.db.scalar(select(Embedding).where(Embedding.chunk_id == chunk_id))
        if embedding is None:
            return []

        hits = self.search(
            embedding.vector,
            filters=filters,
            top_k=top_k + 1,
        )
        return [hit for hit in hits if hit.chunk_id != chunk_id][:top_k]

    def _apply_filters(self, statement: Select, filters: SearchFilters) -> Select:
        if filters.workspace_id is not None:
            statement = statement.where(Source.workspace_id == filters.workspace_id)
        if filters.source_id is not None:
            statement = statement.where(Source.id == filters.source_id)
        if filters.document_id is not None:
            statement = statement.where(Document.id == filters.document_id)
        if filters.date_from is not None:
            statement = statement.where(Chunk.created_at >= filters.date_from)
        if filters.date_to is not None:
            statement = statement.where(Chunk.created_at <= filters.date_to)
        return statement
