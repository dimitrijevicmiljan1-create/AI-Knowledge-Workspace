"""Chunking engine endpoint tests."""

import io
from uuid import uuid4

from fastapi.testclient import TestClient

from app.chunking.extractors import extract_text_from_file
from app.chunking.manager import ChunkingManager
from app.chunking.base import ChunkConfig, ChunkStrategyName
from app.main import app

client = TestClient(app)


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"chunk-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Chunk User"},
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
        json={"name": "Chunk Workspace", "description": "Workspace for chunk tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _upload_text_file(headers: dict[str, str], workspace_id: str, filename: str, content: bytes) -> str:
    response = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": (filename, io.BytesIO(content), "text/plain")},
    )
    assert response.status_code == 201
    return response.json()["file"]["document_id"]


def test_text_extraction_and_chunk_creation() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    content = b"Paragraph one.\n\nParagraph two.\n\nParagraph three."
    document_id = _upload_text_file(headers, workspace_id, "notes.txt", content)

    chunk_response = client.post(f"/documents/{document_id}/chunk", headers=headers, json={})
    assert chunk_response.status_code == 201
    payload = chunk_response.json()
    assert payload["chunk_count"] >= 1
    assert payload["strategy"] == "recursive"
    assert payload["total_tokens"] > 0

    list_response = client.get(f"/documents/{document_id}/chunks", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == payload["chunk_count"]


def test_chunk_overlap_and_rechunk() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    content = ("word " * 300).encode()
    document_id = _upload_text_file(headers, workspace_id, "long.txt", content)

    first_chunk = client.post(
        f"/documents/{document_id}/chunk",
        headers=headers,
        json={"strategy": "fixed", "chunk_size": 200, "chunk_overlap": 50},
    )
    assert first_chunk.status_code == 201
    first_count = first_chunk.json()["chunk_count"]
    assert first_count > 1

    chunks = client.get(f"/documents/{document_id}/chunks", headers=headers).json()["items"]
    assert chunks[0]["content"][-20:] in chunks[1]["content"]

    rechunk_response = client.post(
        f"/documents/{document_id}/rechunk",
        headers=headers,
        json={"strategy": "paragraph"},
    )
    assert rechunk_response.status_code == 200
    assert rechunk_response.json()["strategy"] == "paragraph"


def test_chunk_statistics_preview_and_deletion() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    document_id = _upload_text_file(headers, workspace_id, "stats.md", b"# Title\n\nBody content.")
    client.post(f"/documents/{document_id}/chunk", headers=headers, json={})

    stats_response = client.get(f"/documents/{document_id}/chunk-stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["total_chunks"] >= 1
    assert stats["total_tokens"] >= 1
    assert stats["avg_chunk_size"] > 0

    chunks = client.get(f"/documents/{document_id}/chunks", headers=headers).json()["items"]
    preview = client.get(f"/chunks/{chunks[0]['id']}", headers=headers)
    assert preview.status_code == 200
    assert preview.json()["content"]
    assert preview.json()["chunk_index"] == 0

    delete_response = client.delete(f"/documents/{document_id}/chunks", headers=headers)
    assert delete_response.status_code == 204
    assert client.get(f"/documents/{document_id}/chunks", headers=headers).json()["total"] == 0


def test_chunk_conflict_without_rechunk() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    document_id = _upload_text_file(headers, workspace_id, "dup-chunk.txt", b"chunk once")
    client.post(f"/documents/{document_id}/chunk", headers=headers, json={})

    second_chunk = client.post(f"/documents/{document_id}/chunk", headers=headers, json={})
    assert second_chunk.status_code == 409


def test_chunking_unit_helpers(tmp_path) -> None:
    sample = tmp_path / "sample.md"
    sample.write_text("# Heading\n\nSample markdown body.", encoding="utf-8")
    extracted = extract_text_from_file(str(sample), ".md")
    assert "Heading" in extracted

    manager = ChunkingManager()
    chunks = manager.chunk(
        "alpha\n\nbeta\n\ngamma",
        ChunkConfig(chunk_size=20, chunk_overlap=5, strategy=ChunkStrategyName.recursive),
    )
    assert chunks
