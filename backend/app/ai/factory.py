from functools import lru_cache

from app.ai.base import EmbeddingProvider
from app.ai.openai.embeddings import OpenAIEmbeddingProvider
from app.core.config import settings


@lru_cache
def get_embedding_provider() -> EmbeddingProvider:
    """Return the configured embedding provider."""
    return OpenAIEmbeddingProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_embedding_model,
        dimensions=settings.embedding_dimensions,
        max_retries=settings.embedding_max_retries,
        batch_size=settings.embedding_batch_size,
    )
