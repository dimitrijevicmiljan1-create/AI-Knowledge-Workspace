"""Multi-turn conversation memory tests."""

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.base import EmbeddingProvider
from app.ai.chat.provider import ChatProvider
from app.ai.chat.schemas import ChatMessage
from app.core.config import settings
from app.main import app
from app.rag.conversation_memory import ConversationMemoryLoader, HistoryMessage
from app.rag.prompt_builder import PromptBuilder
from app.rag.context_builder import RetrievalContextBuilder
from app.schemas.search import SearchResult

client = TestClient(app)

JWT_KNOWLEDGE = """
JWT authentication is configured using JWT_SECRET_KEY.
Access tokens expire after 30 minutes.
Refresh tokens expire after 7 days.
"""


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 1536) -> None:
        self._dimensions = dimensions
        self._model = settings.openai_embedding_model

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def generate_embedding(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        vectors: list[list[float]] = []
        for text in texts:
            seed = sum(ord(char) for char in text) % 1000
            vector = [0.0] * self._dimensions
            vector[seed % self._dimensions] = 1.0
            vectors.append(vector)
        return vectors


class ContextAwareMockChatProvider(ChatProvider):
    def __init__(self) -> None:
        self.last_messages: list[ChatMessage] | None = None
        self.call_count = 0

    @property
    def model_name(self) -> str:
        return "mock-chat-model"

    def generate_answer(self, messages: list[ChatMessage]) -> str:
        self.last_messages = messages
        self.call_count += 1
        current_question = self._extract_question(messages[-1].content)

        if "refresh token" in current_question:
            return "Refresh tokens expire after 7 days."
        if "how long" in current_question:
            return "Access tokens expire after 30 minutes."
        return "JWT authentication is configured using JWT_SECRET_KEY."

    def _extract_question(self, content: str) -> str:
        for line in content.splitlines():
            if line.startswith("Question:"):
                return line.removeprefix("Question:").strip().lower()
        return content.lower()


@pytest.fixture
def mock_embedding_provider() -> MockEmbeddingProvider:
    return MockEmbeddingProvider()


@pytest.fixture
def mock_chat_provider() -> ContextAwareMockChatProvider:
    return ContextAwareMockChatProvider()


@pytest.fixture
def memory_patch(
    mock_embedding_provider: MockEmbeddingProvider,
    mock_chat_provider: ContextAwareMockChatProvider,
):
    with (
        patch("app.services.embedding_service.get_embedding_provider", return_value=mock_embedding_provider),
        patch("app.services.search_service.get_embedding_provider", return_value=mock_embedding_provider),
        patch("app.rag.rag_service.get_chat_provider", return_value=mock_chat_provider),
    ):
        yield mock_embedding_provider, mock_chat_provider


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"memory-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Memory User"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": user_email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _create_workspace(headers: dict[str, str]) -> str:
    response = client.post(
        "/workspaces",
        headers=headers,
        json={"name": "Memory Workspace", "description": "Workspace for memory tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_manual_source(headers: dict[str, str], workspace_id: str) -> str:
    response = client.post(
        "/sources",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Auth Docs",
            "source_type": "manual",
            "config": {"description": "Authentication documentation"},
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _ingest_and_embed(headers: dict[str, str], source_id: str) -> None:
    ingest_response = client.post(
        "/documents/ingest",
        headers=headers,
        json={
            "source_id": source_id,
            "title": "Auth Guide",
            "path": "docs/auth.md",
            "content": JWT_KNOWLEDGE,
            "metadata": {"format": "markdown"},
        },
    )
    assert ingest_response.status_code == 200
    document_id = ingest_response.json()["document"]["id"]
    embed_response = client.post(f"/documents/{document_id}/embed", headers=headers)
    assert embed_response.status_code == 200


def _create_session(headers: dict[str, str], workspace_id: str) -> str:
    response = client.post(
        "/chat/session",
        headers=headers,
        json={"workspace_id": workspace_id},
    )
    assert response.status_code == 201
    return response.json()["session_id"]


def _send_message(headers: dict[str, str], session_id: str, message: str) -> dict:
    response = client.post(
        f"/chat/session/{session_id}/message",
        headers=headers,
        json={"message": message, "top_k": 5},
    )
    assert response.status_code == 200
    return response.json()


def test_create_chat_session(memory_patch) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    session_id = _create_session(headers, workspace_id)
    assert session_id


def test_session_ownership_protection(memory_patch) -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers)
    session_id = _create_session(owner_headers, workspace_id)

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    forbidden = client.post(
        f"/chat/session/{session_id}/message",
        headers=other_headers,
        json={"message": "How is JWT configured?", "top_k": 5},
    )
    assert forbidden.status_code == 404


def test_conversation_history_trim_by_message_count() -> None:
    loader = ConversationMemoryLoader()
    history = [
        HistoryMessage(role="user", content=f"question {index}")
        for index in range(15)
    ]

    with patch.object(settings, "chat_max_history_messages", 10):
        with patch.object(settings, "chat_max_history_tokens", 100_000):
            trimmed = loader.trim_history(history)

    assert len(trimmed) == 10
    assert trimmed[0].content == "question 5"
    assert trimmed[-1].content == "question 14"


def test_conversation_history_trim_by_token_limit() -> None:
    loader = ConversationMemoryLoader()
    history = [
        HistoryMessage(role="user", content="word " * 100),
        HistoryMessage(role="assistant", content="reply " * 100),
        HistoryMessage(role="user", content="latest question"),
    ]

    with patch.object(settings, "chat_max_history_messages", 10):
        with patch.object(settings, "chat_max_history_tokens", 50):
            trimmed = loader.trim_history(history)

    assert len(trimmed) < len(history)
    assert trimmed[-1].content == "latest question"


def test_retrieval_query_includes_recent_user_messages() -> None:
    loader = ConversationMemoryLoader()
    history = [
        HistoryMessage(role="user", content="How is JWT authentication configured?"),
        HistoryMessage(
            role="assistant",
            content="JWT authentication is configured using JWT_SECRET_KEY.",
        ),
    ]

    query = loader.build_retrieval_query("How long does it last?", history)
    assert "JWT authentication configured" in query or "JWT authentication" in query
    assert "How long does it last?" in query


def test_prompt_includes_conversation_history_before_context() -> None:
    chunk_id = uuid4()
    results = [
        SearchResult(
            chunk_id=chunk_id,
            document_id=uuid4(),
            document_title="Auth Guide",
            document_path="docs/auth.md",
            chunk_content="Access tokens expire after 30 minutes.",
            similarity_score=0.92,
            source_id=uuid4(),
            workspace_id=uuid4(),
        )
    ]
    context = RetrievalContextBuilder().build(results)
    history = [
        HistoryMessage(role="user", content="How is JWT authentication configured?"),
        HistoryMessage(
            role="assistant",
            content="JWT authentication is configured using JWT_SECRET_KEY.",
        ),
    ]

    messages = PromptBuilder().build("How long does it last?", context, history=history)

    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[1]["content"] == history[0].content
    assert messages[2]["role"] == "assistant"
    assert messages[3]["role"] == "user"
    assert "Context:" in messages[3]["content"]
    assert "How long does it last?" in messages[3]["content"]
    assert "30 minutes" in messages[3]["content"]


def test_multi_turn_acceptance_scenario(
    memory_patch: tuple[MockEmbeddingProvider, ContextAwareMockChatProvider],
) -> None:
    _, mock_chat = memory_patch
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    _ingest_and_embed(headers, source_id)
    session_id = _create_session(headers, workspace_id)

    answer_one = _send_message(headers, session_id, "How is JWT authentication configured?")
    assert "JWT_SECRET_KEY" in answer_one["answer"]

    answer_two = _send_message(headers, session_id, "How long does it last?")
    assert "30 minutes" in answer_two["answer"]

    answer_three = _send_message(headers, session_id, "And refresh tokens?")
    assert "7 days" in answer_three["answer"]

    assert mock_chat.call_count == 3
    assert mock_chat.last_messages is not None
    assert len(mock_chat.last_messages) >= 5
    assert mock_chat.last_messages[1].role == "user"
    assert "JWT authentication configured" in mock_chat.last_messages[1].content


def test_messages_persisted_to_database(
    memory_patch: tuple[MockEmbeddingProvider, ContextAwareMockChatProvider],
) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    _ingest_and_embed(headers, source_id)
    session_id = _create_session(headers, workspace_id)

    _send_message(headers, session_id, "How is JWT authentication configured?")
    _send_message(headers, session_id, "How long does it last?")

    third_response = _send_message(headers, session_id, "And refresh tokens?")
    assert third_response["answer"]

    _, mock_chat = memory_patch
    assert mock_chat.last_messages is not None
    user_messages = [message for message in mock_chat.last_messages if message.role == "user"]
    assert len(user_messages) >= 3
