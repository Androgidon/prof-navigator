from app.domains.question_bank.repository import QuestionBankRepository


class QuestionSelectionService:
    def __init__(self, repository: QuestionBankRepository) -> None:
        self.repository = repository

    async def select_for_assessment(self, assessment_slug: str) -> list[str]:
        questions = await self.repository.list_by_assessment_slug(assessment_slug)
        return [item.question_id for item in questions]
