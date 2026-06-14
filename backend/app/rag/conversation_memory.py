from dataclasses import dataclass

from app.chunking.tokenizer import estimate_token_count
from app.core.config import settings
from app.models.chat_message import MessageRole


@dataclass(frozen=True)
class HistoryMessage:
    role: str
    content: str


class ConversationMemoryLoader:
    """Load and trim persisted conversation history for prompt injection."""

    def trim_history(self, messages: list[HistoryMessage]) -> list[HistoryMessage]:
        if not messages:
            return []

        max_messages = settings.chat_max_history_messages
        trimmed = messages[-max_messages:] if max_messages > 0 else []

        max_tokens = settings.chat_max_history_tokens
        if max_tokens <= 0:
            return trimmed

        while trimmed and self._estimate_tokens(trimmed) > max_tokens:
            trimmed = trimmed[1:]

        return trimmed

    def build_retrieval_query(
        self,
        current_message: str,
        history: list[HistoryMessage],
    ) -> str:
        """Enrich follow-up queries with recent user turns for better RAG retrieval."""
        recent_user_messages = [
            message.content for message in history if message.role == MessageRole.user.value
        ]
        if not recent_user_messages:
            return current_message

        context_window = recent_user_messages[-2:]
        return " ".join([*context_window, current_message])

    def _estimate_tokens(self, messages: list[HistoryMessage]) -> int:
        return sum(estimate_token_count(message.content) for message in messages)
