from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_catalog import AssessmentCatalog


class AdminAssessmentRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_all(self) -> list[AssessmentCatalog]:
        result = await self.session.execute(select(AssessmentCatalog).order_by(AssessmentCatalog.slug.asc()))
        return list(result.scalars().all())

    async def get_by_slug(self, slug: str) -> Optional[AssessmentCatalog]:
        result = await self.session.execute(select(AssessmentCatalog).where(AssessmentCatalog.slug == slug))
        return result.scalars().first()

    async def create_clone(self, source: AssessmentCatalog, new_slug: str) -> AssessmentCatalog:
        clone = AssessmentCatalog(
            slug=new_slug,
            title=source.title,
            description=source.description,
            target_items_count=source.target_items_count,
            min_items_count=source.min_items_count,
            max_items_count=source.max_items_count,
            expected_duration_min=source.expected_duration_min,
            is_active=False,
            scoring_config_json=dict(source.scoring_config_json or {}),
            question_mix_config_json=dict(source.question_mix_config_json or {}),
            version=(source.version or 1) + 1,
        )
        self.session.add(clone)
        await self.session.flush()
        return clone
