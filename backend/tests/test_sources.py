"""Knowledge source management endpoint tests."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"source-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Source User"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": user_email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _create_workspace(headers: dict[str, str], name: str = "Source Workspace") -> str:
    response = client.post(
        "/workspaces",
        headers=headers,
        json={"name": name, "description": "Workspace for source tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def test_source_crud_flow() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    create_response = client.post(
        "/sources",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Engineering Docs",
            "source_type": "github",
            "config": {
                "repository_url": "https://github.com/owner/repo",
                "branch": "main",
            },
        },
    )
    assert create_response.status_code == 201
    source = create_response.json()
    source_id = source["id"]
    assert source["name"] == "Engineering Docs"
    assert source["source_type"] == "github"
    assert source["workspace_id"] == workspace_id
    assert source["status"] == "pending"
    assert source["last_sync_at"] is None

    list_response = client.get(f"/sources?workspace_id={workspace_id}", headers=headers)
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed["total"] == 1
    assert len(listed["items"]) == 1
    assert listed["items"][0]["id"] == source_id

    get_response = client.get(f"/sources/{source_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Engineering Docs"

    update_response = client.patch(
        f"/sources/{source_id}",
        headers=headers,
        json={
            "name": "Updated Engineering Docs",
            "config": {
                "repository_url": "https://github.com/owner/updated-repo",
                "branch": "develop",
            },
        },
    )
    assert update_response.status_code == 200
    updated = update_response.json()
    assert updated["name"] == "Updated Engineering Docs"
    assert updated["config"]["branch"] == "develop"

    stats_response = client.get(f"/sources/{source_id}/stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["source_id"] == source_id
    assert stats["document_count"] == 0
    assert stats["chunk_count"] == 0
    assert stats["status"] == "pending"
    assert stats["last_sync_at"] is None

    delete_response = client.delete(f"/sources/{source_id}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/sources/{source_id}", headers=headers)
    assert missing_response.status_code == 404


def test_source_ownership_protection() -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers, "Protected Workspace")

    create_response = client.post(
        "/sources",
        headers=owner_headers,
        json={
            "workspace_id": workspace_id,
            "name": "Private Source",
            "source_type": "manual",
            "config": {"description": "Owner notes"},
        },
    )
    source_id = create_response.json()["id"]

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    list_response = client.get(f"/sources?workspace_id={workspace_id}", headers=other_headers)
    assert list_response.status_code == 403

    get_response = client.get(f"/sources/{source_id}", headers=other_headers)
    assert get_response.status_code == 403

    update_response = client.patch(
        f"/sources/{source_id}",
        headers=other_headers,
        json={"name": "Hijacked"},
    )
    assert update_response.status_code == 403

    delete_response = client.delete(f"/sources/{source_id}", headers=other_headers)
    assert delete_response.status_code == 403

    stats_response = client.get(f"/sources/{source_id}/stats", headers=other_headers)
    assert stats_response.status_code == 403


def test_source_validation_errors() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)

    invalid_github = client.post(
        "/sources",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Invalid GitHub",
            "source_type": "github",
            "config": {"repository_url": "https://example.com/not-github"},
        },
    )
    assert invalid_github.status_code == 422
    github_errors = invalid_github.json()["detail"]["errors"]
    assert any(error["field"] == "config.repository_url" for error in github_errors)

    invalid_obsidian = client.post(
        "/sources",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Invalid Obsidian",
            "source_type": "obsidian",
            "config": {"vault_path": "/tmp/vault"},
        },
    )
    assert invalid_obsidian.status_code == 422
    obsidian_errors = invalid_obsidian.json()["detail"]["errors"]
    assert any(error["field"] == "config.vault_name" for error in obsidian_errors)

    invalid_local_files = client.post(
        "/sources",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Invalid Local Files",
            "source_type": "local_files",
            "config": {},
        },
    )
    assert invalid_local_files.status_code == 422
    local_errors = invalid_local_files.json()["detail"]["errors"]
    assert any(error["field"] == "config.directory_path" for error in local_errors)

    valid_manual = client.post(
        "/sources",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "name": "Manual Source",
            "source_type": "manual",
            "config": {},
        },
    )
    assert valid_manual.status_code == 201
    assert valid_manual.json()["source_type"] == "manual"


def test_source_unauthorized_access() -> None:
    unauthorized_list = client.get(f"/sources?workspace_id={uuid4()}")
    assert unauthorized_list.status_code == 401

    unauthorized_create = client.post(
        "/sources",
        json={
            "workspace_id": str(uuid4()),
            "name": "No Auth",
            "source_type": "manual",
            "config": {},
        },
    )
    assert unauthorized_create.status_code == 401

    random_source_id = str(uuid4())
    unauthorized_get = client.get(f"/sources/{random_source_id}")
    assert unauthorized_get.status_code == 401
