from __future__ import annotations

from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class SubjectGrade(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "subject_grades"

    profile_id: Mapped[str] = mapped_column(ForeignKey("user_profiles.id"), nullable=False)
    subject_id: Mapped[str] = mapped_column(ForeignKey("subjects.id"), nullable=False)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)

    profile = relationship("UserProfile")
    subject = relationship("Subject")
