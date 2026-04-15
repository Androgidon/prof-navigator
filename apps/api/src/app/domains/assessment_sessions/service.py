from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from app.domains.assessment_catalog.repository import AssessmentCatalogRepository
from app.domains.assessment_sessions.repository import AssessmentSessionRepository
from app.domains.question_bank.repository import QuestionBankRepository
from app.domains.question_bank.selection_service import (
    DeepQuestionSetNotReadyError,
    QuestionSelectionService,
)


class AssessmentSessionService:
    def __init__(
        self,
        catalog_repository: AssessmentCatalogRepository,
        question_repository: QuestionBankRepository,
        session_repository: AssessmentSessionRepository,
    ) -> None:
        self.catalog_repository = catalog_repository
        self.question_repository = question_repository
        self.selection_service = QuestionSelectionService(question_repository)
        self.session_repository = session_repository

    async def start(self, assessment_slug: str, user_id: Optional[str] = None, experiment_mode: str = "baseline"):
        catalog = await self.catalog_repository.get_by_slug(assessment_slug)
        if not catalog:
            return None, None
        question_ids = await self.selection_service.select_for_assessment(assessment_slug, experiment_mode=experiment_mode)
        parsed_user_id = UUID(user_id) if user_id else None
        entity = await self.session_repository.create(
            assessment_slug=assessment_slug,
            question_set_json=question_ids,
            user_id=parsed_user_id,
        )
        return entity, catalog

    async def submit_answer(self, session_id: str, question_id: str, answer: dict[str, Any]):
        entity = await self.session_repository.get_by_id(session_id)
        if not entity:
            return None
        if entity.status == "completed":
            return entity
        if question_id not in (entity.question_set_json or []):
            return None
        return await self.session_repository.save_answer(entity, question_id, answer)
