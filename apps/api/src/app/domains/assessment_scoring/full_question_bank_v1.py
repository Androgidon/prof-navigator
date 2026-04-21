from __future__ import annotations

from typing import List, Literal, Optional, TypedDict


QuestionType = Literal["likert_5", "single_select_4", "multi_select_2", "situational_single", "mini_task"]


class FullQuestionMeta(TypedDict):
    question_id: str
    block: str
    is_core: bool
    question_type: QuestionType
    primary_dimension: str
    secondary_dimensions: List[str]
    boundary: Optional[str]


FULL_V1_BLOCK_WEIGHTS = {
    "B1": 0.22,
    "B2": 0.30,
    "B3": 0.18,
    "B4": 0.20,
    "B5": 0.10,
    "M7": 0.08,
    "M8": 0.08,
}

FULL_V1_ADAPTIVE_BLEND = 0.18
FULL_V1_ADAPTIVE_DELTA_CAP = 12.0

FULL_SIGNAL_BANDS = {
    "strong": (85.0, 95.0),
    "medium": (65.0, 84.0),
    "light": (45.0, 64.0),
    "negative": (30.0, 44.0),
}

BOUNDARY_IDS = {
    "helping_vs_marketing": ["FT_AD_HM_01", "FT_AD_HM_02", "FT_AD_HM_03"],
    "practical_vs_technical_vs_structured": ["FT_AD_PTS_01", "FT_AD_PTS_02", "FT_AD_PTS_03"],
    "engineering_vs_science": ["FT_AD_ES_01", "FT_AD_ES_02", "FT_AD_ES_03"],
    "finance_vs_it_analytics": ["FT_AD_FI_01", "FT_AD_FI_02", "FT_EXP_FI_01", "FT_EXP_FI_02", "FT_EXP_FI_03"],
    "law_vs_public_vs_politics_vs_security": ["FT_AD_LPPS_01", "FT_AD_LPPS_02", "FT_AD_LPPS_03"],
    "creative_vs_exploratory_academic": ["FT_AD_CEA_01", "FT_AD_CEA_02"],
}

# machine-readable draft v1 metadata for 72-question Full bank
FULL_QUESTION_BANK_V1: List[FullQuestionMeta] = [
    *[
        {
            "question_id": f"FT_INT_{i:02d}",
            "block": "B1",
            "is_core": True,
            "question_type": "situational_single" if i in {1, 3, 4, 6, 9, 10} else (
                "likert_5" if i in {4, 8, 12} else ("multi_select_2" if i in {11} else "single_select_4")
            ),
            "primary_dimension": {
                1: "helping", 2: "practical", 3: "analytical", 4: "detail", 5: "structured", 6: "leadership",
                7: "detail", 8: "quantitative", 9: "verbal", 10: "exploratory", 11: "practical", 12: "structured",
            }[i],
            "secondary_dimensions": {
                1: ["verbal", "creative", "analytical", "practical"],
                2: ["technical", "creative", "social"],
                3: ["structured", "social", "practical"],
                4: ["structured"],
                5: ["creative", "practical", "helping"],
                6: ["analytical", "helping", "practical"],
                7: ["practical", "exploratory", "social"],
                8: ["analytical"],
                9: ["structured", "creative", "technical"],
                10: ["practical", "helping", "social"],
                11: ["verbal", "helping", "analytical", "creative"],
                12: ["detail"],
            }[i],
            "boundary": None,
        }
        for i in range(1, 13)
    ],
    *[
        {
            "question_id": f"FT_SJT_{i:02d}",
            "block": "B2",
            "is_core": True,
            "question_type": "multi_select_2" if i == 16 else "situational_single",
            "primary_dimension": {
                1: "helping", 2: "analytical", 3: "structured", 4: "social", 5: "detail", 6: "structured", 7: "analytical", 8: "exploratory",
                9: "helping", 10: "structured", 11: "technical", 12: "verbal", 13: "helping", 14: "detail", 15: "structured", 16: "helping",
            }[i],
            "secondary_dimensions": {
                1: ["verbal", "structured", "practical"], 2: ["detail", "structured", "verbal"], 3: ["analytical", "exploratory", "practical"],
                4: ["helping", "creative", "analytical", "practical"], 5: ["practical", "creative"], 6: ["leadership", "practical", "social"],
                7: ["exploratory", "structured", "social"], 8: ["analytical", "practical"], 9: ["social", "structured", "leadership"],
                10: ["detail", "quantitative"], 11: ["analytical", "practical", "exploratory"], 12: ["helping", "quantitative", "structured"],
                13: ["structured", "social"], 14: ["practical", "exploratory"], 15: ["social", "analytical", "practical"],
                16: ["leadership", "analytical", "practical", "verbal"],
            }[i],
            "boundary": None,
        }
        for i in range(1, 17)
    ],
    *[
        {
            "question_id": f"FT_WST_{i:02d}",
            "block": "B3",
            "is_core": True,
            "question_type": "multi_select_2" if i == 10 else ("likert_5" if i in {1, 2, 3, 4, 7, 9} else "single_select_4"),
            "primary_dimension": {1: "structured", 2: "detail", 3: "practical", 4: "verbal", 5: "analytical", 6: "exploratory", 7: "structured", 8: "technical", 9: "leadership", 10: "practical"}[i],
            "secondary_dimensions": {
                1: ["detail"], 2: ["structured"], 3: ["technical"], 4: ["helping", "social"], 5: ["detail", "social"],
                6: ["structured", "practical"], 7: ["detail"], 8: ["social", "verbal", "quantitative"], 9: ["structured"],
                10: ["analytical", "verbal", "creative", "helping"],
            }[i],
            "boundary": None,
        }
        for i in range(1, 11)
    ],
    *[
        {
            "question_id": f"FT_COG_{i:02d}",
            "block": "B4",
            "is_core": True,
            "question_type": "mini_task",
            "primary_dimension": {1: "analytical", 2: "quantitative", 3: "verbal", 4: "detail", 5: "practical", 6: "structured", 7: "helping", 8: "quantitative", 9: "detail", 10: "exploratory"}[i],
            "secondary_dimensions": {
                1: ["detail"], 2: ["analytical"], 3: ["analytical"], 4: ["structured"], 5: ["technical", "analytical"],
                6: ["analytical", "leadership"], 7: ["verbal"], 8: ["analytical"], 9: ["structured", "analytical"], 10: ["analytical"],
            }[i],
            "boundary": None,
        }
        for i in range(1, 11)
    ],
    *[
        {
            "question_id": f"FT_ENV_{i:02d}",
            "block": "B5",
            "is_core": True,
            "question_type": "multi_select_2" if i == 7 else ("likert_5" if i in {4, 5} else "single_select_4"),
            "primary_dimension": {1: "practical", 2: "structured", 3: "exploratory", 4: "structured", 5: "analytical", 6: "practical", 7: "leadership", 8: "detail"}[i],
            "secondary_dimensions": {
                1: ["social", "analytical", "creative"], 2: ["practical", "exploratory"], 3: ["detail", "verbal", "structured"], 4: ["detail"],
                5: ["exploratory"], 6: ["helping", "quantitative", "creative"], 7: ["social", "structured", "technical", "creative"], 8: ["practical", "helping", "social"],
            }[i],
            "boundary": None,
        }
        for i in range(1, 9)
    ],
    {"question_id": "FT_AD_HM_01", "block": "M1", "is_core": False, "question_type": "situational_single", "primary_dimension": "helping", "secondary_dimensions": ["verbal", "social"], "boundary": "helping_vs_marketing"},
    {"question_id": "FT_AD_HM_02", "block": "M1", "is_core": False, "question_type": "situational_single", "primary_dimension": "helping", "secondary_dimensions": ["social", "creative"], "boundary": "helping_vs_marketing"},
    {"question_id": "FT_AD_HM_03", "block": "M1", "is_core": False, "question_type": "mini_task", "primary_dimension": "helping", "secondary_dimensions": ["verbal"], "boundary": "helping_vs_marketing"},
    {"question_id": "FT_AD_PTS_01", "block": "M2", "is_core": False, "question_type": "situational_single", "primary_dimension": "practical", "secondary_dimensions": ["technical", "structured"], "boundary": "practical_vs_technical_vs_structured"},
    {"question_id": "FT_AD_PTS_02", "block": "M2", "is_core": False, "question_type": "mini_task", "primary_dimension": "structured", "secondary_dimensions": ["detail", "practical"], "boundary": "practical_vs_technical_vs_structured"},
    {"question_id": "FT_AD_PTS_03", "block": "M2", "is_core": False, "question_type": "single_select_4", "primary_dimension": "practical", "secondary_dimensions": ["technical", "structured"], "boundary": "practical_vs_technical_vs_structured"},
    {"question_id": "FT_AD_ES_01", "block": "M3", "is_core": False, "question_type": "situational_single", "primary_dimension": "practical", "secondary_dimensions": ["exploratory", "analytical"], "boundary": "engineering_vs_science"},
    {"question_id": "FT_AD_ES_02", "block": "M3", "is_core": False, "question_type": "mini_task", "primary_dimension": "practical", "secondary_dimensions": ["structured", "technical"], "boundary": "engineering_vs_science"},
    {"question_id": "FT_AD_ES_03", "block": "M3", "is_core": False, "question_type": "single_select_4", "primary_dimension": "practical", "secondary_dimensions": ["exploratory", "analytical"], "boundary": "engineering_vs_science"},
    {"question_id": "FT_AD_FI_01", "block": "M4", "is_core": False, "question_type": "situational_single", "primary_dimension": "quantitative", "secondary_dimensions": ["analytical", "structured"], "boundary": "finance_vs_it_analytics"},
    {"question_id": "FT_AD_FI_02", "block": "M4", "is_core": False, "question_type": "mini_task", "primary_dimension": "quantitative", "secondary_dimensions": ["analytical"], "boundary": "finance_vs_it_analytics"},
    {"question_id": "FT_AD_LPPS_01", "block": "M5", "is_core": False, "question_type": "situational_single", "primary_dimension": "structured", "secondary_dimensions": ["verbal", "social", "leadership"], "boundary": "law_vs_public_vs_politics_vs_security"},
    {"question_id": "FT_AD_LPPS_02", "block": "M5", "is_core": False, "question_type": "mini_task", "primary_dimension": "verbal", "secondary_dimensions": ["analytical", "leadership"], "boundary": "law_vs_public_vs_politics_vs_security"},
    {"question_id": "FT_AD_LPPS_03", "block": "M5", "is_core": False, "question_type": "situational_single", "primary_dimension": "leadership", "secondary_dimensions": ["structured", "social"], "boundary": "law_vs_public_vs_politics_vs_security"},
    {"question_id": "FT_AD_CEA_01", "block": "M6", "is_core": False, "question_type": "situational_single", "primary_dimension": "creative", "secondary_dimensions": ["exploratory", "verbal"], "boundary": "creative_vs_exploratory_academic"},
    {"question_id": "FT_AD_CEA_02", "block": "M6", "is_core": False, "question_type": "mini_task", "primary_dimension": "creative", "secondary_dimensions": ["analytical", "exploratory"], "boundary": "creative_vs_exploratory_academic"},
    {"question_id": "FT_EXP_ROLE_01", "block": "M7", "is_core": False, "question_type": "situational_single", "primary_dimension": "practical", "secondary_dimensions": ["technical", "structured", "leadership"], "boundary": None},
    {"question_id": "FT_EXP_ROLE_02", "block": "M7", "is_core": False, "question_type": "single_select_4", "primary_dimension": "practical", "secondary_dimensions": ["technical", "structured", "leadership"], "boundary": None},
    {"question_id": "FT_EXP_ROLE_03", "block": "M7", "is_core": False, "question_type": "multi_select_2", "primary_dimension": "practical", "secondary_dimensions": ["technical", "structured", "leadership", "detail"], "boundary": None},
    {"question_id": "FT_EXP_ROLE_04", "block": "M7", "is_core": False, "question_type": "situational_single", "primary_dimension": "practical", "secondary_dimensions": ["technical", "structured", "leadership"], "boundary": None},
    {"question_id": "FT_EXP_ROLE_05", "block": "M7", "is_core": False, "question_type": "situational_single", "primary_dimension": "practical", "secondary_dimensions": ["technical", "structured", "leadership"], "boundary": None},
    {"question_id": "FT_EXP_SAFE_01", "block": "M7", "is_core": False, "question_type": "situational_single", "primary_dimension": "structured", "secondary_dimensions": ["detail", "leadership", "practical"], "boundary": None},
    {"question_id": "FT_EXP_SAFE_02", "block": "M7", "is_core": False, "question_type": "mini_task", "primary_dimension": "structured", "secondary_dimensions": ["analytical", "detail"], "boundary": None},
    {"question_id": "FT_EXP_SAFE_03", "block": "M7", "is_core": False, "question_type": "likert_5", "primary_dimension": "structured", "secondary_dimensions": ["detail"], "boundary": None},
    {"question_id": "FT_EXP_SAFE_04", "block": "M7", "is_core": False, "question_type": "single_select_4", "primary_dimension": "structured", "secondary_dimensions": ["analytical", "leadership", "detail"], "boundary": None},
    {"question_id": "FT_EXP_FI_01", "block": "M7", "is_core": False, "question_type": "situational_single", "primary_dimension": "quantitative", "secondary_dimensions": ["structured", "analytical"], "boundary": "finance_vs_it_analytics"},
    {"question_id": "FT_EXP_FI_02", "block": "M7", "is_core": False, "question_type": "mini_task", "primary_dimension": "structured", "secondary_dimensions": ["quantitative", "analytical"], "boundary": "finance_vs_it_analytics"},
    {"question_id": "FT_EXP_FI_03", "block": "M7", "is_core": False, "question_type": "single_select_4", "primary_dimension": "structured", "secondary_dimensions": ["leadership", "quantitative", "analytical"], "boundary": "finance_vs_it_analytics"},
    {"question_id": "FT_EXP_OPS_01", "block": "M8", "is_core": False, "question_type": "situational_single", "primary_dimension": "structured", "secondary_dimensions": ["analytical", "practical"], "boundary": None},
    {"question_id": "FT_EXP_OPS_02", "block": "M8", "is_core": False, "question_type": "likert_5", "primary_dimension": "structured", "secondary_dimensions": ["practical", "detail"], "boundary": None},
    {"question_id": "FT_EXP_OPS_03", "block": "M8", "is_core": False, "question_type": "single_select_4", "primary_dimension": "practical", "secondary_dimensions": ["structured", "technical", "leadership"], "boundary": None},
    {"question_id": "FT_EXP_OPS_04", "block": "M8", "is_core": False, "question_type": "mini_task", "primary_dimension": "structured", "secondary_dimensions": ["detail", "practical", "analytical"], "boundary": None},
]
