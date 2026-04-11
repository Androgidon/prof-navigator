from __future__ import annotations

ASSESSMENT_CATALOG_SEED = [
    {
        "slug": "express_v1",
        "title": "CareerPath Express v1",
        "description": "Quick assessment profile for top-10 recommendations.",
        "target_items_count": 24,
        "min_items_count": 20,
        "max_items_count": 30,
        "expected_duration_min": 7,
        "is_active": True,
        "version": 1,
        "matrix_version_slug": "matrix_v1",
        "scoring_config_json": {
            "sources": {
                "self_report": 0.4,
                "situational": 0.2,
                "subjects_hobbies": 0.2,
                "tasks_calibration": 0.2,
            }
        },
        "question_mix_config_json": {
            "likert": 0.4,
            "forced_choice": 0.25,
            "situational": 0.15,
            "multi_select": 0.1,
            "mini_task": 0.1,
        },
    },
    {
        "slug": "deep_v1",
        "title": "CareerPath Deep v1",
        "description": "Detailed assessment profile for top-10-15 recommendations.",
        "target_items_count": 100,
        "min_items_count": 96,
        "max_items_count": 110,
        "expected_duration_min": 30,
        "is_active": True,
        "version": 1,
        "matrix_version_slug": "matrix_v1",
        "scoring_config_json": {
            "sources": {
                "self_report": 0.4,
                "situational": 0.2,
                "subjects_hobbies": 0.2,
                "tasks_calibration": 0.2,
            }
        },
        "question_mix_config_json": {
            "likert": 0.3,
            "forced_choice": 0.2,
            "situational": 0.2,
            "multi_select_or_ranking": 0.15,
            "mini_task": 0.15,
        },
    },
]
