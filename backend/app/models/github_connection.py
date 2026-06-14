import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.models.github_repository import GitHubRepository
    from app.models.user import User


class GitHubConnection(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "github_connections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    github_user_id: Mapped[int] = mapped_column(nullable=False)
    github_username: Mapped[str] = mapped_column(String(255), nullable=False)
    access_token_encrypted: Mapped[str] = mapped_column(Text, nullable=False)
    connected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="github_connection")
    repositories: Mapped[list["GitHubRepository"]] = relationship(
        "GitHubRepository",
        back_populates="connection",
        cascade="all, delete-orphan",
    )
