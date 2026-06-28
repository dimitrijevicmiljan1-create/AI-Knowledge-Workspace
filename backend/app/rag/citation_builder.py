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
                file_path=chunk.file_path,
                repository_name=chunk.repository_name,
                vault_name=chunk.vault_name,
                source_type=chunk.source_type,
            )
            for chunk in context.chunks
        ]
