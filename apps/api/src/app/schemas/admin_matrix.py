from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field


class MatrixListItemResponse(BaseModel):
    profession_slug: str
    profession_title: str
    cluster: str
    version_slug: str
    completeness_score: int
    validation_status: str


class MatrixDetailResponse(BaseModel):
    profession_slug: str
    profession_title: str
    cluster: str
    version_slug: str
    matrix_version: int
    target_profile_json: dict[str, int] = Field(default_factory=dict)
    dimension_weights_json: dict[str, float] = Field(default_factory=dict)
    critical_dimensions: list[str] = Field(default_factory=list)
    important_subjects: list[str] = Field(default_factory=list)
    hobby_signals: list[str] = Field(default_factory=list)
    preferred_environments: list[str] = Field(default_factory=list)
    why_fit_template: str
    first_steps_template: list[str] = Field(default_factory=list)
    notes: Optional[str] = None


class MatrixPatchRequest(BaseModel):
    target_profile_json: Optional[dict[str, int]] = None
    dimension_weights_json: Optional[dict[str, float]] = None
    critical_dimensions: Optional[list[str]] = None
    important_subjects: Optional[list[str]] = None
    hobby_signals: Optional[list[str]] = None
    preferred_environments: Optional[list[str]] = None
    why_fit_template: Optional[str] = None
    first_steps_template: Optional[list[str]] = None
    notes: Optional[str] = None


class MatrixCloneResponse(BaseModel):
    source_version_slug: str
    draft_version_slug: str
    profession_slug: str


class MatrixPreviewRequest(BaseModel):
    profile_scores: dict[str, int]
    target_profile_json: dict[str, int]
    dimension_weights_json: dict[str, float]
    critical_dimensions: list[str] = Field(default_factory=list)
    cluster: Optional[str] = None


class MatrixPreviewResponse(BaseModel):
    base_similarity: float
    critical_penalty: float
    strong_fit_effect: float
    admissibility_effect: float
    admissible: bool
    final_score: float


class MatrixValidationIssue(BaseModel):
    severity: str
    code: str
    message: str


class MatrixValidationRequest(BaseModel):
    target_profile_json: dict[str, Any]
    dimension_weights_json: dict[str, Any]
    critical_dimensions: list[str] = Field(default_factory=list)
    why_fit_template: str = ""


class MatrixValidationResponse(BaseModel):
    valid: bool
    hard_errors: list[MatrixValidationIssue] = Field(default_factory=list)
    warnings: list[MatrixValidationIssue] = Field(default_factory=list)
    completeness_score: int
