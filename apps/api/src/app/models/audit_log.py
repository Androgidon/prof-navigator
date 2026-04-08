from __future__ import annotations

from sqlalchemy import JSON, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class AdminAuditLog(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "admin_audit_logs"

    actor_id: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    metadata: Mapped[dict] = mapped_column(JSON, nullable=True)
