class OpenAIClientError(Exception):
    """Base exception for OpenAI client errors."""


class OpenAIRateLimitError(OpenAIClientError):
    """Raised when OpenAI rate limits are exceeded."""


class OpenAITemporaryError(OpenAIClientError):
    """Raised for transient OpenAI API failures."""


class OpenAIEmbeddingError(OpenAIClientError):
    """Raised for non-retryable embedding failures."""


class EmbeddingDimensionError(OpenAIClientError):
    """Raised when embedding dimensions do not match expected size."""

    def __init__(self, expected: int, actual: int) -> None:
        self.expected = expected
        self.actual = actual
        super().__init__(f"Expected {expected} dimensions, got {actual}")
