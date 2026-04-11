from __future__ import annotations

from typing import Optional

from sqlalchemy import Boolean, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class AssessmentCatalog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "assessment_catalog"

    slug: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    target_items_count: Mapped[int] = mapped_column(Integer, nullable=False)
    min_items_count: Mapped[int] = mapped_column(Integer, nullable=False)
    max_items_count: Mapped[int] = mapped_column(Integer, nullable=False)
    expected_duration_min: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    scoring_config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    question_mix_config_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
