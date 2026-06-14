import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.github_sync_job import GitHubSyncJob, GitHubSyncJobStatus


class GitHubSyncJobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, repository_id: uuid.UUID) -> GitHubSyncJob:
        job = GitHubSyncJob(
            repository_id=repository_id,
            status=GitHubSyncJobStatus.pending,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: uuid.UUID) -> GitHubSyncJob | None:
        return self.db.get(GitHubSyncJob, job_id)

    def get_latest_for_repository(self, repository_id: uuid.UUID) -> GitHubSyncJob | None:
        statement = (
            select(GitHubSyncJob)
            .where(GitHubSyncJob.repository_id == repository_id)
            .order_by(GitHubSyncJob.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def get_active_for_repository(self, repository_id: uuid.UUID) -> GitHubSyncJob | None:
        statement = (
            select(GitHubSyncJob)
            .where(
                GitHubSyncJob.repository_id == repository_id,
                GitHubSyncJob.status.in_(
                    [GitHubSyncJobStatus.pending, GitHubSyncJobStatus.processing]
                ),
            )
            .order_by(GitHubSyncJob.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def update(self, job: GitHubSyncJob, **fields: object) -> GitHubSyncJob:
        for field, value in fields.items():
            setattr(job, field, value)
        self.db.commit()
        self.db.refresh(job)
        return job
