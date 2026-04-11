from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.assessment_session import AssessmentSession


class AssessmentSessionRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        assessment_slug: str,
        question_set_json: list[str],
        user_id: Optional[UUID] = None,
    ) -> AssessmentSession:
        entity = AssessmentSession(
            user_id=user_id,
            assessment_slug=assessment_slug,
            status="started",
            started_at=datetime.now(timezone.utc),
            question_set_json=question_set_json,
            answers_json={},
            progress_pct=0,
            current_question_index=0,
            metadata_json={"starter_dataset_limited": True},
        )
        self.session.add(entity)
        await self.session.flush()
        return entity

    async def get_by_id(self, session_id: str) -> Optional[AssessmentSession]:
        return await self.session.get(AssessmentSession, UUID(session_id))

    async def save_answer(self, entity: AssessmentSession, question_id: str, payload: dict[str, Any]) -> AssessmentSession:
        answers = dict(entity.answers_json or {})
        answers[question_id] = payload
        entity.answers_json = answers
        total = len(entity.question_set_json or [])
        answered = len(answers)
        entity.current_question_index = min(answered, total)
        entity.progress_pct = int((answered / total) * 100) if total else 0
        entity.status = "in_progress" if answered else "started"
        await self.session.flush()
        return entity

    async def mark_completed(
        self,
        entity: AssessmentSession,
        consistency_score: float,
        confidence_score: float,
    ) -> AssessmentSession:
        entity.status = "completed"
        entity.completed_at = datetime.now(timezone.utc)
        entity.consistency_score = consistency_score
        entity.confidence_score = confidence_score
        entity.progress_pct = 100
        entity.current_question_index = len(entity.question_set_json or [])
        await self.session.flush()
        return entity
