from datetime import UTC, datetime, timedelta
from uuid import UUID

from jose import JWTError, jwt

from app.core.config import settings
from app.core.security import ALGORITHM
from app.github.client import GitHubClient, GitHubOAuthClient
from app.github.encryption import TokenEncryption, get_token_encryption
from app.github.exceptions import GitHubAuthError
from app.models.github_connection import GitHubConnection
from app.models.user import User
from app.repositories.github_connection_repository import GitHubConnectionRepository


class GitHubAuthService:
    OAUTH_STATE_TYPE = "github_oauth_state"
    STATE_EXPIRE_MINUTES = 15

    def __init__(
        self,
        connection_repository: GitHubConnectionRepository,
        oauth_client: GitHubOAuthClient | None = None,
        token_encryption: TokenEncryption | None = None,
    ) -> None:
        self.connection_repository = connection_repository
        self.oauth_client = oauth_client or GitHubOAuthClient()
        self.token_encryption = token_encryption or get_token_encryption()

    def create_authorization_url(self, user: User) -> str:
        state = self._create_state_token(user.id)
        return self.oauth_client.build_authorization_url(state=state)

    def complete_oauth(self, *, code: str, state: str) -> GitHubConnection:
        user_id = self._verify_state_token(state)
        access_token = self.oauth_client.exchange_code_for_token(code)

        github_client = GitHubClient(access_token)
        profile = github_client.get_authenticated_user()
        github_user_id = int(profile["id"])
        github_username = str(profile["login"])

        encrypted_token = self.token_encryption.encrypt(access_token)
        connected_at = datetime.now(UTC)

        existing = self.connection_repository.get_by_user_id(user_id)
        if existing is not None:
            return self.connection_repository.update(
                existing,
                github_user_id=github_user_id,
                github_username=github_username,
                access_token_encrypted=encrypted_token,
                connected_at=connected_at,
            )

        return self.connection_repository.create(
            user_id=user_id,
            github_user_id=github_user_id,
            github_username=github_username,
            access_token_encrypted=encrypted_token,
            connected_at=connected_at,
        )

    def get_connection_for_user(self, user: User) -> GitHubConnection | None:
        return self.connection_repository.get_by_user_id(user.id)

    def get_client_for_connection(self, connection: GitHubConnection) -> GitHubClient:
        access_token = self.token_encryption.decrypt(connection.access_token_encrypted)
        return GitHubClient(access_token)

    def _create_state_token(self, user_id: UUID) -> str:
        expire = datetime.now(UTC) + timedelta(minutes=self.STATE_EXPIRE_MINUTES)
        payload = {
            "sub": str(user_id),
            "type": self.OAUTH_STATE_TYPE,
            "exp": expire,
        }
        return jwt.encode(payload, settings.jwt_secret_key, algorithm=ALGORITHM)

    def _verify_state_token(self, state: str) -> UUID:
        try:
            payload = jwt.decode(state, settings.jwt_secret_key, algorithms=[ALGORITHM])
        except JWTError as error:
            raise GitHubAuthError("Invalid OAuth state token") from error

        if payload.get("type") != self.OAUTH_STATE_TYPE:
            raise GitHubAuthError("Invalid OAuth state token type")

        user_id = payload.get("sub")
        if not user_id:
            raise GitHubAuthError("OAuth state token missing subject")

        return UUID(str(user_id))
