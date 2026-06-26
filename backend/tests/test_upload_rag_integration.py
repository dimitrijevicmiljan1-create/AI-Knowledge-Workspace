"""Upload auto-indexing and local document RAG integration tests."""

import io
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.base import EmbeddingProvider
from app.ai.chat.provider import ChatProvider
from app.ai.chat.schemas import ChatMessage
from app.core.config import settings
from app.main import app

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
    def __init__(self, answer: str = "The uploaded document discusses quarterly revenue growth.") -> None:
        self._answer = answer

    @property
    def model_name(self) -> str:
        return "mock-chat-model"

    def generate_answer(self, messages: list[ChatMessage]) -> str:
        return self._answer


@pytest.fixture
def rag_patch():
    mock_embedding = MockEmbeddingProvider()
    mock_chat = MockChatProvider()
    with (
        patch("app.services.embedding_service.get_embedding_provider", return_value=mock_embedding),
        patch("app.services.search_service.get_embedding_provider", return_value=mock_embedding),
        patch("app.rag.rag_service.get_chat_provider", return_value=mock_chat),
    ):
        yield mock_embedding, mock_chat


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"upload-rag-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Upload RAG User"},
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
        json={"name": "Upload RAG Workspace", "description": "Workspace for upload RAG tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _upload_file(
    headers: dict[str, str],
    workspace_id: str,
    filename: str,
    content: bytes,
    mime_type: str = "text/plain",
) -> str:
    response = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": (filename, io.BytesIO(content), mime_type)},
    )
    assert response.status_code == 201
    return response.json()["file"]["document_id"]


def test_upload_auto_indexes_document(rag_patch) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    content = b"# Quarterly Report\n\nRevenue grew 24% year over year in Q4."

    document_id = _upload_file(
        headers,
        workspace_id,
        "report.md",
        content,
        mime_type="text/markdown",
    )

    stats_response = client.get(f"/documents/{document_id}/stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["chunk_count"] > 0
    assert stats["indexed_at"] is not None

    chunks_response = client.get(f"/documents/{document_id}/chunks", headers=headers)
    assert chunks_response.status_code == 200
    assert chunks_response.json()["total"] == stats["chunk_count"]


def test_uploaded_document_available_in_chat(rag_patch) -> None:
    _, mock_chat = rag_patch
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    _upload_file(
        headers,
        workspace_id,
        "summary.txt",
        b"Our upload pipeline stores files, chunks text, and creates embeddings automatically.",
    )

    chat_response = client.post("/chats", headers=headers, json={})
    assert chat_response.status_code == 201
    chat_id = chat_response.json()["id"]

    message_response = client.post(
        f"/chats/{chat_id}/messages",
        headers=headers,
        json={"message": "Summarize the uploaded document about the upload pipeline."},
    )
    assert message_response.status_code == 200
    payload = message_response.json()
    assert payload["answer"] == mock_chat._answer
    assert "could not find relevant information" not in payload["answer"].lower()
    assert len(payload["citations"]) >= 1


def test_upload_auto_index_respects_user_setting(rag_patch) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    settings_response = client.patch(
        "/settings/knowledge",
        headers=headers,
        json={"auto_index_uploads": False},
    )
    assert settings_response.status_code == 200

    document_id = _upload_file(headers, workspace_id, "manual.txt", b"Manual indexing only.")

    stats_response = client.get(f"/documents/{document_id}/stats", headers=headers)
    assert stats_response.status_code == 200
    assert stats_response.json()["chunk_count"] == 0


def test_chat_auto_title_from_first_message(rag_patch) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    _create_workspace(headers)

    chat_response = client.post("/chats", headers=headers, json={})
    chat_id = chat_response.json()["id"]

    client.post(
        f"/chats/{chat_id}/messages",
        headers=headers,
        json={"message": "How does the upload pipeline work?"},
    )

    chat_detail = client.get(f"/chats/{chat_id}", headers=headers)
    assert chat_detail.status_code == 200
    assert chat_detail.json()["title"] == "How does the upload pipeline work?"


def test_delete_chat_removes_from_database(rag_patch) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    _create_workspace(headers)

    chat_response = client.post("/chats", headers=headers, json={"title": "Delete me"})
    chat_id = chat_response.json()["id"]

    delete_response = client.delete(f"/chats/{chat_id}", headers=headers)
    assert delete_response.status_code == 204

    get_response = client.get(f"/chats/{chat_id}", headers=headers)
    assert get_response.status_code == 404

    list_response = client.get("/chats", headers=headers)
    assert all(item["id"] != chat_id for item in list_response.json()["items"])
