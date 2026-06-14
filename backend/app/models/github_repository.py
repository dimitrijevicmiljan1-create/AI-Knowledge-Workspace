import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.models.github_connection import GitHubConnection
    from app.models.github_sync_job import GitHubSyncJob
    from app.models.source import Source
    from app.models.workspace import Workspace


class GitHubRepositorySyncStatus(str, enum.Enum):
    pending = "pending"
    syncing = "syncing"
    ready = "ready"
    failed = "failed"


class GitHubRepository(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "github_repositories"
    __table_args__ = (
        UniqueConstraint(
            "connection_id",
            "github_repo_id",
            name="uq_github_repositories_connection_repo",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    connection_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("github_connections.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sources.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    github_repo_id: Mapped[int] = mapped_column(nullable=False, index=True)
    repository_owner: Mapped[str] = mapped_column(String(255), nullable=False)
    repository_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False, default="main")
    last_commit_sha: Mapped[str | None] = mapped_column(String(64), nullable=True)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[GitHubRepositorySyncStatus] = mapped_column(
        Enum(GitHubRepositorySyncStatus, name="github_repository_sync_status", native_enum=False),
        nullable=False,
        default=GitHubRepositorySyncStatus.pending,
    )

    connection: Mapped["GitHubConnection"] = relationship(
        "GitHubConnection",
        back_populates="repositories",
    )
    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="github_repositories")
    source: Mapped["Source"] = relationship("Source", back_populates="github_repository")
    sync_jobs: Mapped[list["GitHubSyncJob"]] = relationship(
        "GitHubSyncJob",
        back_populates="repository",
        cascade="all, delete-orphan",
        order_by="GitHubSyncJob.created_at.desc()",
    )
