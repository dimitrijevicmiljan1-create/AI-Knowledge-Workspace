import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

from sqlalchemy import DateTime, Enum, ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.models.document import Document
    from app.models.workspace import Workspace


class SourceType(str, enum.Enum):
    github = "github"
    obsidian = "obsidian"
    local_files = "local_files"
    manual = "manual"


class SourceStatus(str, enum.Enum):
    pending = "pending"
    ready = "ready"
    syncing = "syncing"
    failed = "failed"


class Source(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "sources"

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
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    source_type: Mapped[SourceType] = mapped_column(
        Enum(SourceType, name="source_type", native_enum=False),
        nullable=False,
    )
    config: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=dict)
    status: Mapped[SourceStatus] = mapped_column(
        Enum(SourceStatus, name="source_status", native_enum=False),
        nullable=False,
        default=SourceStatus.pending,
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="sources")
    documents: Mapped[list["Document"]] = relationship(
        "Document",
        back_populates="source",
        cascade="all, delete-orphan",
    )
