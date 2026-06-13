from abc import ABC, abstractmethod


class EmbeddingProvider(ABC):
    """Abstract embedding provider for multi-provider support."""

    @property
    @abstractmethod
    def model_name(self) -> str:
        """Return the embedding model identifier."""

    @property
    @abstractmethod
    def dimensions(self) -> int:
        """Return the expected embedding vector dimensions."""

    @abstractmethod
    def generate_embedding(self, text: str) -> list[float]:
        """Generate a single embedding vector."""

    @abstractmethod
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple texts in batch."""
