from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class QuestionBank(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "question_bank"
    __table_args__ = (
        UniqueConstraint("assessment_version_slug", "question_id", name="uq_question_bank_version_question"),
    )

    question_id: Mapped[str] = mapped_column(String, nullable=False)
    assessment_version_slug: Mapped[str] = mapped_column(String, nullable=False)
    block: Mapped[str] = mapped_column(String, nullable=False)
    subblock: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    question_type: Mapped[str] = mapped_column(String, nullable=False)
    text: Mapped[str] = mapped_column(String, nullable=False)
    options_json: Mapped[list[dict]] = mapped_column(JSONB, nullable=False)
    primary_dimension: Mapped[str] = mapped_column(String, nullable=False)
    secondary_dimensions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    weights_by_dimension_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    consistency_pair_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    difficulty: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    is_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    order_hint: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    status: Mapped[str] = mapped_column(String, nullable=False, default="active")
    question_purpose: Mapped[str] = mapped_column(String, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
