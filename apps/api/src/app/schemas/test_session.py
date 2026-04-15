from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel


class StartAssessmentRequest(BaseModel):
    assessment_slug: Optional[str] = None
    assessment_id: Optional[str] = None
    experiment_mode: Optional[str] = None


class SubmitResponseRequest(BaseModel):
    question_id: str
    payload: dict[str, Any]


class AssessmentSessionResponse(BaseModel):
    session_id: str
    user_id: str
    assessment_id: str
    current_question: int
    completed: bool
    answered_questions: list[str]
