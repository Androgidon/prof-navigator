from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession_catalog import ProfessionCatalog


class ProfessionCatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_ids(self, ids: list):
        if not ids:
            return []
        result = await self.session.scalars(select(ProfessionCatalog).where(ProfessionCatalog.id.in_(ids)))
        return list(result)
