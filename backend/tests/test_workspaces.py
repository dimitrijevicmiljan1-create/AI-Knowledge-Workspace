"""Workspace management endpoint tests."""

from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _register_and_login(email: str | None = None, password: str = "securepass123") -> dict[str, str]:
    user_email = email or f"workspace-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "Workspace User"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": user_email, "password": password},
    )
    assert login_response.status_code == 200
    return login_response.json()


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def test_workspace_crud_flow() -> None:
    tokens = _register_and_login()
    headers = _auth_headers(tokens["access_token"])

    create_response = client.post(
        "/workspaces",
        headers=headers,
        json={"name": "Research Hub", "description": "Primary workspace"},
    )
    assert create_response.status_code == 201
    workspace = create_response.json()
    workspace_id = workspace["id"]
    assert workspace["name"] == "Research Hub"
    assert workspace["description"] == "Primary workspace"

    list_response = client.get("/workspaces", headers=headers)
    assert list_response.status_code == 200
    listed = list_response.json()
    assert listed["total"] == 1
    assert len(listed["items"]) == 1
    assert listed["items"][0]["id"] == workspace_id

    get_response = client.get(f"/workspaces/{workspace_id}", headers=headers)
    assert get_response.status_code == 200
    assert get_response.json()["name"] == "Research Hub"

    update_response = client.patch(
        f"/workspaces/{workspace_id}",
        headers=headers,
        json={"name": "Updated Hub", "description": "Updated description"},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Updated Hub"

    stats_response = client.get(f"/workspaces/{workspace_id}/stats", headers=headers)
    assert stats_response.status_code == 200
    stats = stats_response.json()
    assert stats["workspace_id"] == workspace_id
    assert stats["document_count"] == 0
    assert stats["source_count"] == 0
    assert stats["chat_count"] == 0
    assert stats["created_at"]

    delete_response = client.delete(f"/workspaces/{workspace_id}", headers=headers)
    assert delete_response.status_code == 204

    missing_response = client.get(f"/workspaces/{workspace_id}", headers=headers)
    assert missing_response.status_code == 404


def test_workspace_ownership_validation() -> None:
    owner_tokens = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])

    create_response = client.post(
        "/workspaces",
        headers=owner_headers,
        json={"name": "Private Workspace"},
    )
    workspace_id = create_response.json()["id"]

    other_tokens = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    get_response = client.get(f"/workspaces/{workspace_id}", headers=other_headers)
    assert get_response.status_code == 403

    update_response = client.patch(
        f"/workspaces/{workspace_id}",
        headers=other_headers,
        json={"name": "Hijacked"},
    )
    assert update_response.status_code == 403

    delete_response = client.delete(f"/workspaces/{workspace_id}", headers=other_headers)
    assert delete_response.status_code == 403

    stats_response = client.get(f"/workspaces/{workspace_id}/stats", headers=other_headers)
    assert stats_response.status_code == 403


def test_workspace_unauthorized_access() -> None:
    unauthorized_list = client.get("/workspaces")
    assert unauthorized_list.status_code == 401

    unauthorized_create = client.post("/workspaces", json={"name": "No Auth"})
    assert unauthorized_create.status_code == 401

    random_workspace_id = str(uuid4())
    unauthorized_get = client.get(f"/workspaces/{random_workspace_id}")
    assert unauthorized_get.status_code == 401
