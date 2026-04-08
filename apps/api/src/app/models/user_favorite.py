from __future__ import annotations

from sqlalchemy import ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserFavorite(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_favorites"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    profession_id: Mapped[str] = mapped_column(ForeignKey("professions.id"), nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=True)

    profession = relationship("Profession")
