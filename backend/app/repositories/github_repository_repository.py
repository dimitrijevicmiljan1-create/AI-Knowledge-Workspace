import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.github_repository import GitHubRepository, GitHubRepositorySyncStatus


class GitHubRepositoryRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(
        self,
        *,
        connection_id: uuid.UUID,
        workspace_id: uuid.UUID,
        source_id: uuid.UUID,
        github_repo_id: int,
        repository_owner: str,
        repository_name: str,
        default_branch: str,
        sync_status: GitHubRepositorySyncStatus = GitHubRepositorySyncStatus.pending,
    ) -> GitHubRepository:
        repository = GitHubRepository(
            connection_id=connection_id,
            workspace_id=workspace_id,
            source_id=source_id,
            github_repo_id=github_repo_id,
            repository_owner=repository_owner,
            repository_name=repository_name,
            default_branch=default_branch,
            sync_status=sync_status,
        )
        self.db.add(repository)
        self.db.commit()
        self.db.refresh(repository)
        return repository

    def get_by_id(self, repository_id: uuid.UUID) -> GitHubRepository | None:
        statement = (
            select(GitHubRepository)
            .options(joinedload(GitHubRepository.source))
            .where(GitHubRepository.id == repository_id)
        )
        return self.db.scalars(statement).unique().first()

    def get_by_id_for_user(self, repository_id: uuid.UUID, user_id: uuid.UUID) -> GitHubRepository | None:
        from app.models.github_connection import GitHubConnection

        statement = (
            select(GitHubRepository)
            .join(GitHubConnection, GitHubRepository.connection_id == GitHubConnection.id)
            .options(joinedload(GitHubRepository.source))
            .where(
                GitHubRepository.id == repository_id,
                GitHubConnection.user_id == user_id,
            )
        )
        return self.db.scalars(statement).unique().first()

    def get_by_github_repo_id(
        self,
        connection_id: uuid.UUID,
        github_repo_id: int,
    ) -> GitHubRepository | None:
        statement = select(GitHubRepository).where(
            GitHubRepository.connection_id == connection_id,
            GitHubRepository.github_repo_id == github_repo_id,
        )
        return self.db.scalar(statement)

    def list_by_connection(self, connection_id: uuid.UUID) -> list[GitHubRepository]:
        statement = (
            select(GitHubRepository)
            .where(GitHubRepository.connection_id == connection_id)
            .order_by(GitHubRepository.created_at.desc())
        )
        return list(self.db.scalars(statement).all())

    def update(self, repository: GitHubRepository, **fields: object) -> GitHubRepository:
        for field, value in fields.items():
            if value is not None:
                setattr(repository, field, value)
        self.db.commit()
        self.db.refresh(repository)
        return repository

    def delete(self, repository: GitHubRepository) -> None:
        self.db.delete(repository)
        self.db.commit()
