from __future__ import annotations

from typing import Dict, List

from pydantic import BaseModel


class StartAssessmentRequest(BaseModel):
    user_id: str
    assessment_id: str


class SubmitResponseRequest(BaseModel):
    question_id: str
    payload: Dict[str, str]


class AssessmentSessionResponse(BaseModel):
    session_id: str
    user_id: str
    assessment_id: str
    current_question: int
    completed: bool
    answered_questions: List[str]

    class Config:
        orm_mode = True
