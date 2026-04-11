from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AssessmentSession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessment_sessions"

    user_id: Mapped[Optional[UUID]] = mapped_column(ForeignKey("users.id"), nullable=True)
    assessment_slug: Mapped[str] = mapped_column(ForeignKey("assessment_catalog.slug"), nullable=False)
    status: Mapped[str] = mapped_column(String, nullable=False, default="started")
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    current_question_index: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    question_set_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    answers_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    progress_pct: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    consistency_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    user = relationship("User")
    assessment = relationship("AssessmentCatalog")
