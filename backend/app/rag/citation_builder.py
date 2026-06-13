from app.rag.retrieval_context import RetrievalContext
from app.schemas.chat import Citation


class CitationBuilder:
    """Build source citations from retrieval context."""

    def build(self, context: RetrievalContext) -> list[Citation]:
        return [
            Citation(
                chunk_id=chunk.chunk_id,
                document_id=chunk.document_id,
                source_id=chunk.source_id,
                document_title=chunk.document_title,
            )
            for chunk in context.chunks
        ]
