"""Authentication endpoint tests."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)

TEST_EMAIL = "auth.test@example.com"
TEST_PASSWORD = "securepass123"


def test_register_login_me_and_refresh_flow() -> None:
    register_response = client.post(
        "/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": "Auth Test User",
        },
    )
    assert register_response.status_code == 201
    user = register_response.json()
    assert user["email"] == TEST_EMAIL
    assert "hashed_password" not in user
    assert user["is_active"] is True

    login_response = client.post(
        "/auth/login",
        json={"email": TEST_EMAIL, "password": TEST_PASSWORD},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    assert tokens["token_type"] == "bearer"
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    me_response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert me_response.status_code == 200
    assert me_response.json()["email"] == TEST_EMAIL

    refresh_response = client.post(
        "/auth/refresh",
        json={"refresh_token": tokens["refresh_token"]},
    )
    assert refresh_response.status_code == 200
    refreshed = refresh_response.json()
    assert refreshed["access_token"]
    assert refreshed["refresh_token"]

    users_me_response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {refreshed['access_token']}"},
    )
    assert users_me_response.status_code == 200

    patch_response = client.patch(
        "/users/me",
        headers={"Authorization": f"Bearer {refreshed['access_token']}"},
        json={"full_name": "Updated Name"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["full_name"] == "Updated Name"


def test_unauthorized_access() -> None:
    response = client.get("/auth/me")
    assert response.status_code == 401

    invalid_response = client.get(
        "/auth/me",
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert invalid_response.status_code == 401


def test_password_validation() -> None:
    response = client.post(
        "/auth/register",
        json={"email": "short@example.com", "password": "short"},
    )
    assert response.status_code == 422
