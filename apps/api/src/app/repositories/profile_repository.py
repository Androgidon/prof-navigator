import uuid
from typing import Any, Dict, Optional, Union

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile


class ProfileRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_user_id(self, user_id: Union[str, uuid.UUID]) -> Optional[UserProfile]:
        result = await self._session.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        )
        return result.scalars().first()

    async def upsert_by_user_id(self, user_id: Union[str, uuid.UUID], payload: Dict[str, Any]) -> UserProfile:
        profile = await self.get_by_user_id(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
            self._session.add(profile)

        for field, value in payload.items():
            setattr(profile, field, value)

        await self._session.flush()
        return profile
