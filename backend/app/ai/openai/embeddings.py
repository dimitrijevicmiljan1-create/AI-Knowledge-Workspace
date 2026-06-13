import time

from openai import OpenAIError

from app.ai.base import EmbeddingProvider
from app.ai.openai.client import OpenAIClient
from app.ai.openai.exceptions import (
    EmbeddingDimensionError,
    OpenAIEmbeddingError,
    OpenAIRateLimitError,
    OpenAITemporaryError,
)


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """OpenAI embedding provider using text-embedding-3-small."""

    RETRYABLE_ERRORS = (OpenAIRateLimitError, OpenAITemporaryError)

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        dimensions: int,
        max_retries: int = 3,
        batch_size: int = 100,
    ) -> None:
        self._client = OpenAIClient(api_key=api_key)
        self._model = model
        self._dimensions = dimensions
        self._max_retries = max_retries
        self._batch_size = batch_size

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def generate_embedding(self, text: str) -> list[float]:
        vectors = self.generate_embeddings([text])
        return vectors[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []

        all_vectors: list[list[float]] = []
        for batch_start in range(0, len(texts), self._batch_size):
            batch = texts[batch_start : batch_start + self._batch_size]
            batch_vectors = self._embed_batch_with_retry(batch)
            all_vectors.extend(batch_vectors)
        return all_vectors

    def _embed_batch_with_retry(self, texts: list[str]) -> list[list[float]]:
        last_error: Exception | None = None
        for attempt in range(self._max_retries):
            try:
                response = self._client.client.embeddings.create(
                    input=texts,
                    model=self._model,
                    dimensions=self._dimensions,
                )
                sorted_data = sorted(response.data, key=lambda item: item.index)
                vectors = [item.embedding for item in sorted_data]
                self._validate_dimensions(vectors)
                return vectors
            except self.RETRYABLE_ERRORS as error:
                last_error = error
                if attempt < self._max_retries - 1:
                    time.sleep(2**attempt)
                    continue
                raise
            except OpenAIError as error:
                raise self._client.map_error(error) from error

        if last_error is not None:
            raise last_error
        raise OpenAIEmbeddingError("Embedding request failed without a specific error")

    def _validate_dimensions(self, vectors: list[list[float]]) -> None:
        for vector in vectors:
            if len(vector) != self._dimensions:
                raise EmbeddingDimensionError(self._dimensions, len(vector))
