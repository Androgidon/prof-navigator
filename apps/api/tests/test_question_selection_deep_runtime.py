from types import SimpleNamespace

import pytest

from app.domains.question_bank.selection_service import (
    DeepQuestionSetNotReadyError,
    QuestionSelectionService,
)


class StubQuestionBankRepository:
    def __init__(self, payload_by_slug: dict[str, list[SimpleNamespace]]) -> None:
        self.payload_by_slug = payload_by_slug
        self.calls: list[str] = []

    async def list_by_assessment_slug(self, assessment_slug: str):
        self.calls.append(assessment_slug)
        return self.payload_by_slug.get(assessment_slug, [])


def _question(i: int, qtype: str, question_purpose: str = "deep_core_signal") -> SimpleNamespace:
    return SimpleNamespace(question_id=f"deep_q_{i:02d}", question_type=qtype, question_purpose=question_purpose)


@pytest.mark.anyio
async def test_deep_selection_uses_only_deep_question_set_when_compatible():
    deep_types = ["likert", "forced_choice", "single_select", "situational", "multi_select", "mini_task"]
    deep_questions = [_question(i, deep_types[i % len(deep_types)]) for i in range(1, 41)]
    repo = StubQuestionBankRepository(
        {
            "deep_v1": deep_questions,
            "express_v1": [_question(i, "likert") for i in range(1, 25)],
        }
    )

    selected = await QuestionSelectionService(repo).select_for_assessment("deep_v1", experiment_mode="baseline")

    assert len(selected) == 40
    assert selected[0] == "deep_q_01"
    assert repo.calls == ["deep_v1"]


@pytest.mark.anyio
async def test_deep_selection_fails_when_deep_question_set_is_incomplete():
    repo = StubQuestionBankRepository({"deep_v1": [_question(i, "likert") for i in range(1, 30)]})

    with pytest.raises(DeepQuestionSetNotReadyError):
        await QuestionSelectionService(repo).select_for_assessment("deep_v1")


@pytest.mark.anyio
async def test_deep_selection_fails_when_required_types_missing():
    deep_questions = [_question(i, "likert") for i in range(1, 41)]
    repo = StubQuestionBankRepository({"deep_v1": deep_questions})

    with pytest.raises(DeepQuestionSetNotReadyError) as exc:
        await QuestionSelectionService(repo).select_for_assessment("deep_v1", experiment_mode="baseline")

    assert "missing types" in str(exc.value)


@pytest.mark.anyio
async def test_deep_selection_excludes_expansion_questions_in_baseline_mode():
    deep_types = ["likert", "single_select", "situational", "multi_select", "mini_task"]
    core_questions = [_question(i, deep_types[i % len(deep_types)], "deep_core_signal") for i in range(1, 41)]
    expansion_questions = [_question(i + 100, "situational", "expansion_p0_v1") for i in range(1, 5)]
    repo = StubQuestionBankRepository({"deep_v1": core_questions + expansion_questions})

    selected = await QuestionSelectionService(repo).select_for_assessment("deep_v1", experiment_mode="baseline")

    assert len(selected) == 40
    assert {"deep_q_101", "deep_q_102", "deep_q_103", "deep_q_104"}.isdisjoint(set(selected))


@pytest.mark.anyio
async def test_deep_selection_includes_expansion_questions_in_expansion_mode():
    deep_types = ["likert", "single_select", "situational", "multi_select", "mini_task"]
    core_questions = [_question(i, deep_types[i % len(deep_types)], "deep_core_signal") for i in range(1, 41)]
    expansion_questions = [_question(i + 100, "situational", "expansion_p0_v1") for i in range(1, 5)]
    repo = StubQuestionBankRepository({"deep_v1": core_questions + expansion_questions})

    selected = await QuestionSelectionService(repo).select_for_assessment("deep_v1", experiment_mode="baseline+expansion_p0_v1")

    assert len(selected) == 44
    assert {"deep_q_101", "deep_q_102", "deep_q_103", "deep_q_104"}.issubset(set(selected))
