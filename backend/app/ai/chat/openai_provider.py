import time

from openai import OpenAIError

from app.ai.chat.provider import ChatProvider
from app.ai.chat.schemas import ChatMessage
from app.ai.openai.client import OpenAIClient
from app.ai.openai.exceptions import OpenAIEmbeddingError, OpenAIRateLimitError, OpenAITemporaryError
from app.core.config import settings


class OpenAIChatProvider(ChatProvider):
    """OpenAI chat completion provider."""

    RETRYABLE_ERRORS = (OpenAIRateLimitError, OpenAITemporaryError)

    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        max_retries: int = 3,
    ) -> None:
        self._client = OpenAIClient(api_key=api_key)
        self._model = model
        self._max_retries = max_retries

    @property
    def model_name(self) -> str:
        return self._model

    def generate_answer(self, messages: list[ChatMessage]) -> str:
        payload = [message.model_dump() for message in messages]
        last_error: Exception | None = None

        for attempt in range(self._max_retries):
            try:
                response = self._client.client.chat.completions.create(
                    model=self._model,
                    messages=payload,
                )
                content = response.choices[0].message.content
                if content is None:
                    raise OpenAIEmbeddingError("Chat completion returned empty content")
                return content
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
        raise OpenAIEmbeddingError("Chat completion failed without a specific error")
