from app.core.config import settings
from app.rag.retrieval_context import ContextChunk, RetrievalContext
from app.schemas.search import SearchResult


class RetrievalContextBuilder:
    """Convert search results into a filtered retrieval context."""

    def build(self, search_results: list[SearchResult]) -> RetrievalContext:
        chunks: list[ContextChunk] = []
        for result in search_results:
            if result.similarity_score < settings.search_min_similarity:
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
                )
            )
        return RetrievalContext(chunks=chunks)
