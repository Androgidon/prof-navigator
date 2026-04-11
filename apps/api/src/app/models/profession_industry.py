from __future__ import annotations

from sqlalchemy import Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class ProfessionIndustry(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "profession_industries"

    name_ru: Mapped[str] = mapped_column(Text, nullable=False)
    name_uz: Mapped[str] = mapped_column(Text, nullable=False)
    icon: Mapped[str] = mapped_column(Text, nullable=True)
    color: Mapped[str] = mapped_column(Text, nullable=True)

    professions = relationship(
        "Profession",
        back_populates="industry",
        foreign_keys="Profession.industry_id",
        cascade="all, delete",
    )
