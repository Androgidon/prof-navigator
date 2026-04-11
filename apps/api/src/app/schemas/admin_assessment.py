from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class AssessmentListItemResponse(BaseModel):
    id: str
    slug: str
    title: str
    description: Optional[str]
    target_items_count: int
    min_items_count: int
    max_items_count: int
    expected_duration_min: int
    is_active: bool
    version: int


class AssessmentDetailResponse(AssessmentListItemResponse):
    scoring_config_json: dict[str, Any] = Field(default_factory=dict)
    question_mix_config_json: dict[str, Any] = Field(default_factory=dict)


class AssessmentPatchRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_items_count: Optional[int] = None
    min_items_count: Optional[int] = None
    max_items_count: Optional[int] = None
    expected_duration_min: Optional[int] = None
    is_active: Optional[bool] = None
    scoring_config_json: Optional[dict[str, Any]] = None
    question_mix_config_json: Optional[dict[str, Any]] = None


class CloneAssessmentRequest(BaseModel):
    new_slug: Optional[str] = None


class CloneAssessmentResponse(BaseModel):
    source_slug: str
    draft_slug: str
