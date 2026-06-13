from abc import ABC, abstractmethod

from app.ai.chat.schemas import ChatMessage


class ChatProvider(ABC):
    """Abstract chat provider for multi-provider support."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the chat model identifier."""

    @abstractmethod
    def generate_answer(self, messages: list[ChatMessage]) -> str:
        """Generate an answer from chat messages."""
