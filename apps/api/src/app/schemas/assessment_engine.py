from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field

EXPRESS_RECOMMENDATION_COUNT = 10
DEEP_RECOMMENDATION_COUNT = 15
DIVERSIFICATION_SHORTAGE_FILL_STRATEGY = "score_order_from_skipped_pool"


class StartAssessmentV2Request(BaseModel):
    assessment_slug: str = Field(pattern="^(express_v1|deep_v1)$")


class StartAssessmentV2Response(BaseModel):
    session_id: str
    assessment_slug: str
    status: str
    total_questions: int
    recommendation_target_count: int


class SubmitAssessmentAnswerRequest(BaseModel):
    question_id: str
    answer: dict[str, Any]


class SubmitAssessmentAnswerResponse(BaseModel):
    session_id: str
    status: str
    answered_questions: int
    total_questions: int


class CompleteAssessmentResponse(BaseModel):
    session_id: str
    result_id: str
    assessment_slug: str
    recommendation_target_count: int
    diversification_shortage_fill_strategy: str


class AssessmentResultResponse(BaseModel):
    result_id: str
    session_id: str
    assessment_slug: str
    status: str
    recommendation_target_count: int
    diversification_shortage_fill_strategy: str
    profile_scores: dict[str, int] = Field(default_factory=dict)
    profile_summary: dict[str, Any] = Field(default_factory=dict)
    top_strengths: list[dict[str, Any]] = Field(default_factory=list)
    work_style: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    next_steps: dict[str, Any] = Field(default_factory=dict)
    confidence: dict[str, Any] = Field(default_factory=dict)
    dimension_evidence: dict[str, Any] = Field(default_factory=dict)
