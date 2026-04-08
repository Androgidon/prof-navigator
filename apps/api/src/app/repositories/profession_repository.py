from typing import Iterable

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession import Profession


class ProfessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Iterable[Profession]:
        result = await self._session.execute(select(Profession))
        return result.scalars().all()
