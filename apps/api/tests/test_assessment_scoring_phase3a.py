from types import SimpleNamespace

from app.domains.assessment_scoring.consistency_service import ConsistencyService
from app.domains.assessment_scoring.profession_match_service import BONUS_CAP, ProfessionMatchService
from app.domains.assessment_scoring.profile_scoring_service import ProfileScoringService


def test_profile_scoring_computes_scores_and_fallbacks():
    questions = [
        SimpleNamespace(
            question_id="q1",
            block="interests_and_task_preferences",
            question_type="likert",
            options_json=[],
            weights_by_dimension_json={"technical": 1.0, "analytical": 0.5},
        ),
        SimpleNamespace(
            question_id="q2",
            block="mini_cognitive_tasks",
            question_type="mini_task",
            options_json=[],
            weights_by_dimension_json={"analytical": 1.0, "quantitative": 0.8},
        ),
    ]
    answers = {
        "q1": {"value": 80},
        "q2": {"value": 70},
    }

    out = ProfileScoringService().compute(questions, answers, {"sources": {"self_report": 0.4}})

    assert out["profile_scores"]["technical"] >= 70
    assert out["profile_scores"]["analytical"] >= 50
    assert out["profile_scores"]["practical"] == 50
    assert out["fallback_dimensions"] > 0
    assert out["profile_summary"]["starter_dataset_limited"] is True


def test_consistency_confidence_drops_with_fallbacks():
    dimension_evidence = {
        "analytical": {"evidence_count": 1},
        "technical": {"evidence_count": 0},
        "creative": {"evidence_count": 0},
        "social": {"evidence_count": 0},
        "helping": {"evidence_count": 0},
        "leadership": {"evidence_count": 0},
        "structured": {"evidence_count": 0},
        "exploratory": {"evidence_count": 0},
        "detail": {"evidence_count": 0},
        "verbal": {"evidence_count": 0},
        "quantitative": {"evidence_count": 0},
        "practical": {"evidence_count": 0},
    }
    out = ConsistencyService().compute(
        answers_json={"q1": {"value": 80}},
        dimension_evidence=dimension_evidence,
        total_questions=4,
        fallback_dimensions=11,
    )

    assert out["confidence_level"] in {"low", "medium"}
    assert out["fallback_ratio"] > 0.8


def test_profession_match_bonus_is_capped_and_deterministic():
    matrix = [
        SimpleNamespace(
            profession_id="p1",
            dimension_weights_json={"analytical": 1.0, "technical": 1.0},
            target_profile_json={"analytical": 80, "technical": 80},
            critical_dimensions=["analytical", "technical", "detail"],
            important_subjects=["math"],
            first_steps_template=["step-1"],
            why_fit_template="fit",
        ),
        SimpleNamespace(
            profession_id="p2",
            dimension_weights_json={"analytical": 1.0, "technical": 1.0},
            target_profile_json={"analytical": 79, "technical": 79},
            critical_dimensions=["analytical"],
            important_subjects=["math"],
            first_steps_template=["step-1"],
            why_fit_template="fit",
        ),
    ]
    professions = {
        "p1": SimpleNamespace(slug="a-prof", title="A", cluster="c", summary="s"),
        "p2": SimpleNamespace(slug="b-prof", title="B", cluster="c", summary="s"),
    }

    ranked = ProfessionMatchService().rank(
        profile_scores={
            "analytical": 85,
            "technical": 85,
            "creative": 50,
            "social": 50,
            "helping": 50,
            "leadership": 50,
            "structured": 50,
            "exploratory": 50,
            "detail": 90,
            "verbal": 50,
            "quantitative": 50,
            "practical": 50,
        },
        matrix_rows=matrix,
        profession_by_id=professions,
        target_count=2,
    )

    assert len(ranked) == 2
    assert ranked[0]["match_score"] >= ranked[1]["match_score"]
    assert BONUS_CAP <= 5.0
