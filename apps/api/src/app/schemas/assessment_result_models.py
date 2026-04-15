from __future__ import annotations

from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


FitBand = Literal["high", "medium"]
ConfidenceLevel = Literal["low", "medium", "high"]
CtaAction = Literal["open_full_offer", "start_full_test", "compare_paths"]
AlternativePivotType = Literal[
    "more_communication",
    "more_practical",
    "more_structured",
    "more_creative",
    "more_analytical",
]


class ProfileTypeResponse(BaseModel):
    primary_family: str
    secondary_modifier: Optional[str] = None
    summary: str


class TopStrengthResponse(BaseModel):
    dimension: str
    score: float
    explanation: str


class ExpressExampleProfessionResponse(BaseModel):
    profession_id: str
    profession_slug: str
    title: str
    family_id: str
    family_title: str
    rationale_tag: Optional[str] = None


class ExpressDirectionResponse(BaseModel):
    rank: int
    direction_id: str
    direction_slug: str
    title: str
    direction_score: Optional[float] = None
    fit_band: FitBand
    why_direction: str
    example_professions: list[ExpressExampleProfessionResponse] = Field(default_factory=list)


class ResultConfidenceResponse(BaseModel):
    score: float
    level: ConfidenceLevel
    user_message: str


class ExpressCtaResponse(BaseModel):
    target_action: CtaAction
    target_url: Optional[str] = None
    title: str
    text: str


class ExpressResultResponse(BaseModel):
    result_id: str
    assessment_slug: str
    payload_version: Literal["express_result_v1"]
    completed_at: Optional[datetime] = None
    profile_type: ProfileTypeResponse
    top_strengths: list[TopStrengthResponse] = Field(default_factory=list)
    top_directions: list[ExpressDirectionResponse] = Field(default_factory=list)
    next_steps_school_level: list[str] = Field(default_factory=list)
    confidence: ResultConfidenceResponse
    monetization_cta: ExpressCtaResponse


class FullDirectionResponse(BaseModel):
    rank: int
    direction_id: str
    direction_slug: str
    title: str
    direction_score: Optional[float] = None
    why_direction: str


class FullProfessionResponse(BaseModel):
    rank: int
    profession_id: str
    profession_slug: str
    title: str
    family_id: str
    family_title: str
    direction_id: str
    direction_title: str
    relevance_score: float
    relevance_level: Literal["high", "medium"]
    why_fit: str
    growth_recommendations: list[str] = Field(default_factory=list)


class AlternativeProfessionResponse(BaseModel):
    profession_slug: str
    title: str
    reason: str


class FullAlternativeBlockResponse(BaseModel):
    pivot_type: AlternativePivotType
    title: str
    explanation: str
    professions: list[AlternativeProfessionResponse] = Field(default_factory=list)


class DevelopmentPlanResponse(BaseModel):
    days_30: list[str] = Field(default_factory=list)
    days_90: list[str] = Field(default_factory=list)
    days_180: list[str] = Field(default_factory=list)


class OverallConfidenceResponse(BaseModel):
    score: float
    level: ConfidenceLevel
    notes: list[str] = Field(default_factory=list)


class FullResultResponse(BaseModel):
    result_id: str
    assessment_slug: str
    payload_version: Literal["full_result_v1"]
    completed_at: Optional[datetime] = None
    profile_type: ProfileTypeResponse
    top_strengths: list[TopStrengthResponse] = Field(default_factory=list)
    top_directions: list[FullDirectionResponse] = Field(default_factory=list)
    top_professions: list[FullProfessionResponse] = Field(default_factory=list)
    alternatives: list[FullAlternativeBlockResponse] = Field(default_factory=list)
    development_plan: DevelopmentPlanResponse
    overall_confidence: OverallConfidenceResponse
