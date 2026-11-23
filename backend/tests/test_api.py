"""Test suite for FastAPI REST Endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["apps_count"] == 100


def test_list_apps_all():
    res = client.get("/api/apps")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 100


def test_list_apps_filtered_by_category():
    res = client.get("/api/apps?category=CRM+%26+Sales")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 10
    for a in data:
        assert a["category"] == "CRM & Sales"


def test_list_apps_filtered_by_buildability():
    res = client.get("/api/apps?buildability=Build+Now")
    assert res.status_code == 200
    data = res.json()
    assert len(data) > 0
    for a in data:
        assert a["buildability"] == "Build Now"


def test_list_apps_search():
    res = client.get("/api/apps?search=HubSpot")
    assert res.status_code == 200
    data = res.json()
    assert len(data) >= 1
    assert any(a["app_name"] == "HubSpot" for a in data)


def test_get_app_by_id_success():
    res = client.get("/api/apps/1")
    assert res.status_code == 200
    data = res.json()
    assert data["id"] == 1
    assert data["app_name"] == "Salesforce"
    assert "documentation_urls" in data
    assert "evidence_excerpts" in data


def test_get_app_by_id_not_found():
    res = client.get("/api/apps/999")
    assert res.status_code == 404


def test_get_analytics_endpoint():
    res = client.get("/api/analytics")
    assert res.status_code == 200
    data = res.json()
    assert data["total_apps"] == 100
    assert "auth_distribution" in data
    assert "buildability_distribution" in data
    assert "common_blockers" in data


def test_get_verification_endpoint():
    res = client.get("/api/verification")
    assert res.status_code == 200
    data = res.json()
    assert "metrics" in data
    assert "stages" in data
    assert "audit_ledger" in data
    assert len(data["audit_ledger"]) == 20


def test_export_json_endpoint():
    res = client.get("/api/export/json")
    assert res.status_code == 200
    assert "attachment" in res.headers.get("content-disposition", "")
    data = res.json()
    assert len(data) == 100


def test_export_csv_endpoint():
    res = client.get("/api/export/csv")
    assert res.status_code == 200
    assert "text/csv" in res.headers.get("content-type", "")
    content = res.text
    assert "HubSpot" in content
    assert "Salesforce" in content


@pytest.mark.asyncio
async def test_research_job_trigger_and_poll():
    # Trigger research for App 1
    post_res = client.post("/api/research/1")
    assert post_res.status_code == 200
    job_info = post_res.json()
    assert "job_id" in job_info
    assert job_info["app_id"] == 1

    job_id = job_info["job_id"]
    # Poll status
    status_res = client.get(f"/api/research/status/{job_id}")
    assert status_res.status_code == 200
    status_data = status_res.json()
    assert status_data["job_id"] == job_id
    assert status_data["status"] in ["queued", "discovering", "researching", "verifying", "completed"]
    assert len(status_data["logs"]) > 0
