import csv
from collections import Counter
from pathlib import Path

SOURCE = (
    Path(__file__).resolve().parents[3]
    / "docs"
    / "ai-context"
    / "forTest"
    / "careerpath-question-bank-template.csv"
)


def _load_express_rows():
    with SOURCE.open("r", encoding="utf-8-sig", newline="") as fp:
        rows = list(csv.DictReader(fp))
    return [row for row in rows if row["assessment_version_slug"] == "express_v1"]


def test_express_question_count_is_24():
    rows = _load_express_rows()
    assert 20 <= len(rows) <= 30
    assert len(rows) == 24


def test_express_block_distribution_matches_blueprint():
    rows = _load_express_rows()
    block_counts = Counter(row["block"] for row in rows)
    assert block_counts == {
        "interests_and_task_preferences": 5,
        "subjects_profile": 4,
        "hobbies_and_activities": 4,
        "work_style_and_environment": 4,
        "behavioral_situations": 4,
        "mini_cognitive_tasks": 3,
    }


def test_express_has_dimension_coverage_and_helping_social_verbal_minimum():
    rows = _load_express_rows()
    primary = Counter(row["primary_dimension"] for row in rows)

    core_dimensions = {
        "analytical",
        "technical",
        "creative",
        "social",
        "helping",
        "structured",
        "verbal",
        "quantitative",
        "practical",
    }

    # Every core dimension has at least 1 primary
    for d in core_dimensions:
        assert primary[d] >= 1, f"{d} has no primary question"

    # Helping/social/verbal each >= 3
    assert primary["helping"] >= 3
    assert primary["social"] >= 3
    assert primary["verbal"] >= 3


def test_express_has_no_duplicate_question_keys():
    rows = _load_express_rows()
    keys = [(row["assessment_version_slug"], row["question_id"]) for row in rows]
    assert len(keys) == len(set(keys))
