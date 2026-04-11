from __future__ import annotations

from uuid import UUID as UUIDType

from sqlalchemy import JSON, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Profession(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "professions"

    slug: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    title_ru: Mapped[str] = mapped_column(Text, nullable=False)
    title_uz: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=True)
    profession_vector: Mapped[dict] = mapped_column(JSON, nullable=True)
    start_now_steps: Mapped[list] = mapped_column(JSON, nullable=True)
    important_subjects: Mapped[list] = mapped_column(JSON, nullable=True)
    industry_id: Mapped[UUIDType] = mapped_column(
        UUID(as_uuid=True), ForeignKey("profession_industries.id"), nullable=False
    )

    industry = relationship("ProfessionIndustry", back_populates="professions")
