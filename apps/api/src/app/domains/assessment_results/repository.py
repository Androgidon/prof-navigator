from typing import Any, Optional
from uuid import UUID

from sqlalchemy import case, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_result import AssessmentResult
from app.models.assessment_session import AssessmentSession


class AssessmentResultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_session_id(self, session_id: str) -> Optional[AssessmentResult]:
        return await self.session.scalar(
            select(AssessmentResult).where(AssessmentResult.session_id == UUID(session_id))
        )

    async def get_by_result_id(self, result_id: str) -> Optional[AssessmentResult]:
        return await self.session.get(AssessmentResult, UUID(result_id))

    async def create(
        self,
        session_id: str,
        assessment_slug: str,
        payload: dict[str, Any],
        scoring_breakdown_json: dict[str, Any],
    ) -> AssessmentResult:
        entity = AssessmentResult(
            session_id=UUID(session_id),
            assessment_slug=assessment_slug,
            profile_scores_json=payload["profile_scores"],
            profile_summary_json=payload["profile_summary"],
            top_strengths_json=payload["top_strengths"],
            work_style_json=payload["work_style"],
            recommendations_json=payload["recommendations"],
            next_steps_json=payload["next_steps"],
            confidence_json=payload["confidence"],
            scoring_breakdown_json=scoring_breakdown_json,
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def list_for_user(self, user_id: str):
        user_uuid = UUID(user_id)
        completed_sort = case(
            (AssessmentSession.completed_at.is_(None), AssessmentResult.created_at),
            else_=AssessmentSession.completed_at,
        )

        result = await self.session.execute(
            select(AssessmentResult, AssessmentSession)
            .join(AssessmentSession, AssessmentSession.id == AssessmentResult.session_id)
            .where(AssessmentSession.user_id == user_uuid)
            .order_by(completed_sort.desc(), AssessmentResult.created_at.desc())
        )
        return list(result.all())

    async def get_for_user(self, user_id: str, result_id: str):
        user_uuid = UUID(user_id)
        result_uuid = UUID(result_id)
        result = await self.session.execute(
            select(AssessmentResult, AssessmentSession)
            .join(AssessmentSession, AssessmentSession.id == AssessmentResult.session_id)
            .where(
                AssessmentResult.id == result_uuid,
                AssessmentSession.user_id == user_uuid,
            )
        )
        return result.first()

    async def get_with_session(self, result_id: str):
        result_uuid = UUID(result_id)
        result = await self.session.execute(
            select(AssessmentResult, AssessmentSession)
            .join(AssessmentSession, AssessmentSession.id == AssessmentResult.session_id)
            .where(AssessmentResult.id == result_uuid)
        )
        return result.first()
