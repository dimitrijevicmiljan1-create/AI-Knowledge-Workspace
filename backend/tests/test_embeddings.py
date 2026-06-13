"""Embedding pipeline endpoint tests."""

from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.base import EmbeddingProvider
from app.core.config import settings
from app.main import app

client = TestClient(app)


class MockEmbeddingProvider(EmbeddingProvider):
    def __init__(self, dimensions: int = 1536) -> None:
        self._dimensions = dimensions
        self._model = settings.openai_embedding_model
        self.call_count = 0
        self.last_batch_size = 0

    @property
    def model_name(self) -> str:
        return self._model

    @property
    def dimensions(self) -> int:
        return self._dimensions

    def generate_embedding(self, text: str) -> list[float]:
        return self.generate_embeddings([text])[0]

    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        self.call_count += 1
        self.last_batch_size = len(texts)
        return [[0.1] * self._dimensions for _ in texts]


class WrongDimensionProvider(MockEmbeddingProvider):
    def generate_embeddings(self, texts: list[str]) -> list[list[float]]:
        return [[0.1] * 768 for _ in texts]


@pytest.fixture
def mock_provider() -> MockEmbeddingProvider:
    return MockEmbeddingProvider()


@pytest.fixture
def provider_patch(mock_provider: MockEmbeddingProvider):
    with patch("app.services.embedding_service.get_embedding_provider", return_value=mock_provider):
        yield mock_provider


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"embedding-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Embedding User"},
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
        json={"name": "Embedding Workspace", "description": "Workspace for embedding tests"},
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


def _ingest_document(headers: dict[str, str], source_id: str, path: str = "docs/guide.md") -> dict:
    content = "# Guide\n\nEmbedding test content.\n" * 20
    response = client.post(
        "/documents/ingest",
        headers=headers,
        json={
            "source_id": source_id,
            "title": "Guide",
            "path": path,
            "content": content,
            "metadata": {"format": "markdown"},
        },
    )
    assert response.status_code == 200
    return response.json()


def test_single_document_embedding(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(headers, source_id)
    document_id = ingested["document"]["id"]

    embed_response = client.post(f"/documents/{document_id}/embed", headers=headers)
    assert embed_response.status_code == 200
    payload = embed_response.json()
    assert payload["status"] == "completed"
    assert payload["chunks_embedded"] == ingested["chunk_count"]
    assert payload["chunks_skipped"] == 0
    assert payload["embedding_model"] == "text-embedding-3-small"
    assert provider_patch.call_count >= 1


def test_batch_embedding_multiple_documents(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    first = _ingest_document(headers, source_id, path="docs/first.md")
    second = _ingest_document(headers, source_id, path="docs/second.md")

    workspace_response = client.post(f"/workspaces/{workspace_id}/embed", headers=headers)
    assert workspace_response.status_code == 200
    payload = workspace_response.json()
    assert payload["status"] == "completed"
    assert payload["documents_total"] == 2
    assert payload["chunks_embedded"] == first["chunk_count"] + second["chunk_count"]
    assert provider_patch.call_count >= 1


def test_duplicate_embedding_prevention(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(headers, source_id)
    document_id = ingested["document"]["id"]

    first_embed = client.post(f"/documents/{document_id}/embed", headers=headers)
    assert first_embed.status_code == 200
    first_calls = provider_patch.call_count

    second_embed = client.post(f"/documents/{document_id}/embed", headers=headers)
    assert second_embed.status_code == 200
    second_payload = second_embed.json()
    assert second_payload["chunks_embedded"] == 0
    assert second_payload["chunks_skipped"] == ingested["chunk_count"]
    assert provider_patch.call_count == first_calls


def test_reembedding(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(headers, source_id)
    document_id = ingested["document"]["id"]

    client.post(f"/documents/{document_id}/embed", headers=headers)
    provider_patch.call_count = 0

    reembed_response = client.post(f"/documents/{document_id}/reembed", headers=headers)
    assert reembed_response.status_code == 200
    payload = reembed_response.json()
    assert payload["status"] == "completed"
    assert payload["chunks_embedded"] == ingested["chunk_count"]
    assert provider_patch.call_count >= 1


def test_delete_embeddings(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(headers, source_id)
    document_id = ingested["document"]["id"]

    client.post(f"/documents/{document_id}/embed", headers=headers)
    delete_response = client.delete(f"/documents/{document_id}/embeddings", headers=headers)
    assert delete_response.status_code == 200
    assert delete_response.json()["embeddings_deleted"] == ingested["chunk_count"]

    chunks_response = client.get(f"/documents/{document_id}/chunks", headers=headers)
    assert chunks_response.json()["items"][0]["embedding_model"] is None


def test_embedding_preview(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(headers, source_id)
    document_id = ingested["document"]["id"]
    client.post(f"/documents/{document_id}/embed", headers=headers)

    chunks_response = client.get(f"/documents/{document_id}/chunks", headers=headers)
    chunk_id = chunks_response.json()["items"][0]["id"]

    preview_response = client.get(f"/chunks/{chunk_id}/embedding", headers=headers)
    assert preview_response.status_code == 200
    preview = preview_response.json()
    assert preview["chunk_id"] == chunk_id
    assert preview["dimension"] == 1536
    assert "vector" not in preview


def test_embedding_statistics(provider_patch: MockEmbeddingProvider) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)
    ingested = _ingest_document(headers, source_id)
    document_id = ingested["document"]["id"]

    before_stats = client.get("/embeddings/stats", headers=headers)
    assert before_stats.status_code == 200
    before_total = before_stats.json()["total_embeddings"]

    client.post(f"/documents/{document_id}/embed", headers=headers)

    stats_response = client.get("/embeddings/stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_embeddings"] == before_total + ingested["chunk_count"]
    assert stats["total_chunks_embedded"] == before_total + ingested["chunk_count"]
    assert stats["estimated_cost"] >= 0
    assert stats["last_embedding_time"] is not None


def test_dimension_validation_failure() -> None:
    wrong_provider = WrongDimensionProvider()
    with patch("app.services.embedding_service.get_embedding_provider", return_value=wrong_provider):
        tokens = _register_and_login()
        headers = _auth_headers(tokens["access_token"])
        workspace_id = _create_workspace(headers)
        source_id = _create_manual_source(headers, workspace_id)
        ingested = _ingest_document(headers, source_id)
        document_id = ingested["document"]["id"]

        embed_response = client.post(f"/documents/{document_id}/embed", headers=headers)
        assert embed_response.status_code == 422
        assert "1536" in embed_response.json()["detail"]


def test_embedding_ownership_protection(provider_patch: MockEmbeddingProvider) -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers)
    source_id = _create_manual_source(owner_headers, workspace_id)
    ingested = _ingest_document(owner_headers, source_id)
    document_id = ingested["document"]["id"]

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    embed_forbidden = client.post(f"/documents/{document_id}/embed", headers=other_headers)
    assert embed_forbidden.status_code == 403

    workspace_forbidden = client.post(f"/workspaces/{workspace_id}/embed", headers=other_headers)
    assert workspace_forbidden.status_code == 403


def test_embedding_unauthorized_access() -> None:
    document_id = str(uuid4())
    unauthorized_embed = client.post(f"/documents/{document_id}/embed")
    assert unauthorized_embed.status_code == 401

    unauthorized_stats = client.get("/embeddings/stats")
    assert unauthorized_stats.status_code == 401
