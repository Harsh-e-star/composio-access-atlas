"""Test suite for Composio Access Atlas Dataset & Invariants.
"""
import pytest
from app.database import get_all_apps, get_app_by_id

CATEGORIES = [
    "AI, Research & Media",
    "CRM & Sales",
    "Communications",
    "Data, SEO & Scraping",
    "Developer & Infrastructure",
    "Ecommerce",
    "Finance & Fintech",
    "Marketing & Social",
    "Productivity & Projects",
    "Support & Helpdesk"
]


def test_dataset_contains_exactly_100_apps():
    apps = get_all_apps()
    assert len(apps) == 100, f"Expected 100 apps, got {len(apps)}"


def test_all_10_categories_represented_with_10_apps_each():
    apps = get_all_apps()
    counts = {}
    for a in apps:
        cat = a["category"]
        counts[cat] = counts.get(cat, 0) + 1

    assert len(counts) == 10, f"Expected 10 distinct categories, got {len(counts)}"
    for cat in CATEGORIES:
        assert cat in counts, f"Category '{cat}' missing from dataset"
        assert counts[cat] == 10, f"Category '{cat}' expected 10 apps, got {counts[cat]}"


def test_app_ids_are_strictly_1_to_100_contiguous():
    apps = get_all_apps()
    ids = [a["id"] for a in apps]
    assert sorted(ids) == list(range(1, 101)), "App IDs must be strictly contiguous from 1 to 100"


def test_every_app_has_valid_fields_and_evidence():
    apps = get_all_apps()
    for a in apps:
        assert a["app_name"], f"App {a['id']} missing app_name"
        assert a["website"].startswith("http"), f"App {a['id']} has invalid website: {a['website']}"
        assert a["primary_auth"], f"App {a['id']} missing primary_auth"
        assert isinstance(a["auth_methods"], list) and len(a["auth_methods"]) > 0, f"App {a['id']} missing auth_methods"
        assert a["api_type"], f"App {a['id']} missing api_type"
        assert a["access_tier"] in [
            "Free self-serve", "Trial self-serve", "Paid self-serve",
            "Admin approval", "Partner approval", "Contact sales", "Unknown"
        ], f"App {a['id']} invalid access_tier: {a['access_tier']}"
        assert a["buildability"] in [
            "Build Now", "Build With Prerequisites", "Outreach Required", "Blocked / Unknown"
        ], f"App {a['id']} invalid buildability: {a['buildability']}"
        assert a["official_mcp"] in ["Yes", "No", "Unknown"]
        assert a["community_mcp"] in ["Yes", "No", "Unknown"]
        assert len(a["documentation_urls"]) > 0, f"App {a['id']} missing documentation_urls"
        assert len(a["evidence_excerpts"]) > 0, f"App {a['id']} missing evidence_excerpts"


def test_get_app_by_id():
    app1 = get_app_by_id(1)
    assert app1 is not None
    assert app1["app_name"] == "Salesforce"

    app2 = get_app_by_id(2)
    assert app2 is not None
    assert app2["app_name"] == "HubSpot"

    app100 = get_app_by_id(100)
    assert app100 is not None
    assert app100["app_name"] == "Grain"

    missing = get_app_by_id(999)
    assert missing is None
