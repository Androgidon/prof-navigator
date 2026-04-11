from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_catalog import AssessmentCatalog


class AssessmentCatalogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_slug(self, slug: str):
        return await self.session.scalar(select(AssessmentCatalog).where(AssessmentCatalog.slug == slug))
