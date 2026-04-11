from __future__ import annotations

from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class AssessmentResult(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessment_results"

    session_id: Mapped[UUID] = mapped_column(ForeignKey("assessment_sessions.id"), nullable=False, unique=True)
    assessment_slug: Mapped[str] = mapped_column(String, nullable=False)
    profile_scores_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    profile_summary_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    top_strengths_json: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    work_style_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    recommendations_json: Mapped[list[dict]] = mapped_column(JSONB, nullable=False, default=list)
    next_steps_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    confidence_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    scoring_breakdown_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)

    session = relationship("AssessmentSession")
