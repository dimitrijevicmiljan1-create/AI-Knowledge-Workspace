"""Document ingestion endpoint tests."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"document-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Document User"},
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
        json={"name": "Document Workspace", "description": "Workspace for document tests"},
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


def test_document_ingestion_flow() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    source_id = _create_manual_source(headers, workspace_id)

    content = "# Getting Started\n\nWelcome to the knowledge workspace.\n" * 50
    ingest_response = client.post(
        "/documents/ingest",
        headers=headers,
        json={
            "source_id": source_id,
            "title": "Getting Started Guide",
            "path": "docs/getting-started.md",
            "content": content,
            "metadata": {"format": "markdown"},
        },
    )
    assert ingest_response.status_code == 200
    ingested = ingest_response.json()
    document_id = ingested["document"]["id"]
    assert ingested["ingestion_status"] == "created"
    assert ingested["chunk_count"] > 0
    assert ingested["document"]["checksum"]
    assert ingested["document"]["indexed_at"]

    source_response = client.get(f"/sources/{source_id}", headers=headers)
    assert source_response.json()["status"] == "ready"

    list_response = client.get(f"/documents?source_id={source_id}", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    get_response = client.get(f"/documents/{document_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["title"] == "Getting Started Guide"

    chunks_response = client.get(f"/documents/{document_id}/chunks", headers=headers)
    assert chunks_response.status_code == 200
    chunks = chunks_response.json()
    assert chunks["total"] == ingested["chunk_count"]
    assert chunks["items"][0]["chunk_index"] == 0

    stats_response = client.get(f"/documents/{document_id}/stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["chunk_count"] == ingested["chunk_count"]
    assert stats["checksum"] == ingested["document"]["checksum"]

    update_response = client.patch(
        f"/documents/{document_id}",
        headers=headers,
        json={"title": "Updated Guide", "metadata": {"format": "markdown", "version": 2}},
    )
    assert update_response.status_code == 200
    assert update_response.json()["title"] == "Updated Guide"
    assert update_response.json()["metadata"]["version"] == 2

    unchanged_response = client.post(
        "/documents/ingest",
        headers=headers,
        json={
            "source_id": source_id,
            "title": "Getting Started Guide",
            "path": "docs/getting-started.md",
            "content": content,
            "metadata": {"format": "markdown"},
        },
    )
    assert unchanged_response.status_code == 200
    assert unchanged_response.json()["ingestion_status"] == "unchanged"

    updated_content = content + "\nAdditional section."
    updated_ingest = client.post(
        "/documents/ingest",
        headers=headers,
        json={
            "source_id": source_id,
            "title": "Getting Started Guide v2",
            "path": "docs/getting-started.md",
            "content": updated_content,
            "metadata": {"format": "markdown"},
        },
    )
    assert updated_ingest.status_code == 200
    assert updated_ingest.json()["ingestion_status"] == "updated"
    assert updated_ingest.json()["document"]["title"] == "Getting Started Guide v2"

    delete_response = client.delete(f"/documents/{document_id}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/documents/{document_id}", headers=headers)
    assert missing_response.status_code == 404


def test_document_ownership_protection() -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers)
    source_id = _create_manual_source(owner_headers, workspace_id)

    ingest_response = client.post(
        "/documents/ingest",
        headers=owner_headers,
        json={
            "source_id": source_id,
            "title": "Private Doc",
            "path": "private.md",
            "content": "Secret content",
        },
    )
    document_id = ingest_response.json()["document"]["id"]

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    list_response = client.get(f"/documents?source_id={source_id}", headers=other_headers)
    assert list_response.status_code == 403

    get_response = client.get(f"/documents/{document_id}", headers=other_headers)
    assert get_response.status_code == 403

    ingest_forbidden = client.post(
        "/documents/ingest",
        headers=other_headers,
        json={
            "source_id": source_id,
            "title": "Hijacked",
            "path": "hijack.md",
            "content": "Unauthorized",
        },
    )
    assert ingest_forbidden.status_code == 403


def test_document_unauthorized_access() -> None:
    unauthorized_ingest = client.post(
        "/documents/ingest",
        json={
            "source_id": str(uuid4()),
            "title": "No Auth",
            "path": "no-auth.md",
            "content": "content",
        },
    )
    assert unauthorized_ingest.status_code == 401

    unauthorized_list = client.get(f"/documents?source_id={uuid4()}")
    assert unauthorized_list.status_code == 401
