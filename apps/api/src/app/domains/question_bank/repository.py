from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.question_bank import QuestionBank


class QuestionBankRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list_by_assessment_slug(self, assessment_slug: str):
        result = await self.session.scalars(
            select(QuestionBank)
            .where(QuestionBank.assessment_version_slug == assessment_slug)
            .order_by(QuestionBank.order_hint.asc(), QuestionBank.question_id.asc())
        )
        return list(result)

    async def list_by_question_ids(self, assessment_slug: str, question_ids: list[str]):
        if not question_ids:
            return []
        result = await self.session.scalars(
            select(QuestionBank).where(
                QuestionBank.assessment_version_slug == assessment_slug,
                QuestionBank.question_id.in_(question_ids),
            )
        )
        return list(result)
