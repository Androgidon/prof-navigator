from app.schemas.assessment_engine import (
    DEEP_RECOMMENDATION_COUNT,
    DIVERSIFICATION_SHORTAGE_FILL_STRATEGY,
    EXPRESS_RECOMMENDATION_COUNT,
)


def recommendation_target_count(assessment_slug: str) -> int:
    if assessment_slug == "deep_v1":
        return DEEP_RECOMMENDATION_COUNT
    return EXPRESS_RECOMMENDATION_COUNT


def diversification_fill_strategy() -> str:
    return DIVERSIFICATION_SHORTAGE_FILL_STRATEGY
