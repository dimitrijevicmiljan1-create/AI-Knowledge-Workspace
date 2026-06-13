"""RAG answer generation tests."""

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.base import EmbeddingProvider
from app.ai.chat.provider import ChatProvider
from app.ai.chat.schemas import ChatMessage
from app.core.config import settings
from app.main import app
from app.rag.citation_builder import CitationBuilder
from app.rag.context_builder import RetrievalContextBuilder
from app.rag.prompt_builder import PromptBuilder
from app.schemas.search import SearchResult

client = TestClient(app)


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


class MockChatProvider(ChatProvider):
    def __init__(self, answer: str = "JWT is configured using JWT_SECRET_KEY [1].") -> None:
        self._answer = answer
        self.last_messages: list[ChatMessage] | None = None

    @property
    def model_name(self) -> str:
        return "mock-chat-model"

    def generate_answer(self, messages: list[ChatMessage]) -> str:
        self.last_messages = messages
        return self._answer


@pytest.fixture
def mock_embedding_provider() -> MockEmbeddingProvider:
    return MockEmbeddingProvider()


@pytest.fixture
def mock_chat_provider() -> MockChatProvider:
    return MockChatProvider()


@pytest.fixture
def rag_patch(mock_embedding_provider: MockEmbeddingProvider, mock_chat_provider: MockChatProvider):
    with (
        patch("app.services.embedding_service.get_embedding_provider", return_value=mock_embedding_provider),
        patch("app.services.search_service.get_embedding_provider", return_value=mock_embedding_provider),
        patch("app.rag.rag_service.get_chat_provider", return_value=mock_chat_provider),
    ):
        yield mock_embedding_provider, mock_chat_provider


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"rag-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "RAG User"},
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
        json={"name": "RAG Workspace", "description": "Workspace for RAG tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_manual_source(headers: dict[str, str], workspace_id: str) -> str:
    response = client.post(
        "/sources",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Manual Source",
            "source_type": "manual",
            "config": {"description": "Test manual source"},
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _ingest_and_embed(
    headers: dict[str, str],
    source_id: str,
    *,
    path: str,
    title: str,
    content: str,
) -> str:
    ingest_response = client.post(
        "/documents/ingest",
        headers=headers,
        json={
            "source_id": source_id,
            "title": title,
            "path": path,
            "content": content,
            "metadata": {"format": "markdown"},
        },
    )
    assert ingest_response.status_code == 200
    document_id = ingest_response.json()["document"]["id"]
    embed_response = client.post(f"/documents/{document_id}/embed", headers=headers)
    assert embed_response.status_code == 200
    return document_id


def test_retrieval_context_creation() -> None:
    chunk_id = uuid4()
    document_id = uuid4()
    source_id = uuid4()
    workspace_id = uuid4()
    results = [
        SearchResult(
            chunk_id=chunk_id,
            document_id=document_id,
            document_title="Auth Guide",
            chunk_content="Configure JWT authentication.",
            similarity_score=0.91,
            source_id=source_id,
            workspace_id=workspace_id,
        )
    ]

    context = RetrievalContextBuilder().build(results)
    assert len(context.chunks) == 1
    chunk = context.chunks[0]
    assert chunk.chunk_id == chunk_id
    assert chunk.document_title == "Auth Guide"
    assert chunk.similarity_score == 0.91


def test_similarity_filtering() -> None:
    results = [
        SearchResult(
            chunk_id=uuid4(),
            document_id=uuid4(),
            document_title="Low",
            chunk_content="low relevance",
            similarity_score=0.55,
            source_id=uuid4(),
            workspace_id=uuid4(),
        ),
        SearchResult(
            chunk_id=uuid4(),
            document_id=uuid4(),
            document_title="High",
            chunk_content="high relevance",
            similarity_score=0.85,
            source_id=uuid4(),
            workspace_id=uuid4(),
        ),
    ]

    context = RetrievalContextBuilder().build(results)
    assert len(context.chunks) == 1
    assert context.chunks[0].document_title == "High"


def test_prompt_building() -> None:
    chunk_id = uuid4()
    document_id = uuid4()
    source_id = uuid4()
    results = [
        SearchResult(
            chunk_id=chunk_id,
            document_id=document_id,
            document_title="Auth Guide",
            chunk_content="Use JWT_SECRET_KEY for signing tokens.",
            similarity_score=0.92,
            source_id=source_id,
            workspace_id=uuid4(),
        )
    ]
    context = RetrievalContextBuilder().build(results)
    messages = PromptBuilder().build("How is JWT configured?", context)

    assert messages[0]["role"] == "system"
    assert "JWT_SECRET_KEY" in messages[1]["content"]
    assert "How is JWT configured?" in messages[1]["content"]
    assert str(chunk_id) in messages[1]["content"]


def test_citation_generation() -> None:
    chunk_id = uuid4()
    document_id = uuid4()
    source_id = uuid4()
    results = [
        SearchResult(
            chunk_id=chunk_id,
            document_id=document_id,
            document_title="Auth Guide",
            chunk_content="JWT content",
            similarity_score=0.88,
            source_id=source_id,
            workspace_id=uuid4(),
        )
    ]
    context = RetrievalContextBuilder().build(results)
    citations = CitationBuilder().build(context)

    assert len(citations) == 1
    assert citations[0].chunk_id == chunk_id
    assert citations[0].document_id == document_id
    assert citations[0].source_id == source_id
    assert citations[0].document_title == "Auth Guide"


def test_workspace_chat_endpoint(rag_patch: tuple[MockEmbeddingProvider, MockChatProvider]) -> None:
    _, mock_chat = rag_patch
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    _ingest_and_embed(
        headers,
        source_id,
        path="docs/auth.md",
        title="Auth Guide",
        content="Configure JWT authentication using JWT_SECRET_KEY.",
    )

    response = client.post(
        f"/chat/workspace/{workspace_id}",
        headers=headers,
        json={"question": "How is JWT configured?", "top_k": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["answer"] == mock_chat._answer
    assert payload["processing_time"] >= 0
    assert payload["exchange_id"] is not None
    assert len(payload["citations"]) >= 1
    assert len(payload["retrieved_chunks"]) >= 1
    assert mock_chat.last_messages is not None


def test_document_chat_endpoint(rag_patch: tuple[MockEmbeddingProvider, MockChatProvider]) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    document_id = _ingest_and_embed(
        headers,
        source_id,
        path="docs/doc-chat.md",
        title="Doc Chat",
        content="Document-scoped JWT configuration details.",
    )

    response = client.post(
        f"/chat/document/{document_id}",
        headers=headers,
        json={"question": "JWT configuration", "top_k": 3},
    )
    assert response.status_code == 200
    assert response.json()["answer"]
    assert response.json()["exchange_id"] is not None


def test_source_chat_endpoint(rag_patch: tuple[MockEmbeddingProvider, MockChatProvider]) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    _ingest_and_embed(
        headers,
        source_id,
        path="docs/source-chat.md",
        title="Source Chat",
        content="Source-scoped authentication guidance.",
    )

    response = client.post(
        f"/chat/source/{source_id}",
        headers=headers,
        json={"question": "authentication guidance", "top_k": 3},
    )
    assert response.status_code == 200
    assert response.json()["answer"]
    assert response.json()["exchange_id"] is not None


def test_chat_ownership_protection(rag_patch: tuple[MockEmbeddingProvider, MockChatProvider]) -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers)
    source_id = _create_manual_source(owner_headers, workspace_id)
    document_id = _ingest_and_embed(
        owner_headers,
        source_id,
        path="docs/private.md",
        title="Private",
        content="Private JWT configuration notes.",
    )

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    workspace_forbidden = client.post(
        f"/chat/workspace/{workspace_id}",
        headers=other_headers,
        json={"question": "JWT", "top_k": 5},
    )
    assert workspace_forbidden.status_code == 403

    source_forbidden = client.post(
        f"/chat/source/{source_id}",
        headers=other_headers,
        json={"question": "JWT", "top_k": 5},
    )
    assert source_forbidden.status_code == 403

    document_forbidden = client.post(
        f"/chat/document/{document_id}",
        headers=other_headers,
        json={"question": "JWT", "top_k": 5},
    )
    assert document_forbidden.status_code == 403


def test_chat_unauthorized_access() -> None:
    workspace_id = str(uuid4())
    unauthorized = client.post(
        f"/chat/workspace/{workspace_id}",
        json={"question": "test", "top_k": 5},
    )
    assert unauthorized.status_code == 401


def test_end_to_end_answer_without_relevant_context(
    rag_patch: tuple[MockEmbeddingProvider, MockChatProvider],
) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    response = client.post(
        f"/chat/workspace/{workspace_id}",
        headers=headers,
        json={"question": "Unknown topic with no indexed content", "top_k": 5},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "could not find relevant information" in payload["answer"].lower()
    assert payload["citations"] == []
    assert payload["retrieved_chunks"] == []
    assert payload["exchange_id"] is not None
