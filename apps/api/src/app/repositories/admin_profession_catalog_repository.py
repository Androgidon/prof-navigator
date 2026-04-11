from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession_catalog import ProfessionCatalog


class AdminProfessionCatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(
        self,
        query: Optional[str] = None,
        cluster: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[ProfessionCatalog]:
        stmt = select(ProfessionCatalog)
        if query:
            like = f"%{query.strip()}%"
            stmt = stmt.where((ProfessionCatalog.slug.ilike(like)) | (ProfessionCatalog.title.ilike(like)))
        if cluster:
            stmt = stmt.where(ProfessionCatalog.cluster == cluster)
        if status:
            stmt = stmt.where(ProfessionCatalog.status == status)
        stmt = stmt.order_by(ProfessionCatalog.title.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[ProfessionCatalog]:
        result = await self.session.execute(select(ProfessionCatalog).where(ProfessionCatalog.slug == slug))
        return result.scalars().first()

    async def create(self, payload: dict) -> ProfessionCatalog:
        entity = ProfessionCatalog(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity
