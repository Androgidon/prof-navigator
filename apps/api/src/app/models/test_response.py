from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class TestResponse(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "test_responses"

    session_id: Mapped[str] = mapped_column(ForeignKey("test_sessions.id"), nullable=False)
    question_id: Mapped[str] = mapped_column(ForeignKey("test_questions.id"), nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    session = relationship("TestSession")
    question = relationship("TestQuestion")
