from __future__ import annotations

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.profession_catalog import ProfessionCatalog
from app.models.profession_matrix import ProfessionMatrix


class AdminProfessionMatrixRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_with_professions(
        self,
        version_slug: Optional[str] = None,
        profession_query: Optional[str] = None,
        cluster: Optional[str] = None,
    ):
        stmt = (
            select(ProfessionMatrix, ProfessionCatalog)
            .join(ProfessionCatalog, ProfessionCatalog.id == ProfessionMatrix.profession_id)
            .order_by(ProfessionCatalog.title.asc())
        )
        if version_slug:
            stmt = stmt.where(ProfessionMatrix.version_slug == version_slug)
        if profession_query:
            like = f"%{profession_query.strip()}%"
            stmt = stmt.where((ProfessionCatalog.slug.ilike(like)) | (ProfessionCatalog.title.ilike(like)))
        if cluster:
            stmt = stmt.where(ProfessionCatalog.cluster == cluster)

        result = await self.session.execute(stmt)
        return list(result.all())

    async def get_with_profession(self, version_slug: str, profession_slug: str):
        result = await self.session.execute(
            select(ProfessionMatrix, ProfessionCatalog)
            .join(ProfessionCatalog, ProfessionCatalog.id == ProfessionMatrix.profession_id)
            .where(
                ProfessionMatrix.version_slug == version_slug,
                ProfessionCatalog.slug == profession_slug,
            )
        )
        return result.first()

    async def get_by_profession_and_version(self, profession_id, version_slug: str) -> Optional[ProfessionMatrix]:
        result = await self.session.execute(
            select(ProfessionMatrix).where(
                ProfessionMatrix.profession_id == profession_id,
                ProfessionMatrix.version_slug == version_slug,
            )
        )
        return result.scalars().first()

    async def create_clone(self, source: ProfessionMatrix, draft_version_slug: str) -> ProfessionMatrix:
        clone = ProfessionMatrix(
            profession_id=source.profession_id,
            version_slug=draft_version_slug,
            target_profile_json=dict(source.target_profile_json or {}),
            dimension_weights_json=dict(source.dimension_weights_json or {}),
            critical_dimensions=list(source.critical_dimensions or []),
            important_subjects=list(source.important_subjects or []),
            hobby_signals=list(source.hobby_signals or []),
            preferred_environments=list(source.preferred_environments or []),
            why_fit_template=source.why_fit_template,
            first_steps_template=list(source.first_steps_template or []),
            notes=source.notes,
            matrix_version=(source.matrix_version or 1) + 1,
        )
        self.session.add(clone)
        await self.session.flush()
        return clone
