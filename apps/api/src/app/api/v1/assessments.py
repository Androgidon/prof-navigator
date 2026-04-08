from fastapi import APIRouter, Depends

from app.api.dependencies import get_session
from app.schemas.test_session import StartAssessmentRequest, AssessmentSessionResponse
from app.services.test_session_service import TestSessionService

router = APIRouter()


@router.post("/start", response_model=AssessmentSessionResponse)
async def start(payload: StartAssessmentRequest, session=Depends(get_session)) -> AssessmentSessionResponse:
    service = TestSessionService(session)
    test_session = await service.start(payload)
    return AssessmentSessionResponse(
        session_id=str(test_session.id),
        user_id=str(test_session.user_id),
        assessment_id=str(test_session.test_id),
        current_question=test_session.current_question,
        completed=test_session.completed,
        answered_questions=[],
    )
