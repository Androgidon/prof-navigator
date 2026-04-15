from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession_catalog import ProfessionCatalog


class AdminProfessionCatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _apply_filters(
        self,
        stmt,
        query: Optional[str] = None,
        search: Optional[str] = None,
        cluster: Optional[str] = None,
        status: Optional[str] = None,
    ):
        effective_query = (query or search or "").strip()
        if effective_query:
            like = f"%{effective_query}%"
            stmt = stmt.where((ProfessionCatalog.slug.ilike(like)) | (ProfessionCatalog.title.ilike(like)))
        if cluster:
            stmt = stmt.where(ProfessionCatalog.cluster == cluster)
        if status:
            stmt = stmt.where(ProfessionCatalog.status == status)
        return stmt

    async def list_all(
        self,
        query: Optional[str] = None,
        search: Optional[str] = None,
        cluster: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[ProfessionCatalog]:
        stmt = self._apply_filters(
            select(ProfessionCatalog),
            query=query,
            search=search,
            cluster=cluster,
            status=status,
        )
        stmt = stmt.order_by(ProfessionCatalog.title.asc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_paginated(
        self,
        page: int,
        page_size: int,
        query: Optional[str] = None,
        search: Optional[str] = None,
        cluster: Optional[str] = None,
        status: Optional[str] = None,
    ) -> tuple[list[ProfessionCatalog], int]:
        filtered_stmt = self._apply_filters(
            select(ProfessionCatalog),
            query=query,
            search=search,
            cluster=cluster,
            status=status,
        )

        count_stmt = self._apply_filters(
            select(func.count()).select_from(ProfessionCatalog),
            query=query,
            search=search,
            cluster=cluster,
            status=status,
        )
        total = int((await self.session.execute(count_stmt)).scalar_one() or 0)

        offset = (page - 1) * page_size
        rows_stmt = filtered_stmt.order_by(ProfessionCatalog.title.asc()).offset(offset).limit(page_size)
        result = await self.session.execute(rows_stmt)
        return list(result.scalars().all()), total

    async def get_by_slug(self, slug: str) -> Optional[ProfessionCatalog]:
        result = await self.session.execute(select(ProfessionCatalog).where(ProfessionCatalog.slug == slug))
        return result.scalars().first()

    async def create(self, payload: dict) -> ProfessionCatalog:
        entity = ProfessionCatalog(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity
