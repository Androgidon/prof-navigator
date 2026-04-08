import uuid
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.refresh_token import RefreshToken


class RefreshTokenRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(
        self,
        *,
        user_id: str,
        token_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        refresh = RefreshToken(
            user_id=user_id,
            token_id=token_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self._session.add(refresh)
        await self._session.flush()
        return refresh

    async def find_by_jti(self, jti: str) -> Optional[RefreshToken]:
        try:
            token_uuid = uuid.UUID(jti)
        except ValueError:
            return None
        result = await self._session.execute(
            select(RefreshToken).where(RefreshToken.token_id == token_uuid)
        )
        return result.scalars().first()

    async def revoke(self, refresh: RefreshToken) -> None:
        refresh.revoked = True
        await self._session.flush()
