"""Retrieval source resolution tests."""

import io
import time
from unittest.mock import patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.ai.base import EmbeddingProvider
from app.core.config import settings
from app.main import app
from app.models.source import SourceType
from app.services.retrieval_source_service import RETRIEVAL_SOURCE_TYPES, RetrievalSourceService

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
def provider_patch():
    mock_provider = MockEmbeddingProvider()
    with (
        patch("app.services.embedding_service.get_embedding_provider", return_value=mock_provider),
        patch("app.services.search_service.get_embedding_provider", return_value=mock_provider),
    ):
        yield mock_provider


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"retrieval-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Retrieval User"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": user_email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _get_workspace(headers: dict[str, str]) -> str:
    response = client.get("/workspaces/me", headers=headers)
    assert response.status_code == 200
    return response.json()["id"]


def test_retrieval_source_types_include_obsidian() -> None:
    assert SourceType.obsidian in RETRIEVAL_SOURCE_TYPES
    assert SourceType.github in RETRIEVAL_SOURCE_TYPES
    assert SourceType.local_files in RETRIEVAL_SOURCE_TYPES


def test_obsidian_source_included_in_workspace_retrieval(provider_patch, monkeypatch) -> None:
    from app.db.session import SessionLocal
    from app.obsidian.sync import ObsidianSyncService

    def run_sync_immediately(self, job_id, vault_id, user_id, files) -> None:
        db = SessionLocal()
        try:
            ObsidianSyncService(db).execute_sync(job_id, vault_id, user_id, files)
        finally:
            db.close()

    monkeypatch.setattr(ObsidianSyncService, "_run_sync_job", run_sync_immediately)

    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _get_workspace(headers)

    create_response = client.post(
        "/obsidian/vaults",
        headers=headers,
        json={"workspace_id": workspace_id, "vault_name": "Retrieval Vault"},
    )
    vault_id = create_response.json()["id"]

    sync_response = client.post(
        f"/obsidian/vaults/{vault_id}/sync",
        headers=headers,
        files=[
            (
                "files",
                ("Retrieval Vault/secret-note.md", io.BytesIO(b"# Secret\n\nOnly in Obsidian."), "text/markdown"),
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

    db = SessionLocal()
    try:
        source_ids = RetrievalSourceService(db).list_retrieval_source_ids(workspace_id)
        assert source_ids, "Expected at least one retrieval-ready source"
    finally:
        db.close()

    search_response = client.post(
        f"/search/workspace/{workspace_id}",
        headers=headers,
        json={"query": "Secret Obsidian note", "top_k": 5},
    )
    assert search_response.status_code == 200
    results = search_response.json()["results"]
    assert results
    assert any(result["source_type"] == "obsidian" for result in results)
