from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select

from app.models.profile import UserProfile
from app.repositories.profile_repository import ProfileRepository
from app.schemas.profile import ProfileCreate


class ProfileService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._repo = ProfileRepository(session)

    async def create(self, payload: ProfileCreate) -> UserProfile:
        profile = UserProfile(
            user_id=payload.user_id,
            full_name=payload.full_name,
            birth_date=payload.birth_date,
            country=payload.country,
            region=payload.region,
            city=payload.city,
            language=payload.language,
            grades=payload.grades,
            interests=payload.interests,
        )
        self.session.add(profile)
        await self.session.flush()
        return profile
