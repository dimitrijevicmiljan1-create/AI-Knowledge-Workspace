from app.rag.retrieval_context import RetrievalContext

SYSTEM_PROMPT = """You are a helpful knowledge workspace assistant.
Answer the user's question using ONLY the provided context.
If the context does not contain enough information, clearly state that you cannot answer from the available sources.
When referencing information, cite sources using [1], [2], etc. matching the numbered context entries.
Do not invent facts or sources beyond the provided context."""


class PromptBuilder:
    """Build LLM prompts without making API calls."""

    def build(self, question: str, context: RetrievalContext) -> list[dict[str, str]]:
        return [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": self._build_user_message(question, context)},
        ]

    def _build_user_message(self, question: str, context: RetrievalContext) -> str:
        if context.is_empty:
            context_block = "No relevant context was retrieved."
        else:
            entries = []
            for index, chunk in enumerate(context.chunks, start=1):
                entries.append(
                    "\n".join(
                        [
                            f"[{index}] Title: {chunk.document_title}",
                            f"Source ID: {chunk.source_id}",
                            f"Document ID: {chunk.document_id}",
                            f"Chunk ID: {chunk.chunk_id}",
                            f"Relevance: {chunk.similarity_score:.4f}",
                            f"Content:\n{chunk.content}",
                        ]
                    )
                )
            context_block = "\n\n".join(entries)

        return "\n\n".join(
            [
                "Context:",
                context_block,
                "",
                f"Question: {question}",
                "",
                "Provide a concise answer with citations like [1], [2] where appropriate.",
            ]
        )
