from typing import Iterable, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.profession import Profession
from app.models.profession_catalog import ProfessionCatalog
from app.models.profession_matrix import ProfessionMatrix


class ProfessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_all(self) -> Iterable[Profession]:
        result = await self._session.execute(
            select(Profession)
            .options(selectinload(Profession.industry))
            .order_by(Profession.title_ru.asc())
        )
        return result.scalars().all()

    async def get_by_slug(self, slug: str) -> Optional[Profession]:
        result = await self._session.execute(
            select(Profession)
            .where(Profession.slug == slug)
            .options(selectinload(Profession.industry))
        )
        return result.scalar_one_or_none()

    async def list_active(self) -> list[ProfessionCatalog]:
        result = await self._session.execute(
            select(ProfessionCatalog)
            .where(ProfessionCatalog.status == "active")
            .order_by(ProfessionCatalog.title.asc())
        )
        return list(result.scalars().all())

    async def get_active_by_slug(self, slug: str) -> Optional[ProfessionCatalog]:
        result = await self._session.execute(
            select(ProfessionCatalog).where(
                ProfessionCatalog.slug == slug,
                ProfessionCatalog.status == "active",
            )
        )
        return result.scalars().first()

    async def get_matrix(self, profession_id, version_slug: str = "matrix_v1") -> Optional[ProfessionMatrix]:
        result = await self._session.execute(
            select(ProfessionMatrix).where(
                ProfessionMatrix.profession_id == profession_id,
                ProfessionMatrix.version_slug == version_slug,
            )
        )
        return result.scalars().first()

    async def list_related_by_cluster(self, cluster: str, exclude_slug: str, limit: int = 4) -> list[ProfessionCatalog]:
        result = await self._session.execute(
            select(ProfessionCatalog)
            .where(
                ProfessionCatalog.status == "active",
                ProfessionCatalog.cluster == cluster,
                ProfessionCatalog.slug != exclude_slug,
            )
            .order_by(ProfessionCatalog.title.asc())
            .limit(limit)
        )
        return list(result.scalars().all())
