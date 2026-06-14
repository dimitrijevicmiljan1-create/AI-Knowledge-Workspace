import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.github.auth import GitHubAuthService
from app.github.client import GitHubRepositoryInfo
from app.github.repositories import GitHubRepositoryDiscoveryService
from app.github.sync import GitHubSyncService
from app.models.github_repository import GitHubRepository, GitHubRepositorySyncStatus
from app.models.github_sync_job import GitHubSyncJob
from app.models.source import SourceType
from app.models.user import User
from app.repositories.github_connection_repository import GitHubConnectionRepository
from app.repositories.github_repository_repository import GitHubRepositoryRepository
from app.repositories.source_repository import SourceRepository
from app.repositories.workspace_repository import WorkspaceRepository
from app.schemas.github import (
    GitHubConnectionResponse,
    GitHubConnectResponse,
    GitHubDiscoveredRepository,
    GitHubOAuthCallbackResponse,
    GitHubRepositoryAddRequest,
    GitHubRepositoryDiscoveryResponse,
    GitHubRepositoryResponse,
    GitHubRepositorySyncResponse,
    GitHubSyncJobResponse,
)


class GitHubService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.connection_repository = GitHubConnectionRepository(db)
        self.repository_repository = GitHubRepositoryRepository(db)
        self.source_repository = SourceRepository(db)
        self.workspace_repository = WorkspaceRepository(db)
        self.auth_service = GitHubAuthService(self.connection_repository)
        self.discovery_service = GitHubRepositoryDiscoveryService(
            self.connection_repository,
            self.auth_service,
        )
        self.sync_service = GitHubSyncService(db)

    def initiate_connect(self, user: User) -> GitHubConnectResponse:
        authorization_url = self.auth_service.create_authorization_url(user)
        return GitHubConnectResponse(authorization_url=authorization_url)

    def complete_oauth(self, *, code: str, state: str) -> GitHubOAuthCallbackResponse:
        connection = self.auth_service.complete_oauth(code=code, state=state)
        return GitHubOAuthCallbackResponse(
            success=True,
            github_username=connection.github_username,
            connected_at=connection.connected_at,
        )

    def get_connection(self, user: User) -> GitHubConnectionResponse:
        connection = self.connection_repository.get_by_user_id(user.id)
        if connection is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub account is not connected",
            )
        return GitHubConnectionResponse(
            github_username=connection.github_username,
            connected_at=connection.connected_at,
        )

    def list_discovered_repositories(
        self,
        user: User,
        *,
        page: int = 1,
        per_page: int = 100,
    ) -> GitHubRepositoryDiscoveryResponse:
        repositories = self.discovery_service.list_available_repositories(
            user,
            page=page,
            per_page=per_page,
        )
        return GitHubRepositoryDiscoveryResponse(
            items=[self._to_discovery_item(repo) for repo in repositories],
            page=page,
            per_page=per_page,
            total=len(repositories),
        )

    def add_repository(
        self,
        user: User,
        repository_in: GitHubRepositoryAddRequest,
    ) -> GitHubRepositoryResponse:
        connection = self.discovery_service.get_connection(user)
        self._ensure_workspace_owner(user, repository_in.workspace_id)

        existing = self.repository_repository.get_by_github_repo_id(
            connection.id,
            repository_in.github_repo_id,
        )
        if existing is not None:
            return self._to_repository_response(existing)

        client = self.auth_service.get_client_for_connection(connection)
        repo_info = client.get_repository(repository_in.owner, repository_in.name)

        source = self.source_repository.create(
            workspace_id=repository_in.workspace_id,
            name=f"github/{repo_info.full_name}",
            source_type=SourceType.github,
            config={
                "repository_url": f"https://github.com/{repo_info.full_name}",
                "branch": repo_info.default_branch,
                "github_repo_id": repo_info.id,
            },
        )

        repository = self.repository_repository.create(
            connection_id=connection.id,
            workspace_id=repository_in.workspace_id,
            source_id=source.id,
            github_repo_id=repo_info.id,
            repository_owner=repo_info.owner,
            repository_name=repo_info.name,
            default_branch=repo_info.default_branch,
            sync_status=GitHubRepositorySyncStatus.pending,
        )
        return self._to_repository_response(repository)

    def get_repository(self, user: User, repository_id: uuid.UUID) -> GitHubRepositoryResponse:
        repository = self._get_owned_repository(user, repository_id)
        return self._to_repository_response(repository)

    def start_sync(self, user: User, repository_id: uuid.UUID) -> GitHubRepositorySyncResponse:
        job = self.sync_service.start_sync(repository_id, user)
        return GitHubRepositorySyncResponse(
            job_id=job.id,
            repository_id=repository_id,
            status=job.status,
        )

    def get_sync_status(self, user: User, repository_id: uuid.UUID) -> GitHubSyncJobResponse:
        self._get_owned_repository(user, repository_id)
        job = self.sync_service.get_latest_job(repository_id)
        if job is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No sync job found for repository",
            )
        return self._to_sync_job_response(job)

    def delete_repository(self, user: User, repository_id: uuid.UUID) -> None:
        repository = self._get_owned_repository(user, repository_id)
        source = repository.source
        self.repository_repository.delete(repository)
        if source is not None:
            self.source_repository.delete(source)

    def _get_owned_repository(self, user: User, repository_id: uuid.UUID) -> GitHubRepository:
        repository = self.repository_repository.get_by_id_for_user(repository_id, user.id)
        if repository is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="GitHub repository not found",
            )
        return repository

    def _ensure_workspace_owner(self, user: User, workspace_id: uuid.UUID) -> None:
        workspace = self.workspace_repository.get_by_id(workspace_id)
        if workspace is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace not found",
            )
        if workspace.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this workspace",
            )

    def _to_discovery_item(self, repo: GitHubRepositoryInfo) -> GitHubDiscoveredRepository:
        return GitHubDiscoveredRepository(
            github_repo_id=repo.id,
            owner=repo.owner,
            name=repo.name,
            full_name=repo.full_name,
            default_branch=repo.default_branch,
            visibility=repo.visibility,
            description=repo.description,
            updated_at=repo.updated_at,
            private=repo.private,
        )

    def _to_repository_response(self, repository: GitHubRepository) -> GitHubRepositoryResponse:
        return GitHubRepositoryResponse(
            id=repository.id,
            workspace_id=repository.workspace_id,
            source_id=repository.source_id,
            github_repo_id=repository.github_repo_id,
            repository_owner=repository.repository_owner,
            repository_name=repository.repository_name,
            default_branch=repository.default_branch,
            last_commit_sha=repository.last_commit_sha,
            last_synced_at=repository.last_synced_at,
            sync_status=repository.sync_status,
            created_at=repository.created_at,
            updated_at=repository.updated_at,
        )

    def _to_sync_job_response(self, job: GitHubSyncJob) -> GitHubSyncJobResponse:
        return GitHubSyncJobResponse(
            id=job.id,
            repository_id=job.repository_id,
            status=job.status,
            started_at=job.started_at,
            completed_at=job.completed_at,
            files_scanned=job.files_scanned,
            documents_created=job.documents_created,
            documents_updated=job.documents_updated,
            documents_deleted=job.documents_deleted,
            error_message=job.error_message,
            created_at=job.created_at,
        )
