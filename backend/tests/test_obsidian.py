"""Obsidian vault integration tests."""

import io
import time
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.base import EmbeddingProvider
from app.ai.chat.provider import ChatProvider
from app.ai.chat.schemas import ChatMessage
from app.core.config import settings
from app.main import app
from app.obsidian.filters import should_index_obsidian_path
from app.obsidian.parser import ObsidianNoteParser
from app.obsidian.sync import ObsidianSyncService, ObsidianVaultFile

client = TestClient(app)

SYNIDOX_NOTE = b"# Synidox\n\nNotes about the Synidox project architecture."


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
    def __init__(self, answer: str = "You wrote about Synidox architecture in your vault.") -> None:
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
    user_email = email or f"obsidian-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Obsidian User"},
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
        json={"name": "Obsidian Workspace", "description": "Workspace for Obsidian tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_should_index_obsidian_path() -> None:
    assert should_index_obsidian_path("notes/synidox.md")
    assert not should_index_obsidian_path(".obsidian/workspace.json")
    assert not should_index_obsidian_path("notes/image.png")
    assert not should_index_obsidian_path(".trash/deleted.md")


def test_obsidian_note_parser_extracts_title() -> None:
    parsed = ObsidianNoteParser().parse(
        path="notes/synidox.md",
        content="# Synidox\n\nProject notes.",
        vault_name="Research",
    )
    assert parsed.title == "Synidox"
    metadata = ObsidianNoteParser().build_document_metadata(
        parsed,
        content_checksum="abc",
        workspace_id=uuid4(),
        vault_id=uuid4(),
    )
    assert metadata["source"] == "obsidian"
    assert metadata["source_type"] == "obsidian"
    assert metadata["vault_name"] == "Research"
    assert metadata["path"] == "notes/synidox.md"
    assert metadata["title"] == "Synidox"
    assert metadata["workspace_id"]
    assert metadata["vault_id"]


def test_create_and_sync_obsidian_vault(rag_patch, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.db.session import SessionLocal

    def run_sync_immediately(
        self,
        job_id,
        vault_id,
        user_id,
        files,
    ) -> None:
        db = SessionLocal()
        try:
            ObsidianSyncService(db).execute_sync(job_id, vault_id, user_id, files)
        finally:
            db.close()

    monkeypatch.setattr(ObsidianSyncService, "_run_sync_job", run_sync_immediately)

    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    create_response = client.post(
        "/obsidian/vaults",
        headers=headers,
        json={"workspace_id": workspace_id, "vault_name": "Research"},
    )
    assert create_response.status_code == 201
    vault_id = create_response.json()["id"]

    sync_response = client.post(
        f"/obsidian/vaults/{vault_id}/sync",
        headers=headers,
        data=[("relative_paths", "Research/notes/synidox.md")],
        files=[
            (
                "files",
                ("synidox.md", io.BytesIO(SYNIDOX_NOTE), "text/markdown"),
            ),
            (
                "files",
                ("config.md", io.BytesIO(b"hidden"), "text/markdown"),
            ),
        ],
    )
    assert sync_response.status_code == 200

    deadline = time.time() + 5
    status_payload = None
    while time.time() < deadline:
        status_response = client.get(f"/obsidian/vaults/{vault_id}/status", headers=headers)
        assert status_response.status_code == 200
        status_payload = status_response.json()
        if status_payload["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)

    assert status_payload is not None
    assert status_payload["status"] == "completed"
    assert status_payload["files_scanned"] == 1
    assert status_payload["documents_created"] == 1

    chat_response = client.post("/chats", headers=headers, json={})
    chat_id = chat_response.json()["id"]
    message_response = client.post(
        f"/chats/{chat_id}/messages",
        headers=headers,
        json={"message": "What did I write about Synidox?"},
    )
    assert message_response.status_code == 200
    payload = message_response.json()
    assert "Synidox" in payload["answer"] or payload["citations"]
    if payload["citations"]:
        assert payload["citations"][0]["source_type"] == "obsidian"


def test_vault_content_query_retrieves_note_text(rag_patch, monkeypatch: pytest.MonkeyPatch) -> None:
    from app.db.session import SessionLocal

    def run_sync_immediately(self, job_id, vault_id, user_id, files) -> None:
        db = SessionLocal()
        try:
            ObsidianSyncService(db).execute_sync(job_id, vault_id, user_id, files)
        finally:
            db.close()

    monkeypatch.setattr(ObsidianSyncService, "_run_sync_job", run_sync_immediately)

    vault_note = b"# Personal Project\n\nMy secret recipe for sourdough bread uses 80% hydration."

    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    create_response = client.post(
        "/obsidian/vaults",
        headers=headers,
        json={"workspace_id": workspace_id, "vault_name": "Personal"},
    )
    vault_id = create_response.json()["id"]

    sync_response = client.post(
        f"/obsidian/vaults/{vault_id}/sync",
        headers=headers,
        data={"relative_paths_json": '["Personal/recipes/sourdough.md"]'},
        files=[
            (
                "files",
                ("sourdough.md", io.BytesIO(vault_note), "text/markdown"),
            ),
        ],
    )
    assert sync_response.status_code == 200

    deadline = time.time() + 5
    while time.time() < deadline:
        status_response = client.get(f"/obsidian/vaults/{vault_id}/status", headers=headers)
        assert status_response.status_code == 200
        if status_response.json()["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)
    assert status_response.json()["status"] == "completed"

    vector_store = client.get(
        f"/obsidian/vector-store?workspace_id={workspace_id}",
        headers=headers,
    )
    assert vector_store.status_code == 200
    vector_payload = vector_store.json()
    assert vector_payload["total_chunks"] > 0
    assert vector_payload["sample_chunks"]
    assert "sourdough" in vector_payload["sample_chunks"][0]["chunk_content"].lower()

    chat_response = client.post("/chats", headers=headers, json={})
    chat_id = chat_response.json()["id"]
    message_response = client.post(
        f"/chats/{chat_id}/messages",
        headers=headers,
        json={"message": "What is inside my Obsidian vault?"},
    )
    assert message_response.status_code == 200
    payload = message_response.json()
    answer = payload["answer"].lower()
    assert "sourdough" in answer or "hydration" in answer or payload["citations"]
    if payload["citations"]:
        assert payload["citations"][0]["source_type"] == "obsidian"


def test_list_and_delete_obsidian_vault(rag_patch) -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    create_response = client.post(
        "/obsidian/vaults",
        headers=headers,
        json={"workspace_id": workspace_id, "vault_name": "Delete Me"},
    )
    vault_id = create_response.json()["id"]

    list_response = client.get(f"/obsidian/vaults?workspace_id={workspace_id}", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    delete_response = client.delete(f"/obsidian/vaults/{vault_id}", headers=headers)
    assert delete_response.status_code == 204

    list_after_delete = client.get(f"/obsidian/vaults?workspace_id={workspace_id}", headers=headers)
    assert list_after_delete.json()["total"] == 0
