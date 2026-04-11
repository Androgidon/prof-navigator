from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_bank import QuestionBank


class AdminQuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_questions(
        self,
        assessment_slug: Optional[str] = None,
        block: Optional[str] = None,
        question_type: Optional[str] = None,
        status: Optional[str] = None,
        query: Optional[str] = None,
    ) -> list[QuestionBank]:
        stmt = select(QuestionBank)
        if assessment_slug:
            stmt = stmt.where(QuestionBank.assessment_version_slug == assessment_slug)
        if block:
            stmt = stmt.where(QuestionBank.block == block)
        if question_type:
            stmt = stmt.where(QuestionBank.question_type == question_type)
        if status:
            stmt = stmt.where(QuestionBank.status == status)
        if query:
            like = f"%{query.strip()}%"
            stmt = stmt.where((QuestionBank.text.ilike(like)) | (QuestionBank.question_id.ilike(like)))
        stmt = stmt.order_by(
            QuestionBank.assessment_version_slug.asc(),
            QuestionBank.block.asc(),
            QuestionBank.order_hint.asc(),
            QuestionBank.question_id.asc(),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get(self, assessment_slug: str, question_id: str) -> Optional[QuestionBank]:
        result = await self.session.execute(
            select(QuestionBank).where(
                QuestionBank.assessment_version_slug == assessment_slug,
                QuestionBank.question_id == question_id,
            )
        )
        return result.scalars().first()

    async def get_max_order_hint(self, assessment_slug: str, block: str) -> int:
        result = await self.session.execute(
            select(func.max(QuestionBank.order_hint)).where(
                QuestionBank.assessment_version_slug == assessment_slug,
                QuestionBank.block == block,
            )
        )
        value = result.scalar()
        return int(value or 0)

    async def create(self, payload: dict) -> QuestionBank:
        entity = QuestionBank(**payload)
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def list_by_assessment_block(self, assessment_slug: str, block: str) -> list[QuestionBank]:
        result = await self.session.execute(
            select(QuestionBank)
            .where(
                QuestionBank.assessment_version_slug == assessment_slug,
                QuestionBank.block == block,
            )
            .order_by(QuestionBank.order_hint.asc(), QuestionBank.question_id.asc())
        )
        return list(result.scalars().all())

    async def create_clone(self, source: QuestionBank, target_assessment_slug: str) -> QuestionBank:
        clone = QuestionBank(
            question_id=source.question_id,
            assessment_version_slug=target_assessment_slug,
            block=source.block,
            subblock=source.subblock,
            question_type=source.question_type,
            text=source.text,
            options_json=list(source.options_json or []),
            primary_dimension=source.primary_dimension,
            secondary_dimensions=list(source.secondary_dimensions or []),
            weights_by_dimension_json=dict(source.weights_by_dimension_json or {}),
            consistency_pair_id=source.consistency_pair_id,
            difficulty=source.difficulty,
            is_required=source.is_required,
            order_hint=source.order_hint,
            status="draft",
            question_purpose=source.question_purpose,
            notes=source.notes,
        )
        self.session.add(clone)
        await self.session.flush()
        return clone
