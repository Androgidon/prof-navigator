from pathlib import Path

import pytest

from app.loaders.assessment_seed_config import ASSESSMENT_CATALOG_SEED
from app.loaders.assessment_seed_loader import AssessmentSeedLoader, SeedValidationError


REQUIRED_FILES = [
    "assessment-engine-prd.md",
    "careerpath-100-professions.csv",
    "careerpath-profession-matrix-filled.csv",
    "careerpath-question-bank-blueprint.md",
    "careerpath-question-bank-template.csv",
]


def test_seed_loader_validates_required_files(tmp_path: Path):
    for name in REQUIRED_FILES:
        (tmp_path / name).write_text("ok", encoding="utf-8")

    loader = AssessmentSeedLoader(root=tmp_path)
    resolved = loader.validate_paths()

    assert set(resolved.keys()) == {
        "assessment_prd",
        "profession_catalog",
        "profession_matrix",
        "question_blueprint",
        "question_template",
    }


def test_seed_loader_raises_on_missing_files(tmp_path: Path):
    loader = AssessmentSeedLoader(root=tmp_path)

    with pytest.raises(FileNotFoundError):
        loader.validate_paths()


def test_assessment_catalog_seed_has_two_versions():
    slugs = {item["slug"] for item in ASSESSMENT_CATALOG_SEED}

    assert slugs == {"express_v1", "deep_v1"}


def test_question_loader_raises_on_malformed_json(tmp_path: Path):
    question_csv = tmp_path / "careerpath-question-bank-template.csv"
    question_csv.write_text(
        "question_id,assessment_version_slug,block,subblock,question_type,text,options_json,primary_dimension,secondary_dimensions,weights_by_dimension_json,consistency_pair_id,difficulty,is_required,order_hint,status,question_purpose,notes\n"
        "q1,express_v1,b,s,likert,text,not-json,technical,analytical,{\"technical\":1.0},,,true,1,active,purpose,\n",
        encoding="utf-8",
    )

    loader = AssessmentSeedLoader(root=tmp_path)

    with pytest.raises(SeedValidationError):
        loader._load_question_rows(question_csv)


def test_matrix_loader_raises_on_missing_dimension_column(tmp_path: Path):
    matrix_csv = tmp_path / "careerpath-profession-matrix-filled.csv"
    matrix_csv.write_text(
        "slug,title,cluster,summary,status,target_analytical,weight_analytical,critical_dimensions,important_subjects,hobby_signals,preferred_environments,why_fit_template,first_steps_template,notes\n"
        "programmer,Programmer,IT,Summary,active,88,1.2,analytical,math,coding,office,why,step,\n",
        encoding="utf-8",
    )

    loader = AssessmentSeedLoader(root=tmp_path)

    with pytest.raises(SeedValidationError):
        loader._load_matrix_rows(matrix_csv, {"matrix_v1"})
