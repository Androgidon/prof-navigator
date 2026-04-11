from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator


QUESTION_TYPES_REQUIRING_OPTIONS = {
    "forced_choice",
    "situational",
    "single_select",
    "multi_select",
    "multi_select_or_ranking",
}


class QuestionListItemResponse(BaseModel):
    id: str
    assessment_version_slug: str
    question_id: str
    block: str
    subblock: Optional[str]
    question_type: str
    text: str
    primary_dimension: str
    secondary_dimensions: list[str] = Field(default_factory=list)
    order_hint: int
    status: str


class QuestionDetailResponse(QuestionListItemResponse):
    options_json: list[dict[str, Any]] = Field(default_factory=list)
    weights_by_dimension_json: dict[str, Any] = Field(default_factory=dict)
    consistency_pair_id: Optional[str] = None
    difficulty: Optional[str] = None
    is_required: bool
    question_purpose: str
    notes: Optional[str] = None


class QuestionCreateRequest(BaseModel):
    assessment_version_slug: str
    question_id: str
    block: str
    question_type: str
    text: str
    primary_dimension: str
    question_purpose: str
    options_json: Optional[list[dict[str, Any]]] = None
    weights_by_dimension_json: dict[str, Any]
    subblock: Optional[str] = None
    secondary_dimensions: list[str] = Field(default_factory=list)
    consistency_pair_id: Optional[str] = None
    difficulty: Optional[str] = None
    is_required: bool = True
    notes: Optional[str] = None
    status: str = "draft"
    order_hint: Optional[int] = None

    @model_validator(mode="after")
    def validate_required(self):
        if self.question_type in QUESTION_TYPES_REQUIRING_OPTIONS:
            if not self.options_json or len(self.options_json) == 0:
                raise ValueError("options_json is required for selected question_type")
        if self.question_type == "likert" and self.options_json is None:
            self.options_json = [
                {"key": "1", "label": "Совсем не про меня"},
                {"key": "2", "label": "Скорее не про меня"},
                {"key": "3", "label": "Иногда"},
                {"key": "4", "label": "Скорее про меня"},
                {"key": "5", "label": "Полностью про меня"},
            ]
        weight = self.weights_by_dimension_json.get(self.primary_dimension)
        if not isinstance(weight, (int, float)):
            raise ValueError("weights_by_dimension_json must include numeric primary_dimension weight")
        return self


class QuestionPatchRequest(BaseModel):
    block: Optional[str] = None
    subblock: Optional[str] = None
    question_type: Optional[str] = None
    text: Optional[str] = None
    options_json: Optional[list[dict[str, Any]]] = None
    primary_dimension: Optional[str] = None
    secondary_dimensions: Optional[list[str]] = None
    weights_by_dimension_json: Optional[dict[str, Any]] = None
    consistency_pair_id: Optional[str] = None
    difficulty: Optional[str] = None
    is_required: Optional[bool] = None
    order_hint: Optional[int] = None
    status: Optional[str] = None
    question_purpose: Optional[str] = None
    notes: Optional[str] = None


class CloneQuestionRequest(BaseModel):
    target_assessment_version_slug: str


class ReorderItem(BaseModel):
    question_id: str
    order_hint: int


class QuestionReorderRequest(BaseModel):
    assessment_version_slug: str
    block: str
    items: Optional[list[ReorderItem]] = None
    ordered_question_ids: Optional[list[str]] = None

    @model_validator(mode="after")
    def validate_payload(self):
        has_items = bool(self.items)
        has_ordered = bool(self.ordered_question_ids)
        if has_items == has_ordered:
            raise ValueError("Provide either items or ordered_question_ids")
        return self


class QuestionReorderResponse(BaseModel):
    assessment_version_slug: str
    block: str
    updated: int


class PreviewSignalRequest(BaseModel):
    question_type: str
    options_json: list[dict[str, Any]] = Field(default_factory=list)
    weights_by_dimension_json: dict[str, Any] = Field(default_factory=dict)
    answer: dict[str, Any] = Field(default_factory=dict)


class PreviewSignalResponse(BaseModel):
    signals: dict[str, dict[str, float]] = Field(default_factory=dict)
    notes: list[str] = Field(default_factory=list)
