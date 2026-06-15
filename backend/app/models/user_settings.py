import uuid
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import CreatedAtMixin, UpdatedAtMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(Base, CreatedAtMixin, UpdatedAtMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    default_model: Mapped[str] = mapped_column(String(128), nullable=False, default="gpt-4.1-mini")
    temperature: Mapped[float] = mapped_column(Float, nullable=False, default=0.7)
    response_length: Mapped[str] = mapped_column(String(32), nullable=False, default="medium")
    chunk_size: Mapped[int] = mapped_column(Integer, nullable=False, default=512)
    chunk_overlap: Mapped[int] = mapped_column(Integer, nullable=False, default=64)
    auto_index_uploads: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    user: Mapped["User"] = relationship("User", back_populates="settings")
