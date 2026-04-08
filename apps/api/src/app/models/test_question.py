from __future__ import annotations

from sqlalchemy import Integer, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class TestQuestion(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "test_questions"

    block_id: Mapped[str] = mapped_column(ForeignKey("test_blocks.id"), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    order: Mapped[int] = mapped_column(Integer, nullable=False)
    question_type: Mapped[str] = mapped_column(Text, nullable=False)

    block = relationship("TestBlock", back_populates="questions")
