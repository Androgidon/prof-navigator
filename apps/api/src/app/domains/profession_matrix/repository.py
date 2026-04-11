from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession_matrix import ProfessionMatrix


class ProfessionMatrixRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_version_slug(self, version_slug: str):
        result = await self.session.scalars(
            select(ProfessionMatrix).where(ProfessionMatrix.version_slug == version_slug)
        )
        return list(result)
