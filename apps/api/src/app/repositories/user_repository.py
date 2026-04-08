from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, email: str, hashed_password: str) -> User:
        user = User(email=email, hashed_password=hashed_password)
        self._session.add(user)
        await self._session.flush()
        return user

    async def find_by_email(self, email: str) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.email == email))
        return result.scalars().first()

    async def find_by_id(self, user_id: str) -> Optional[User]:
        result = await self._session.execute(select(User).where(User.id == user_id))
        return result.scalars().first()
