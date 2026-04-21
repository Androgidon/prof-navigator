from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.email_verification_code import EmailVerificationCode


class EmailVerificationCodeRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest_active(self, user_id: uuid.UUID) -> Optional[EmailVerificationCode]:
        result = await self._session.execute(
            select(EmailVerificationCode)
            .where(
                EmailVerificationCode.user_id == user_id,
                EmailVerificationCode.consumed_at.is_(None),
            )
            .order_by(EmailVerificationCode.created_at.desc())
            .limit(1)
        )
        return result.scalars().first()

    async def create(
        self,
        user_id: uuid.UUID,
        email: str,
        code_hash: str,
        expires_at: datetime,
        resend_available_at: datetime,
        attempts_left: int,
    ) -> EmailVerificationCode:
        entity = EmailVerificationCode(
            user_id=user_id,
            email=email,
            code_hash=code_hash,
            expires_at=expires_at,
            resend_available_at=resend_available_at,
            attempts_left=attempts_left,
        )
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def consume(self, entity: EmailVerificationCode, consumed_at: datetime) -> None:
        entity.consumed_at = consumed_at
        await self._session.flush()

    async def decrement_attempts(self, entity: EmailVerificationCode) -> None:
        entity.attempts_left = max(0, int(entity.attempts_left) - 1)
        await self._session.flush()

    async def invalidate_active_codes(self, user_id: uuid.UUID, consumed_at: datetime) -> None:
        await self._session.execute(
            update(EmailVerificationCode)
            .where(
                EmailVerificationCode.user_id == user_id,
                EmailVerificationCode.consumed_at.is_(None),
            )
            .values(consumed_at=consumed_at)
        )

    async def delete_expired_or_consumed_before(self, now: datetime, consumed_before: datetime) -> int:
        result = await self._session.execute(
            EmailVerificationCode.__table__.delete().where(
                (EmailVerificationCode.expires_at < now)
                | (
                    EmailVerificationCode.consumed_at.is_not(None)
                    & (EmailVerificationCode.consumed_at < consumed_before)
                )
            )
        )
        return int(result.rowcount or 0)
