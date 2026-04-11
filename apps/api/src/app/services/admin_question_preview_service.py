from __future__ import annotations

from typing import Any

from app.domains.assessment_scoring.profile_scoring_service import ProfileScoringService


class _PreviewQuestion:
    def __init__(self, question_type: str, options_json: list[dict[str, Any]], weights_by_dimension_json: dict[str, Any]):
        self.question_type = question_type
        self.options_json = options_json
        self.weights_by_dimension_json = weights_by_dimension_json


class AdminQuestionPreviewService:
    def build_signals(
        self,
        question_type: str,
        options_json: list[dict[str, Any]],
        weights_by_dimension_json: dict[str, Any],
        answer: dict[str, Any],
    ) -> dict[str, dict[str, float]]:
        scorer = ProfileScoringService()
        question = _PreviewQuestion(
            question_type=question_type,
            options_json=options_json,
            weights_by_dimension_json=weights_by_dimension_json,
        )
        raw = scorer._extract_dimension_signals(question, answer)
        return {
            key: {
                "score": float(value[0]),
                "relevance": float(value[1]),
            }
            for key, value in raw.items()
        }
