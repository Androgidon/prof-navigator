from app.domains.assessment_results.result_policy import (
    diversification_fill_strategy,
    recommendation_target_count,
)


def test_recommendation_target_count_express():
    assert recommendation_target_count("express_v1") == 10


def test_recommendation_target_count_deep():
    assert recommendation_target_count("deep_v1") == 15


def test_diversification_fill_strategy():
    assert diversification_fill_strategy() == "score_order_from_skipped_pool"
