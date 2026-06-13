from functools import lru_cache

from app.ai.chat.openai_provider import OpenAIChatProvider
from app.ai.chat.provider import ChatProvider
from app.core.config import settings


@lru_cache
def get_chat_provider() -> ChatProvider:
    """Return the configured chat provider."""
    return OpenAIChatProvider(
        api_key=settings.openai_api_key,
        model=settings.openai_chat_model,
        max_retries=settings.embedding_max_retries,
    )
