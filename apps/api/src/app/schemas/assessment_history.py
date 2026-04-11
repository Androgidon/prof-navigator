from __future__ import annotations

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class AssessmentHistoryItemResponse(BaseModel):
    result_id: str
    assessment_slug: str
    test_title: str
    completed_at: datetime
    top_professions: list[str] = Field(default_factory=list)
    is_latest: bool


class AssessmentHistoryResponse(BaseModel):
    items: list[AssessmentHistoryItemResponse] = Field(default_factory=list)


class AssessmentResultDetailResponse(BaseModel):
    result_id: str
    assessment_slug: str
    completed_at: Optional[datetime] = None
    profile_summary: dict[str, Any] = Field(default_factory=dict)
    top_strengths: list[dict[str, Any]] = Field(default_factory=list)
    work_style: dict[str, Any] = Field(default_factory=dict)
    recommendations: list[dict[str, Any]] = Field(default_factory=list)
    next_steps: dict[str, Any] = Field(default_factory=dict)
    confidence: dict[str, Any] = Field(default_factory=dict)
    dimension_evidence: dict[str, Any] = Field(default_factory=dict)
