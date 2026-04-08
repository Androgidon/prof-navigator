from __future__ import annotations

from sqlalchemy import JSON, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDMixin, TimestampMixin


class Recommendation(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "recommendations"

    user_profile_id: Mapped[str] = mapped_column(
        ForeignKey("user_profiles.id"), nullable=False
    )
    profession_id: Mapped[str] = mapped_column(
        ForeignKey("professions.id"), nullable=False
    )
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    explanatory_factors: Mapped[dict] = mapped_column(JSON, nullable=True)

    profile = relationship("UserProfile")
    profession = relationship("Profession")
