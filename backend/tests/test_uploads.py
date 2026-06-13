"""File upload endpoint tests."""

import io
from uuid import uuid4

from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"upload-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Upload User"},
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
        json={"name": "Upload Workspace", "description": "Workspace for upload tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_single_file_upload() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    content = b"# Notes\n\nUploaded markdown content."

    response = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": ("notes.md", io.BytesIO(content), "text/markdown")},
    )
    assert response.status_code == 201
    payload = response.json()["file"]
    assert payload["status"] == "created"
    assert payload["filename"] == "notes.md"
    assert payload["document_id"]
    assert payload["checksum"]

    list_response = client.get(f"/uploads?workspace_id={workspace_id}", headers=headers)
    assert list_response.status_code == 200
    assert list_response.json()["total"] == 1

    workspace_files = client.get(f"/workspaces/{workspace_id}/files", headers=headers)
    assert workspace_files.status_code == 200
    assert workspace_files.json()["items"][0]["filename"] == "notes.md"


def test_multiple_file_upload() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    response = client.post(
        "/uploads/multiple",
        headers=headers,
        data={"workspace_id": workspace_id},
        files=[
            ("files", ("alpha.txt", io.BytesIO(b"alpha content"), "text/plain")),
            ("files", ("beta.md", io.BytesIO(b"# beta"), "text/markdown")),
        ],
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["uploaded"] == 2
    assert payload["failed"] == 0
    assert len(payload["results"]) == 2


def test_invalid_file_rejected() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    response = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": ("malware.exe", io.BytesIO(b"fake exe"), "application/octet-stream")},
    )
    assert response.status_code == 422


def test_large_file_rejected() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    oversized = b"x" * (settings.max_upload_size_bytes + 1)

    response = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": ("large.txt", io.BytesIO(oversized), "text/plain")},
    )
    assert response.status_code == 422


def test_duplicate_file_skipped() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    content = b"duplicate content"

    first = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": ("dup.txt", io.BytesIO(content), "text/plain")},
    )
    assert first.status_code == 201
    document_id = first.json()["file"]["document_id"]

    second = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": ("dup.txt", io.BytesIO(content), "text/plain")},
    )
    assert second.status_code == 201
    second_payload = second.json()["file"]
    assert second_payload["status"] == "skipped"
    assert second_payload["document_id"] == document_id

    multiple = client.post(
        "/uploads/multiple",
        headers=headers,
        data={"workspace_id": workspace_id},
        files=[("files", ("dup.txt", io.BytesIO(content), "text/plain"))],
    )
    assert multiple.json()["skipped"] == 1


def test_file_deletion() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    upload_response = client.post(
        "/uploads",
        headers=headers,
        data={"workspace_id": workspace_id},
        files={"file": ("delete-me.txt", io.BytesIO(b"delete me"), "text/plain")},
    )
    document_id = upload_response.json()["file"]["document_id"]

    delete_response = client.delete(f"/uploads/{document_id}", headers=headers)
    assert delete_response.status_code == 204

    list_response = client.get(f"/uploads?workspace_id={workspace_id}", headers=headers)
    assert list_response.json()["total"] == 0


def test_upload_ownership_protection() -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers)

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    upload_forbidden = client.post(
        "/uploads",
        headers=other_headers,
        data={"workspace_id": workspace_id},
        files={"file": ("secret.txt", io.BytesIO(b"secret"), "text/plain")},
    )
    assert upload_forbidden.status_code == 403

    list_forbidden = client.get(f"/uploads?workspace_id={workspace_id}", headers=other_headers)
    assert list_forbidden.status_code == 403

    workspace_files_forbidden = client.get(f"/workspaces/{workspace_id}/files", headers=other_headers)
    assert workspace_files_forbidden.status_code == 403
