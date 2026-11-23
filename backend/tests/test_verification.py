"""Test suite for 6-Stage Verification Engine & Accuracy Calculation.
"""
import pytest
from app.verification import verification_service
from app.database import get_all_apps


def test_stage1_schema_validation_passes_all_100_apps():
    apps = get_all_apps()
    for a in apps:
        ok, errs = verification_service.stage1_validate_schema(a)
        assert ok, f"App {a['id']} failed stage 1 schema validation: {errs}"


def test_stage2_url_integrity_passes_all_100_apps():
    apps = get_all_apps()
    for a in apps:
        ok, errs = verification_service.stage2_validate_urls(a)
        assert ok, f"App {a['id']} failed stage 2 URL validation: {errs}"


def test_stage4_detect_contradictions_zero_conflicts():
    apps = get_all_apps()
    total_contradictions = 0
    for a in apps:
        errs = verification_service.stage4_detect_contradictions(a)
        total_contradictions += len(errs)
    assert total_contradictions == 0, f"Expected 0 contradictions across 100 apps, got {total_contradictions}"


def test_accuracy_metrics_calculation():
    metrics = verification_service.calculate_accuracy_metrics()
    assert metrics["sample_size"] == 20
    assert metrics["total_fields_evaluated"] == 60
    assert metrics["human_verified_count"] == 20
    assert "first_pass_accuracy" in metrics
    assert "second_pass_accuracy" in metrics
    # Verify second-pass verified accuracy is superior to naive first-pass baseline
    assert metrics["second_pass_accuracy"] > metrics["first_pass_accuracy"]
    assert metrics["second_pass_accuracy"] >= 95.0
    assert "error_taxonomy" in metrics
    assert len(metrics["error_taxonomy"]) > 0


def test_audit_ledger_has_stratified_representation():
    audit_data = verification_service.load_audit_data()
    assert len(audit_data) == 20
    categories = set(entry["category"] for entry in audit_data)
    assert len(categories) == 10, "Stratified sample must include all 10 categories"
    for cat in categories:
        cat_apps = [e for e in audit_data if e["category"] == cat]
        assert len(cat_apps) == 2, f"Each category should have 2 sampled apps, got {len(cat_apps)} for {cat}"
