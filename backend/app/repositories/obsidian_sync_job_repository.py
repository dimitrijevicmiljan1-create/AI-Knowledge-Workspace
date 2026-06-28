import uuid

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.obsidian_sync_job import ObsidianSyncJob, ObsidianSyncJobStatus


class ObsidianSyncJobRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, *, vault_id: uuid.UUID) -> ObsidianSyncJob:
        job = ObsidianSyncJob(
            vault_id=vault_id,
            status=ObsidianSyncJobStatus.pending,
        )
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_by_id(self, job_id: uuid.UUID) -> ObsidianSyncJob | None:
        return self.db.get(ObsidianSyncJob, job_id)

    def get_latest_for_vault(self, vault_id: uuid.UUID) -> ObsidianSyncJob | None:
        statement = (
            select(ObsidianSyncJob)
            .where(ObsidianSyncJob.vault_id == vault_id)
            .order_by(ObsidianSyncJob.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def get_active_for_vault(self, vault_id: uuid.UUID) -> ObsidianSyncJob | None:
        statement = (
            select(ObsidianSyncJob)
            .where(
                ObsidianSyncJob.vault_id == vault_id,
                ObsidianSyncJob.status.in_(
                    [ObsidianSyncJobStatus.pending, ObsidianSyncJobStatus.processing]
                ),
            )
            .order_by(ObsidianSyncJob.created_at.desc())
            .limit(1)
        )
        return self.db.scalar(statement)

    def update(self, job: ObsidianSyncJob, **fields: object) -> ObsidianSyncJob:
        for field, value in fields.items():
            setattr(job, field, value)
        self.db.commit()
        self.db.refresh(job)
        return job
