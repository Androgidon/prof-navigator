from __future__ import annotations

from sqlalchemy import Boolean, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class TestSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "test_sessions"

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    test_id: Mapped[str] = mapped_column(ForeignKey("assessments.id"), nullable=False)
    current_question: Mapped[int] = mapped_column(Integer, default=0)
    completed: Mapped[bool] = mapped_column(Boolean, default=False)

    user = relationship("User")
    test = relationship("Assessment")
