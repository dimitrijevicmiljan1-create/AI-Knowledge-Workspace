import logging

from app.core.config import settings
from app.rag.retrieval_context import ContextChunk, RetrievalContext
from app.schemas.search import SearchResult

logger = logging.getLogger(__name__)


class RetrievalContextBuilder:
    """Convert search results into a filtered retrieval context."""

    def build(self, search_results: list[SearchResult]) -> RetrievalContext:
        chunks: list[ContextChunk] = []
        for result in search_results:
            if result.similarity_score < settings.search_min_similarity:
                logger.debug(
                    "Filtered chunk below similarity threshold chunk_id=%s score=%.4f threshold=%.2f",
                    result.chunk_id,
                    result.similarity_score,
                    settings.search_min_similarity,
                )
                continue
            chunks.append(
                ContextChunk(
                    chunk_id=result.chunk_id,
                    document_id=result.document_id,
                    source_id=result.source_id,
                    document_title=result.document_title,
                    content=result.chunk_content,
                    similarity_score=result.similarity_score,
                    file_path=result.file_path,
                    repository_name=result.repository_name,
                    vault_name=result.vault_name,
                    source_type=result.source_type,
                )
            )
        logger.info(
            "Context assembly kept=%d filtered_from=%d min_similarity=%.2f source_types=%s paths=%s",
            len(chunks),
            len(search_results),
            settings.search_min_similarity,
            [chunk.source_type for chunk in chunks[:5]],
            [chunk.file_path for chunk in chunks[:5]],
        )
        return RetrievalContext(chunks=chunks)
