from __future__ import annotations

from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_bank import QuestionBank


class AdminQuestionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    def _apply_filters(
        self,
        stmt,
        assessment_slug: Optional[str] = None,
        block: Optional[str] = None,
        question_type: Optional[str] = None,
        status: Optional[str] = None,
        question_purpose: Optional[str] = None,
        experiment_mode: Optional[str] = None,
        experiment_tag: Optional[str] = None,
        query: Optional[str] = None,
    ):
        if assessment_slug:
            stmt = stmt.where(QuestionBank.assessment_version_slug == assessment_slug)
        if block:
            stmt = stmt.where(QuestionBank.block == block)
        if question_type:
            stmt = stmt.where(QuestionBank.question_type == question_type)
        if status:
            stmt = stmt.where(QuestionBank.status == status)
        if question_purpose:
            stmt = stmt.where(QuestionBank.question_purpose == question_purpose)
        if experiment_mode:
            stmt = stmt.where(QuestionBank.experiment_mode == experiment_mode)
        if experiment_tag:
            stmt = stmt.where(QuestionBank.experiment_tag == experiment_tag)
        if query:
            like = f"%{query.strip()}%"
            stmt = stmt.where((QuestionBank.text.ilike(like)) | (QuestionBank.question_id.ilike(like)))
        return stmt

    async def list_questions(
        self,
        assessment_slug: Optional[str] = None,
        block: Optional[str] = None,
        question_type: Optional[str] = None,
        status: Optional[str] = None,
        question_purpose: Optional[str] = None,
        experiment_mode: Optional[str] = None,
        experiment_tag: Optional[str] = None,
        query: Optional[str] = None,
    ) -> list[QuestionBank]:
        stmt = self._apply_filters(
            select(QuestionBank),
            assessment_slug=assessment_slug,
            block=block,
            question_type=question_type,
            status=status,
            question_purpose=question_purpose,
            experiment_mode=experiment_mode,
            experiment_tag=experiment_tag,
            query=query,
        )
        stmt = stmt.order_by(
            QuestionBank.assessment_version_slug.asc(),
            QuestionBank.block.asc(),
            QuestionBank.order_hint.asc(),
            QuestionBank.question_id.asc(),
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_questions_paginated(
        self,
        page: int,
        page_size: int,
        assessment_slug: Optional[str] = None,
        block: Optional[str] = None,
        question_type: Optional[str] = None,
        status: Optional[str] = None,
        question_purpose: Optional[str] = None,
        experiment_mode: Optional[str] = None,
        experiment_tag: Optional[str] = None,
        query: Optional[str] = None,
    ) -> tuple[list[QuestionBank], int]:
        filtered_stmt = self._apply_filters(
            select(QuestionBank),
            assessment_slug=assessment_slug,
            block=block,
            question_type=question_type,
            status=status,
            question_purpose=question_purpose,
            experiment_mode=experiment_mode,
            experiment_tag=experiment_tag,
            query=query,
        )
        count_stmt = self._apply_filters(
            select(func.count()).select_from(QuestionBank),
            assessment_slug=assessment_slug,
            block=block,
            question_type=question_type,
            status=status,
            question_purpose=question_purpose,
            experiment_mode=experiment_mode,
            experiment_tag=experiment_tag,
            query=query,
        )
        total = int((await self.session.execute(count_stmt)).scalar_one() or 0)
        offset = (page - 1) * page_size
        rows_stmt = filtered_stmt.order_by(
            QuestionBank.assessment_version_slug.asc(),
            QuestionBank.block.asc(),
            QuestionBank.order_hint.asc(),
            QuestionBank.question_id.asc(),
        ).offset(offset).limit(page_size)
        result = await self.session.execute(rows_stmt)
        return list(result.scalars().all()), total

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

    async def get_summary_counts(self, assessment_slug: Optional[str] = None) -> dict[str, int]:
        stmt = select(QuestionBank)
        if assessment_slug:
            stmt = stmt.where(QuestionBank.assessment_version_slug == assessment_slug)
        result = await self.session.execute(stmt)
        rows = list(result.scalars().all())

        def is_experimental(item: QuestionBank) -> bool:
            mode = (item.experiment_mode or "").strip().lower()
            if mode and mode != "baseline":
                return True
            purpose = (item.question_purpose or "").strip().lower()
            return purpose.startswith("expansion_") or purpose == "expansion_p0_v1"

        total = len(rows)
        active_baseline = 0
        active_experimental = 0
        inactive_or_draft = 0

        for item in rows:
            status = (item.status or "").strip().lower()
            if status == "active":
                if getattr(item, "active_in_scoring", True):
                    if is_experimental(item):
                        active_experimental += 1
                    else:
                        active_baseline += 1
                else:
                    inactive_or_draft += 1
            else:
                inactive_or_draft += 1

        return {
            "total_questions": total,
            "active_baseline": active_baseline,
            "active_experimental": active_experimental,
            "inactive_or_draft": inactive_or_draft,
        }

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
            active_in_scoring=getattr(source, "active_in_scoring", True),
            experiment_tag=getattr(source, "experiment_tag", None),
            experiment_mode=getattr(source, "experiment_mode", None),
            boundary_metadata_json=getattr(source, "boundary_metadata_json", None),
            notes=source.notes,
        )
        self.session.add(clone)
        await self.session.flush()
        return clone
