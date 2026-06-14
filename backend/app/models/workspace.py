import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.models.chat_session import ChatSession
    from app.models.github_repository import GitHubRepository
    from app.models.source import Source
    from app.models.user import User


class Workspace(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "workspaces"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    owner_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    owner: Mapped["User"] = relationship("User", back_populates="workspaces")
    sources: Mapped[list["Source"]] = relationship(
        "Source",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    chat_sessions: Mapped[list["ChatSession"]] = relationship(
        "ChatSession",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
    github_repositories: Mapped[list["GitHubRepository"]] = relationship(
        "GitHubRepository",
        back_populates="workspace",
        cascade="all, delete-orphan",
    )
