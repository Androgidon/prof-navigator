from __future__ import annotations

from datetime import datetime
from typing import Any

from app.domains.assessment_results.repository import AssessmentResultRepository
from app.domains.result_explanations.service import ResultExplanationService


TEST_TITLES = {
    "express_v1": "Express тест",
    "deep_v1": "Deep тест",
    "full_v1": "Full тест",
}


class AssessmentResultService:
    def __init__(self, repository: AssessmentResultRepository) -> None:
        self.repository = repository
        self.explanations = ResultExplanationService()

    async def get_existing_for_session(self, session_id: str):
        return await self.repository.get_by_session_id(session_id)

    async def create_result(
        self,
        session_id: str,
        assessment_slug: str,
        scoring_output: dict[str, Any],
        recommendations: list[dict[str, Any]],
        consistency_output: dict[str, Any],
    ):
        starter_dataset_limited = scoring_output["starter_dataset_limited"]
        top_strengths = self.explanations.build_top_strengths(
            scoring_output["profile_scores"], starter_dataset_limited
        )
        work_style = self.explanations.build_work_style(
            scoring_output["profile_scores"], starter_dataset_limited
        )
        next_steps = self.explanations.build_next_steps(starter_dataset_limited)

        payload = {
            "profile_scores": scoring_output["profile_scores"],
            "profile_summary": {
                **scoring_output["profile_summary"],
                "preliminary": starter_dataset_limited,
            },
            "top_strengths": top_strengths,
            "work_style": work_style,
            "recommendations": recommendations,
            "next_steps": next_steps,
            "confidence": {
                "score": consistency_output["confidence_score"],
                "level": consistency_output["confidence_level"],
                "starter_dataset_limited": starter_dataset_limited,
                "limited_reason": "Insufficient breadth of answered starter questions."
                if starter_dataset_limited
                else None,
            },
            "dimension_evidence": scoring_output["dimension_evidence"],
        }
        scoring_breakdown = {
            "consistency": consistency_output,
            "fallback_dimensions": scoring_output["fallback_dimensions"],
            "starter_dataset_limited": starter_dataset_limited,
        }
        entity = await self.repository.create(
            session_id=session_id,
            assessment_slug=assessment_slug,
            payload=payload,
            scoring_breakdown_json=scoring_breakdown,
        )
        return entity, payload

    async def list_user_history(self, user_id: str):
        rows = await self.repository.list_for_user(user_id)
        items = []
        for index, (result, session) in enumerate(rows):
            recommendations = list(result.recommendations_json or [])
            top_professions = [
                str(item.get("profession") or item.get("slug") or "")
                for item in recommendations[:3]
                if (item.get("profession") or item.get("slug"))
            ]
            completed_at = session.completed_at or result.created_at
            items.append(
                {
                    "result_id": str(result.id),
                    "assessment_slug": result.assessment_slug,
                    "test_title": TEST_TITLES.get(result.assessment_slug, result.assessment_slug),
                    "completed_at": completed_at,
                    "top_professions": top_professions,
                    "is_latest": index == 0,
                }
            )
        return items

    async def get_result_payload(self, result_id: str, user_id: Optional[str] = None):
        if user_id:
            row = await self.repository.get_for_user(user_id, result_id)
            if not row:
                return None
            entity, session = row
            completed_at = session.completed_at or entity.created_at
        else:
            row = await self.repository.get_with_session(result_id)
            if not row:
                return None
            entity, session = row
            completed_at = session.completed_at or entity.created_at

        return {
            "result_id": str(entity.id),
            "session_id": str(entity.session_id),
            "assessment_slug": entity.assessment_slug,
            "completed_at": completed_at,
            "status": "completed",
            "profile_scores": entity.profile_scores_json,
            "profile_summary": entity.profile_summary_json,
            "top_strengths": entity.top_strengths_json,
            "work_style": entity.work_style_json,
            "recommendations": entity.recommendations_json,
            "next_steps": entity.next_steps_json,
            "confidence": entity.confidence_json,
            "dimension_evidence": entity.scoring_breakdown_json,
        }
