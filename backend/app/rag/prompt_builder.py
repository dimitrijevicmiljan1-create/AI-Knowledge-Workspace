from app.rag.conversation_memory import HistoryMessage
from app.rag.retrieval_context import RetrievalContext

SYSTEM_PROMPT = """You are a helpful knowledge workspace assistant.
Answer the user's question using ONLY the provided context.
If the context does not contain enough information, clearly state that you cannot answer from the available sources.
When referencing information, cite sources using [1], [2], etc. matching the numbered context entries.
Do not invent facts or sources beyond the provided context.

When the user asks a follow-up question, use the conversation history to understand what they are referring to.
Retrieved context is always the source of truth — conversation history helps interpret the question but must never override retrieved facts."""

HISTORY_INSTRUCTION = (
    "The conversation history above is for context only. "
    "Always prioritize the retrieved context below when answering."
)


class PromptBuilder:
    """Build LLM prompts without making API calls."""

    def build(
        self,
        question: str,
        context: RetrievalContext,
        history: list[HistoryMessage] | None = None,
    ) -> list[dict[str, str]]:
        messages: list[dict[str, str]] = [{"role": "system", "content": SYSTEM_PROMPT}]

        if history:
            for message in history:
                messages.append({"role": message.role, "content": message.content})

        messages.append(
            {
                "role": "user",
                "content": self._build_user_message(question, context, include_history_note=bool(history)),
            }
        )
        return messages

    def _build_user_message(
        self,
        question: str,
        context: RetrievalContext,
        *,
        include_history_note: bool,
    ) -> str:
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

        parts = []
        if include_history_note:
            parts.extend([HISTORY_INSTRUCTION, ""])

        parts.extend(
            [
                "Context:",
                context_block,
                "",
                f"Question: {question}",
                "",
                "Provide a concise answer with citations like [1], [2] where appropriate.",
            ]
        )
        return "\n\n".join(parts)
