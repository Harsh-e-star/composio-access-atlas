"""Test suite for Analytics Calculation Engine.
"""
import pytest
from app.analytics import compute_analytics_summary
from app.database import get_all_apps


def test_analytics_summary_totals():
    summary = compute_analytics_summary()
    assert summary["total_apps"] == 100
    assert summary["categories_count"] == 10
    assert summary["reviewed_count"] == 100
    assert summary["evidence_coverage_pct"] == 100.0


def test_distribution_sums_equal_100():
    summary = compute_analytics_summary()
    
    # Auth distribution sum
    auth_sum = sum(summary["auth_distribution"].values())
    assert auth_sum == 100, f"Auth distribution sum expected 100, got {auth_sum}"
    
    # Access distribution sum
    access_sum = sum(summary["access_distribution"].values())
    assert access_sum == 100, f"Access distribution sum expected 100, got {access_sum}"
    
    # Buildability distribution sum
    build_sum = sum(summary["buildability_distribution"].values())
    assert build_sum == 100, f"Buildability distribution sum expected 100, got {build_sum}"


def test_category_metrics_contains_all_10():
    summary = compute_analytics_summary()
    cat_metrics = summary["category_metrics"]
    assert len(cat_metrics) == 10
    for cm in cat_metrics:
        assert cm["total_apps"] == 10
        assert cm["readiness_score"] >= 0 and cm["readiness_score"] <= 100


def test_priority_segments_contain_all_apps():
    summary = compute_analytics_summary()
    total_segmented = (
        len(summary["quick_wins"]) +
        len(summary["prerequisites_required"]) +
        len(summary["outreach_required"]) +
        len(summary["blocked_or_unknown"])
    )
    assert total_segmented == 100, f"Expected 100 segmented apps, got {total_segmented}"
