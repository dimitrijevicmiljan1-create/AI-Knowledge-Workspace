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
        if filters.source_ids is not None and not filters.source_ids:
            return []

        distance_expr = Embedding.vector.cosine_distance(query_vector)
        similarity_expr = (1 - distance_expr).label("similarity_score")

        statement: Select = (
            select(
                Chunk.id.label("chunk_id"),
                Document.id.label("document_id"),
                Document.title.label("document_title"),
                Document.path.label("document_path"),
                Document.document_metadata.label("document_metadata"),
                Chunk.content.label("chunk_content"),
                Source.id.label("source_id"),
                Source.source_type.label("source_type"),
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
                document_path=row.document_path,
                chunk_content=row.chunk_content,
                similarity_score=float(row.similarity_score),
                source_id=row.source_id,
                workspace_id=row.workspace_id,
                source_type=row.source_type.value if row.source_type is not None else None,
                repository_name=self._extract_repository_name(row.document_metadata),
                file_path=self._extract_file_path(row.document_metadata, row.document_path),
                vault_name=self._extract_vault_name(row.document_metadata),
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
        elif filters.source_ids is not None:
            statement = statement.where(Source.id.in_(filters.source_ids))
        if filters.document_id is not None:
            statement = statement.where(Document.id == filters.document_id)
        if filters.date_from is not None:
            statement = statement.where(Chunk.created_at >= filters.date_from)
        if filters.date_to is not None:
            statement = statement.where(Chunk.created_at <= filters.date_to)
        return statement

    def _extract_repository_name(self, metadata: dict | None) -> str | None:
        if not metadata:
            return None
        repository_name = metadata.get("repository_name")
        repository_owner = metadata.get("repository_owner")
        if repository_owner and repository_name:
            return f"{repository_owner}/{repository_name}"
        return repository_name

    def _extract_file_path(self, metadata: dict | None, document_path: str) -> str | None:
        if metadata:
            path = metadata.get("path") or metadata.get("relative_path")
            if path:
                return str(path)
        return document_path

    def _extract_vault_name(self, metadata: dict | None) -> str | None:
        if not metadata:
            return None
        vault_name = metadata.get("vault_name")
        return str(vault_name) if vault_name else None
