from __future__ import annotations

from typing import Optional
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class ProfessionMatrix(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "profession_matrix"
    __table_args__ = (
        UniqueConstraint("profession_id", "version_slug", name="uq_profession_matrix_profession_version"),
    )

    profession_id: Mapped[UUID] = mapped_column(ForeignKey("profession_catalog.id"), nullable=False)
    version_slug: Mapped[str] = mapped_column(String, nullable=False)
    target_profile_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    dimension_weights_json: Mapped[dict] = mapped_column(JSONB, nullable=False)
    critical_dimensions: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    important_subjects: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    hobby_signals: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    preferred_environments: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    why_fit_template: Mapped[str] = mapped_column(String, nullable=False)
    first_steps_template: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    notes: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    matrix_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    profession = relationship("ProfessionCatalog")
