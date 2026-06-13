from openai import APIConnectionError, APITimeoutError, OpenAI, RateLimitError

from app.ai.openai.exceptions import (
    OpenAIEmbeddingError,
    OpenAIRateLimitError,
    OpenAITemporaryError,
)


class OpenAIClient:
    """Low-level OpenAI API client wrapper."""

    def __init__(self, *, api_key: str) -> None:
        self._client = OpenAI(api_key=api_key)

    @property
    def client(self) -> OpenAI:
        return self._client

    def map_error(self, error: Exception) -> Exception:
        if isinstance(error, RateLimitError):
            return OpenAIRateLimitError(str(error))
        if isinstance(error, (APIConnectionError, APITimeoutError)):
            return OpenAITemporaryError(str(error))
        return OpenAIEmbeddingError(str(error))
