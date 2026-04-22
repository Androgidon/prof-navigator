import uuid
from typing import Dict, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profile import UserProfile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreate, ProfileUpdate


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = ProfileRepository(session)

    @staticmethod
    def _normalize_user_id(user_id: Union[str, uuid.UUID]) -> uuid.UUID:
        if isinstance(user_id, uuid.UUID):
            return user_id
        return uuid.UUID(user_id)

    async def create(self, payload: ProfileCreate) -> UserProfile:
        profile = UserProfile(
            user_id=payload.user_id,
            full_name=payload.full_name,
            birth_date=payload.birth_date,
            country=payload.country,
            region=payload.region,
            city=payload.city,
            school=payload.school,
            phone=payload.phone,
            gender=payload.gender,
            language=payload.language,
            grades=payload.grades,
            interests=payload.interests,
        )
        self.session.add(profile)
        await self.session.flush()
        return profile

    async def get_for_user(self, user_id: Union[str, uuid.UUID]) -> Optional[UserProfile]:
        return await self._repo.get_by_user_id(self._normalize_user_id(user_id))

    async def upsert_for_user(self, user_id: Union[str, uuid.UUID], payload: ProfileUpdate) -> UserProfile:
        update_data: Dict[str, object] = payload.model_dump(exclude_unset=True)
        return await self._repo.upsert_by_user_id(
            user_id=self._normalize_user_id(user_id), payload=update_data
        )
