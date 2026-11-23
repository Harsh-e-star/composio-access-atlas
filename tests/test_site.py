"""Browser tests for the standalone case study (docs/index.html)."""
import json, re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
PAGE = ROOT / "docs" / "index.html"
pw = pytest.importorskip("playwright.sync_api")


def data():
    html = PAGE.read_text()
    m = re.search(r"const D = (\{.*?\});\n", html, re.S)
    return json.loads(m.group(1).replace("<\\/", "</"))


@pytest.fixture(scope="module")
def browser():
    if not PAGE.exists():
        pytest.skip("run python -m agent.build_site first")
    with pw.sync_playwright() as p:
        b = p.chromium.launch()
        yield b
        b.close()


@pytest.fixture
def page(browser):
    pg = browser.new_page(viewport={"width": 1280, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.goto(PAGE.as_uri())
    pg.errors = errors
    yield pg
    assert not errors, errors
    pg.close()


def test_no_external_requests_or_localhost():
    html = PAGE.read_text()
    assert "localhost" not in html and "127.0.0.1" not in html
    assert not re.search(r'<script[^>]+src=', html) and not re.search(r'<link[^>]+stylesheet', html)


def test_kpis_match_dataset(page):
    d = data()
    kpis = page.locator("#kpis .kpi .v").all_inner_texts()
    assert kpis[0] == str(len(d["apps"]))
    assert kpis[1] == str(d["meta"]["pass_a_ok"])
    s = d["stats"]
    assert kpis[3] == str(s["tiers"]["free_self_serve"] + s["tiers"]["trial_self_serve"])
    assert kpis[5] == str(len(s["mcp"]["official"]))
    if d["meta"]["human_accuracy"].get("status") != "measured":
        assert kpis[6] == "Pending"


def test_charts_render(page):
    assert page.locator("#catChart svg rect").count() >= 10
    assert page.locator("#authBars .row").count() == 6


def test_search_and_filters(page):
    page.fill("#q", "github")
    assert page.locator("#rows tr").count() >= 1
    assert "GitHub" in page.locator("#rows").inner_text()
    page.fill("#q", "")
    total = page.locator("#rows tr").count()
    page.select_option("#fVerdict", "READY")
    n = page.locator("#rows tr").count()
    assert 0 < n < total
    assert all(t == "Ready" for t in page.locator("#rows .pill").all_inner_texts())


def test_detail_drawer_with_evidence(page):
    page.fill("#q", "github")
    page.locator("#rows tr").first.click()
    dr = page.locator("#drawer")
    assert "open" in dr.get_attribute("class")
    assert dr.locator(".claim a[href^='http']").count() >= 1
    page.keyboard.press("Escape")
    assert "open" not in dr.get_attribute("class")


def test_exports_download(page):
    with page.expect_download() as d:
        page.click("#dlCsv")
    assert d.value.suggested_filename.endswith(".csv")
    with page.expect_download() as d:
        page.click("#dlJson")
    rows = json.loads(Path(d.value.path()).read_text())
    assert len(rows) == len(data()["apps"])


def test_mobile_no_horizontal_scroll(browser):
    pg = browser.new_page(viewport={"width": 375, "height": 800})
    pg.goto(PAGE.as_uri())
    sw = pg.evaluate("document.documentElement.scrollWidth")
    assert sw <= 376, sw
    pg.close()
