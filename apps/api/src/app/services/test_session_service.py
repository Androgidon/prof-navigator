from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.test_session import TestSession
from app.schemas.test_session import AssessmentSessionResponse, StartAssessmentRequest


class TestSessionService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def start(self, payload: StartAssessmentRequest) -> TestSession:
        test_session = TestSession(
            user_id=payload.user_id,
            test_id=payload.assessment_id,
            current_question=0,
            completed=False,
        )
        self.session.add(test_session)
        await self.session.flush()
        return test_session
