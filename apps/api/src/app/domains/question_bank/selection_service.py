from app.domains.question_bank.repository import QuestionBankRepository


class DeepQuestionSetNotReadyError(RuntimeError):
    pass


class QuestionSelectionService:
    EXPANSION_MODE = "baseline+expansion_p0_v1"

    def __init__(self, repository: QuestionBankRepository) -> None:
        self.repository = repository

    async def select_for_assessment(self, assessment_slug: str, experiment_mode: str = "baseline") -> list[str]:
        questions = await self.repository.list_by_assessment_slug(assessment_slug)

        if assessment_slug == "deep_v1":
            questions = self._apply_deep_v1_mode(questions, experiment_mode)
            self._validate_deep_v1_questions(questions)

        return [item.question_id for item in questions]

    @classmethod
    def _apply_deep_v1_mode(cls, questions: list, experiment_mode: str) -> list:
        mode = (experiment_mode or "baseline").strip().lower()
        if mode == cls.EXPANSION_MODE:
            return questions
        return [item for item in questions if str(getattr(item, "question_purpose", "") or "") != "expansion_p0_v1"]

    @staticmethod
    def _validate_deep_v1_questions(questions: list) -> None:
        if len(questions) < 40:
            raise DeepQuestionSetNotReadyError(
                "deep_v1 question set is incomplete; express fallback is forbidden"
            )

        required_types = {
            "likert",
            "single_select",
            "situational",
            "multi_select",
            "mini_task",
        }
        present_types = {
            str(getattr(item, "question_type", "") or "")
            for item in questions
        }

        # Compatibility rule: forced_choice is canonicalized into single_select
        # in current import pipeline, so single_select covers both.
        compatibility_present_types = set(present_types)
        if "single_select" in compatibility_present_types:
            compatibility_present_types.add("forced_choice")

        if not required_types.issubset(compatibility_present_types):
            missing = sorted(required_types.difference(compatibility_present_types))
            raise DeepQuestionSetNotReadyError(
                f"deep_v1 question set is not deep-compatible; missing types: {', '.join(missing)}"
            )
