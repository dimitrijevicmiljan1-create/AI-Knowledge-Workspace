"""Vector search endpoint tests."""

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.base import EmbeddingProvider
from app.core.config import settings
from app.main import app
from app.search.ranking import SearchHit, rank_hits

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


@pytest.fixture
def mock_provider() -> MockEmbeddingProvider:
    return MockEmbeddingProvider()


@pytest.fixture
def provider_patch(mock_provider: MockEmbeddingProvider):
    with (
        patch("app.services.embedding_service.get_embedding_provider", return_value=mock_provider),
        patch("app.services.search_service.get_embedding_provider", return_value=mock_provider),
    ):
        yield mock_provider


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"search-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Search User"},
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
        json={"name": "Search Workspace", "description": "Workspace for search tests"},
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


def _ingest_document(
    headers: dict[str, str],
    source_id: str,
    *,
    path: str,
    content: str,
    title: str,
) -> dict:
    response = client.post(
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
    assert response.status_code == 200
    return response.json()


def _embed_document(headers: dict[str, str], document_id: str) -> None:
    response = client.post(f"/documents/{document_id}/embed", headers=headers)
    assert response.status_code == 200


def test_workspace_search(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(
        headers,
        source_id,
        path="docs/auth.md",
        title="Auth Guide",
        content="Configure JWT authentication and workspace ownership checks.",
    )
    _embed_document(headers, ingested["document"]["id"])

    search_response = client.post(
        f"/search/workspace/{workspace_id}",
        headers=headers,
        json={"query": "JWT authentication", "top_k": 5},
    )
    assert search_response.status_code == 200
    payload = search_response.json()
    assert payload["query"] == "JWT authentication"
    assert payload["top_k"] == 5
    assert payload["total_results"] >= 1
    assert payload["search_id"] is not None
    result = payload["results"][0]
    assert result["document_title"] == "Auth Guide"
    assert result["workspace_id"] == workspace_id
    assert "similarity_score" in result


def test_document_search(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    first = _ingest_document(
        headers,
        source_id,
        path="docs/first.md",
        title="First",
        content="Alpha content about databases.",
    )
    second = _ingest_document(
        headers,
        source_id,
        path="docs/second.md",
        title="Second",
        content="Beta content about authentication tokens.",
    )
    _embed_document(headers, first["document"]["id"])
    _embed_document(headers, second["document"]["id"])

    search_response = client.post(
        f"/search/document/{first['document']['id']}",
        headers=headers,
        json={"query": "authentication tokens", "top_k": 5},
    )
    assert search_response.status_code == 200
    payload = search_response.json()
    assert payload["total_results"] >= 1
    assert all(item["document_id"] == first["document"]["id"] for item in payload["results"])


def test_source_search(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(
        headers,
        source_id,
        path="docs/source.md",
        title="Source Doc",
        content="Semantic retrieval with pgvector cosine similarity.",
    )
    _embed_document(headers, ingested["document"]["id"])

    search_response = client.post(
        f"/search/source/{source_id}",
        headers=headers,
        json={"query": "pgvector cosine", "top_k": 3},
    )
    assert search_response.status_code == 200
    payload = search_response.json()
    assert payload["total_results"] >= 1
    assert all(item["source_id"] == source_id for item in payload["results"])


def test_ranking_engine() -> None:
    hits = [
        SearchHit(
            chunk_id=uuid4(),
            document_id=uuid4(),
            document_title="A",
            document_path="docs/a.md",
            chunk_content="a",
            similarity_score=0.2,
            source_id=uuid4(),
            workspace_id=uuid4(),
        ),
        SearchHit(
            chunk_id=uuid4(),
            document_id=uuid4(),
            document_title="B",
            document_path="docs/b.md",
            chunk_content="b",
            similarity_score=0.9,
            source_id=uuid4(),
            workspace_id=uuid4(),
        ),
        SearchHit(
            chunk_id=uuid4(),
            document_id=uuid4(),
            document_title="C",
            document_path="docs/c.md",
            chunk_content="c",
            similarity_score=0.5,
            source_id=uuid4(),
            workspace_id=uuid4(),
        ),
    ]

    ranked = rank_hits(hits, normalize=False)
    assert ranked[0].similarity_score == 0.9
    assert ranked[-1].similarity_score == 0.2

    normalized = rank_hits(hits)
    assert normalized[0].similarity_score == 1.0
    assert normalized[-1].similarity_score == 0.0


def test_search_history_and_statistics(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(
        headers,
        source_id,
        path="docs/history.md",
        title="History Doc",
        content="Track search history and analytics.",
    )
    _embed_document(headers, ingested["document"]["id"])

    stats_before = client.get("/search/stats", headers=headers)
    assert stats_before.status_code == 200
    before_total = stats_before.json()["total_searches"]

    search_response = client.post(
        f"/search/workspace/{workspace_id}",
        headers=headers,
        json={"query": "search history", "top_k": 5},
    )
    assert search_response.status_code == 200

    stats_after = client.get("/search/stats", headers=headers)
    assert stats_after.status_code == 200
    stats = stats_after.json()
    assert stats["total_searches"] == before_total + 1
    assert stats["avg_results"] >= 0
    assert stats["most_active_workspace"] == workspace_id
    assert stats["recent_queries_count"] >= 1


def test_search_ownership_protection(provider_patch: MockEmbeddingProvider) -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers)
    source_id = _create_manual_source(owner_headers, workspace_id)
    ingested = _ingest_document(
        owner_headers,
        source_id,
        path="docs/private.md",
        title="Private",
        content="Private knowledge base content.",
    )
    _embed_document(owner_headers, ingested["document"]["id"])

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    workspace_forbidden = client.post(
        f"/search/workspace/{workspace_id}",
        headers=other_headers,
        json={"query": "private", "top_k": 5},
    )
    assert workspace_forbidden.status_code == 403

    document_forbidden = client.post(
        f"/search/document/{ingested['document']['id']}",
        headers=other_headers,
        json={"query": "private", "top_k": 5},
    )
    assert document_forbidden.status_code == 403

    source_forbidden = client.post(
        f"/search/source/{source_id}",
        headers=other_headers,
        json={"query": "private", "top_k": 5},
    )
    assert source_forbidden.status_code == 403


def test_search_unauthorized_access() -> None:
    workspace_id = str(uuid4())
    unauthorized_search = client.post(
        f"/search/workspace/{workspace_id}",
        json={"query": "test", "top_k": 5},
    )
    assert unauthorized_search.status_code == 401

    unauthorized_stats = client.get("/search/stats")
    assert unauthorized_stats.status_code == 401
