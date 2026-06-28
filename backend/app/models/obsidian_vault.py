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
    from app.models.obsidian_sync_job import ObsidianSyncJob
    from app.models.source import Source
    from app.models.workspace import Workspace


class ObsidianVaultSyncStatus(str, enum.Enum):
    pending = "pending"
    syncing = "syncing"
    ready = "ready"
    failed = "failed"


class ObsidianVault(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "obsidian_vaults"
    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "vault_name",
            name="uq_obsidian_vaults_workspace_name",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
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
    vault_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_synced_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sync_status: Mapped[ObsidianVaultSyncStatus] = mapped_column(
        Enum(ObsidianVaultSyncStatus, name="obsidian_vault_sync_status", native_enum=False),
        nullable=False,
        default=ObsidianVaultSyncStatus.pending,
    )

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="obsidian_vaults")
    source: Mapped["Source"] = relationship("Source", back_populates="obsidian_vault")
    sync_jobs: Mapped[list["ObsidianSyncJob"]] = relationship(
        "ObsidianSyncJob",
        back_populates="vault",
        cascade="all, delete-orphan",
        order_by="ObsidianSyncJob.created_at.desc()",
    )
