from app.github.auth import GitHubAuthService
from app.github.client import GitHubClient, GitHubRepositoryInfo
from app.models.github_connection import GitHubConnection
from app.models.user import User
from app.repositories.github_connection_repository import GitHubConnectionRepository


class GitHubRepositoryDiscoveryService:
    """Discover repositories available to a connected GitHub account."""

    def __init__(
        self,
        connection_repository: GitHubConnectionRepository,
        auth_service: GitHubAuthService | None = None,
    ) -> None:
        self.connection_repository = connection_repository
        self.auth_service = auth_service or GitHubAuthService(connection_repository)

    def list_available_repositories(
        self,
        user: User,
        *,
        page: int = 1,
        per_page: int = 100,
    ) -> list[GitHubRepositoryInfo]:
        connection = self._get_connection(user)
        client = self.auth_service.get_client_for_connection(connection)
        return client.list_repositories(page=page, per_page=per_page)

    def get_connection(self, user: User) -> GitHubConnection:
        return self._get_connection(user)

    def _get_connection(self, user: User) -> GitHubConnection:
        connection = self.connection_repository.get_by_user_id(user.id)
        if connection is None:
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub account is not connected",
            )
        return connection
