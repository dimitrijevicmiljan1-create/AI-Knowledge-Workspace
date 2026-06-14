"""GitHub integration tests."""

from datetime import UTC, datetime
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

import pytest
from cryptography.fernet import Fernet
from fastapi.testclient import TestClient
from jose import jwt
from sqlalchemy.orm import Session

from app.ai.base import EmbeddingProvider
from app.ai.chat.provider import ChatProvider
from app.ai.chat.schemas import ChatMessage
from app.core.config import settings
from app.core.security import ALGORITHM
from app.db.session import SessionLocal
from app.github.auth import GitHubAuthService
from app.github.client import GitHubFileContent, GitHubRepositoryInfo, GitHubTreeEntry
from app.github.encryption import TokenEncryption
from app.github.filters import should_index_file
from app.github.parser import RepositoryFileParser
from app.github.sync import GitHubSyncService
from app.main import app
from app.models.github_sync_job import GitHubSyncJobStatus
from app.repositories.document_repository import DocumentRepository
from app.repositories.github_repository_repository import GitHubRepositoryRepository
from app.repositories.github_sync_job_repository import GitHubSyncJobRepository
from app.repositories.user_repository import UserRepository

client = TestClient(app)

TEST_ENCRYPTION_KEY = Fernet.generate_key().decode()
JWT_AUTH_DOC = """
# Authentication

JWT authentication is configured using JWT_SECRET_KEY.
Access tokens expire after 30 minutes.
Refresh tokens expire after 7 days.
"""


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
    @property
    def model_name(self) -> str:
        return "mock-chat-model"

    def generate_answer(self, messages: list[ChatMessage]) -> str:
        return "JWT authentication is configured using JWT_SECRET_KEY [1]."


@pytest.fixture(autouse=True)
def github_settings(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(settings, "github_client_id", "test-client-id")
    monkeypatch.setattr(settings, "github_client_secret", "test-client-secret")
    monkeypatch.setattr(settings, "github_oauth_redirect_uri", "http://testserver/github/callback")
    monkeypatch.setattr(settings, "github_token_encryption_key", TEST_ENCRYPTION_KEY)


@pytest.fixture
def mock_embedding_provider() -> MockEmbeddingProvider:
    return MockEmbeddingProvider()


@pytest.fixture
def github_patch(mock_embedding_provider: MockEmbeddingProvider):
    with (
        patch("app.services.embedding_service.get_embedding_provider", return_value=mock_embedding_provider),
        patch("app.services.search_service.get_embedding_provider", return_value=mock_embedding_provider),
        patch("app.rag.rag_service.get_chat_provider", return_value=MockChatProvider()),
    ):
        yield


def _register_and_login(email: str | None = None, password: str = "securepass123") -> tuple[dict[str, str], str]:
    user_email = email or f"github-{uuid4()}@example.com"
    client.post(
        "/auth/register",
        json={"email": user_email, "password": password, "full_name": "GitHub User"},
    )
    login_response = client.post(
        "/auth/login",
        json={"email": user_email, "password": password},
    )
    assert login_response.status_code == 200
    tokens = login_response.json()
    return tokens, user_email


def _auth_headers(access_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {access_token}"}


def _create_workspace(headers: dict[str, str]) -> str:
    response = client.post(
        "/workspaces",
        headers=headers,
        json={"name": "GitHub Workspace", "description": "Workspace for GitHub tests"},
    )
    assert response.status_code == 201
    return response.json()["id"]


def _create_oauth_state(user_id: str) -> str:
    return jwt.encode(
        {
            "sub": user_id,
            "type": GitHubAuthService.OAUTH_STATE_TYPE,
            "exp": datetime.now(UTC).timestamp() + 900,
        },
        settings.jwt_secret_key,
        algorithm=ALGORITHM,
    )


def _mock_repo_info() -> GitHubRepositoryInfo:
    return GitHubRepositoryInfo(
        id=123456,
        owner="acme",
        name="auth-docs",
        full_name="acme/auth-docs",
        default_branch="main",
        visibility="private",
        description="Authentication documentation",
        updated_at="2026-06-14T12:00:00Z",
        private=True,
    )


def _connect_github(headers: dict[str, str]) -> None:
    with (
        patch("app.github.auth.GitHubOAuthClient.exchange_code_for_token", return_value="gho_test_token"),
        patch("app.github.auth.GitHubClient.get_authenticated_user", return_value={"id": 42, "login": "octocat"}),
    ):
        me = client.get("/users/me", headers=headers)
        state = _create_oauth_state(me.json()["id"])
        callback = client.get("/github/callback", params={"code": "test-code", "state": state})
        assert callback.status_code == 200


def _add_repository(headers: dict[str, str], workspace_id: str) -> str:
    response = client.post(
        "/github/repositories",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "github_repo_id": 123456,
            "owner": "acme",
            "name": "auth-docs",
        },
    )
    assert response.status_code == 201
    return response.json()["id"]


def _execute_sync(repo_id: str, user_email: str) -> None:
    db = SessionLocal()
    try:
        user = UserRepository(db).get_by_email(user_email)
        assert user is not None
        repository = GitHubRepositoryRepository(db).get_by_id(UUID(repo_id))
        assert repository is not None
        job = GitHubSyncJobRepository(db).create(repository_id=repository.id)
        GitHubSyncService(db).execute_sync(job.id, repository.id, user.id)
    finally:
        db.close()


def test_should_index_supported_files() -> None:
    assert should_index_file("README.md")
    assert should_index_file("src/auth/jwt.py")
    assert should_index_file("docs/authentication.md")
    assert not should_index_file("node_modules/pkg/index.js")
    assert not should_index_file("assets/logo.png")
    assert not should_index_file("dist/bundle.js")


def test_repository_file_parser_builds_metadata() -> None:
    parsed = RepositoryFileParser().parse(
        path="src/auth/jwt.py",
        content=JWT_AUTH_DOC,
        blob_sha="abc123",
        commit_sha="commit123",
        repository_owner="acme",
        repository_name="auth-docs",
    )
    metadata = RepositoryFileParser().build_document_metadata(parsed)
    assert metadata["repository_name"] == "auth-docs"
    assert metadata["repository_owner"] == "acme"
    assert metadata["relative_path"] == "src/auth/jwt.py"
    assert metadata["file_name"] == "jwt.py"
    assert metadata["last_commit_sha"] == "commit123"


def test_token_encryption_roundtrip() -> None:
    encryption = TokenEncryption(TEST_ENCRYPTION_KEY)
    encrypted = encryption.encrypt("gho_test_token")
    assert encrypted != "gho_test_token"
    assert encryption.decrypt(encrypted) == "gho_test_token"


@patch("app.github.auth.GitHubOAuthClient.exchange_code_for_token", return_value="gho_test_token")
@patch("app.github.auth.GitHubClient.get_authenticated_user")
def test_oauth_callback_stores_encrypted_connection(
    mock_get_user: MagicMock,
    mock_exchange: MagicMock,
) -> None:
    mock_get_user.return_value = {"id": 42, "login": "octocat"}
    tokens, _ = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    me = client.get("/users/me", headers=headers)
    state = _create_oauth_state(me.json()["id"])

    response = client.get(
        "/github/callback",
        params={"code": "test-code", "state": state},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["success"] is True
    assert payload["github_username"] == "octocat"

    connection_response = client.get("/github/connection", headers=headers)
    assert connection_response.status_code == 200
    assert connection_response.json()["github_username"] == "octocat"


def test_connect_returns_authorization_url() -> None:
    tokens, _ = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    response = client.post("/github/connect", headers=headers)
    assert response.status_code == 200
    assert "github.com/login/oauth/authorize" in response.json()["authorization_url"]


@patch("app.github.repositories.GitHubClient.list_repositories")
def test_list_discovered_repositories(mock_list_repos: MagicMock, github_patch) -> None:
    mock_list_repos.return_value = [_mock_repo_info()]
    tokens, _ = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    _connect_github(headers)

    response = client.get("/github/repositories", headers=headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 1
    assert payload["items"][0]["full_name"] == "acme/auth-docs"


@patch("app.github.auth.GitHubClient.get_repository")
def test_add_repository_creates_source(mock_get_repo: MagicMock, github_patch) -> None:
    mock_get_repo.return_value = _mock_repo_info()
    tokens, _ = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    _connect_github(headers)

    response = client.post(
        "/github/repositories",
        headers=headers,
        json={
            "workspace_id": workspace_id,
            "github_repo_id": 123456,
            "owner": "acme",
            "name": "auth-docs",
        },
    )
    assert response.status_code == 201
    payload = response.json()
    assert payload["repository_name"] == "auth-docs"
    assert payload["sync_status"] == "pending"


@patch("app.github.auth.GitHubClient.get_repository")
def test_repository_ownership_protection(mock_get_repo: MagicMock, github_patch) -> None:
    mock_get_repo.return_value = _mock_repo_info()
    owner_tokens, _ = _register_and_login()
    owner_headers = _auth_headers(owner_tokens["access_token"])
    workspace_id = _create_workspace(owner_headers)
    _connect_github(owner_headers)
    repo_id = _add_repository(owner_headers, workspace_id)

    other_tokens, _ = _register_and_login()
    other_headers = _auth_headers(other_tokens["access_token"])

    forbidden = client.get(f"/github/repositories/{repo_id}", headers=other_headers)
    assert forbidden.status_code == 404


def test_github_unauthorized_access() -> None:
    response = client.post("/github/connect")
    assert response.status_code == 401


@patch("app.github.client.GitHubClient.get_file_content")
@patch("app.github.client.GitHubClient.get_recursive_tree")
@patch("app.github.client.GitHubClient.get_branch_commit_sha")
@patch("app.github.auth.GitHubClient.get_repository")
def test_repository_sync_creates_documents_and_embeddings(
    mock_get_repo: MagicMock,
    mock_commit_sha: MagicMock,
    mock_tree: MagicMock,
    mock_file_content: MagicMock,
    github_patch,
) -> None:
    mock_get_repo.return_value = _mock_repo_info()
    mock_commit_sha.return_value = "commit123"
    mock_tree.return_value = [
        GitHubTreeEntry(path="src/auth/jwt.py", sha="blob123", type="blob", size=100),
        GitHubTreeEntry(path="README.md", sha="blob456", type="blob", size=50),
    ]

    def _file_content(owner: str, name: str, path: str, *, ref: str) -> GitHubFileContent:
        content = JWT_AUTH_DOC if path.endswith(".py") else "# Auth Docs\nJWT overview."
        return GitHubFileContent(path=path, content=content, sha=f"sha-{path}", size=len(content))

    mock_file_content.side_effect = _file_content

    tokens, user_email = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    _connect_github(headers)
    repo_id = _add_repository(headers, workspace_id)

    _execute_sync(repo_id, user_email)

    db = SessionLocal()
    try:
        repository = GitHubRepositoryRepository(db).get_by_id(UUID(repo_id))
        assert repository is not None
        documents = DocumentRepository(db).list_by_source(repository.source_id)
        assert len(documents) == 2
        assert any(document.path == "src/auth/jwt.py" for document in documents)
    finally:
        db.close()

    status_response = client.get(f"/github/repositories/{repo_id}/status", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["status"] == "completed"
    assert status_response.json()["documents_created"] == 2


@patch("app.github.client.GitHubClient.get_file_content")
@patch("app.github.client.GitHubClient.get_recursive_tree")
@patch("app.github.client.GitHubClient.get_branch_commit_sha")
@patch("app.github.auth.GitHubClient.get_repository")
def test_incremental_sync_skips_unchanged_files(
    mock_get_repo: MagicMock,
    mock_commit_sha: MagicMock,
    mock_tree: MagicMock,
    mock_file_content: MagicMock,
    github_patch,
) -> None:
    mock_get_repo.return_value = _mock_repo_info()
    mock_commit_sha.return_value = "commit123"
    mock_tree.return_value = [
        GitHubTreeEntry(path="src/auth/jwt.py", sha="blob123", type="blob", size=100),
    ]

    mock_file_content.return_value = GitHubFileContent(
        path="src/auth/jwt.py",
        content=JWT_AUTH_DOC,
        sha="blob123",
        size=len(JWT_AUTH_DOC),
    )

    tokens, user_email = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    _connect_github(headers)
    repo_id = _add_repository(headers, workspace_id)

    _execute_sync(repo_id, user_email)
    _execute_sync(repo_id, user_email)

    db = SessionLocal()
    try:
        repository = GitHubRepositoryRepository(db).get_by_id(UUID(repo_id))
        assert repository is not None
        documents = DocumentRepository(db).list_by_source(repository.source_id)
        assert len(documents) == 1
    finally:
        db.close()

    status_response = client.get(f"/github/repositories/{repo_id}/status", headers=headers)
    assert status_response.status_code == 200
    assert status_response.json()["documents_created"] == 0
    assert status_response.json()["documents_updated"] == 0


@patch("app.github.client.GitHubClient.get_file_content")
@patch("app.github.client.GitHubClient.get_recursive_tree")
@patch("app.github.client.GitHubClient.get_branch_commit_sha")
@patch("app.github.auth.GitHubClient.get_repository")
def test_sync_deletes_removed_files(
    mock_get_repo: MagicMock,
    mock_commit_sha: MagicMock,
    mock_tree: MagicMock,
    mock_file_content: MagicMock,
    github_patch,
) -> None:
    mock_get_repo.return_value = _mock_repo_info()
    mock_commit_sha.return_value = "commit123"

    tokens, user_email = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    _connect_github(headers)
    repo_id = _add_repository(headers, workspace_id)

    mock_tree.return_value = [
        GitHubTreeEntry(path="src/auth/jwt.py", sha="blob123", type="blob", size=100),
        GitHubTreeEntry(path="README.md", sha="blob456", type="blob", size=50),
    ]

    def _file_content(owner: str, name: str, path: str, *, ref: str) -> GitHubFileContent:
        content = JWT_AUTH_DOC if path.endswith(".py") else "# Auth Docs"
        return GitHubFileContent(path=path, content=content, sha=f"sha-{path}", size=len(content))

    mock_file_content.side_effect = _file_content
    _execute_sync(repo_id, user_email)

    mock_tree.return_value = [
        GitHubTreeEntry(path="src/auth/jwt.py", sha="blob123", type="blob", size=100),
    ]
    _execute_sync(repo_id, user_email)

    db = SessionLocal()
    try:
        repository = GitHubRepositoryRepository(db).get_by_id(UUID(repo_id))
        assert repository is not None
        documents = DocumentRepository(db).list_by_source(repository.source_id)
        assert len(documents) == 1
        assert documents[0].path == "src/auth/jwt.py"
    finally:
        db.close()

    status_response = client.get(f"/github/repositories/{repo_id}/status", headers=headers)
    assert status_response.json()["documents_deleted"] == 1


@patch("app.github.client.GitHubClient.get_file_content")
@patch("app.github.client.GitHubClient.get_recursive_tree")
@patch("app.github.client.GitHubClient.get_branch_commit_sha")
@patch("app.github.auth.GitHubClient.get_repository")
def test_acceptance_search_and_rag_integration(
    mock_get_repo: MagicMock,
    mock_commit_sha: MagicMock,
    mock_tree: MagicMock,
    mock_file_content: MagicMock,
    github_patch,
) -> None:
    mock_get_repo.return_value = _mock_repo_info()
    mock_commit_sha.return_value = "commit123"
    mock_tree.return_value = [
        GitHubTreeEntry(path="src/auth/jwt.py", sha="blob123", type="blob", size=100),
    ]
    mock_file_content.return_value = GitHubFileContent(
        path="src/auth/jwt.py",
        content=JWT_AUTH_DOC,
        sha="blob123",
        size=len(JWT_AUTH_DOC),
    )

    tokens, user_email = _register_and_login()
    headers = _auth_headers(tokens["access_token"])
    workspace_id = _create_workspace(headers)
    _connect_github(headers)
    repo_id = _add_repository(headers, workspace_id)
    _execute_sync(repo_id, user_email)

    db = SessionLocal()
    try:
        repository = GitHubRepositoryRepository(db).get_by_id(UUID(repo_id))
        assert repository is not None
        source_id = str(repository.source_id)
    finally:
        db.close()

    search_response = client.post(
        f"/search/source/{source_id}",
        headers=headers,
        json={"query": "JWT authentication configured", "top_k": 5},
    )
    assert search_response.status_code == 200
    search_payload = search_response.json()
    assert search_payload["total_results"] >= 1
    assert search_payload["results"][0]["file_path"] == "src/auth/jwt.py"
    assert search_payload["results"][0]["repository_name"] == "acme/auth-docs"

    chat_response = client.post(
        f"/chat/source/{source_id}",
        headers=headers,
        json={"question": "How is JWT authentication configured?", "top_k": 5},
    )
    assert chat_response.status_code == 200
    chat_payload = chat_response.json()
    assert "JWT_SECRET_KEY" in chat_payload["answer"]
    assert len(chat_payload["citations"]) >= 1
    assert chat_payload["citations"][0]["file_path"] == "src/auth/jwt.py"
    assert chat_payload["citations"][0]["repository_name"] == "acme/auth-docs"
