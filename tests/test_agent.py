"""Software tests. These prove the code behaves as specified — NOT that the research is
factually correct (that is what the human audit measures)."""
import asyncio, csv, json
from pathlib import Path

import httpx
import pytest

from agent import registry, stages, verify, fetch
from agent.schema import AppRecord, Extraction, Claim


# ---------------- registry
def test_exactly_100_apps_10_categories():
    apps = registry.load()
    assert len(apps) == 100
    assert [a["id"] for a in apps] == list(range(1, 101))
    assert len({a["name"] for a in apps}) == 100
    assert len(registry.CATEGORIES) == 10
    for c in registry.CATEGORIES:
        assert sum(a["category"] == c for a in apps) == 10


def test_registry_matches_brief_spot_checks():
    names = {a["id"]: a["name"] for a in registry.load()}
    assert names[10] == "DealCloud" and names[59] == "Waterfall.io"
    assert names[84] == "Paygent Connect" and names[99] == "YouTube Transcript"
    assert names[100] == "Grain" and names[1] == "Salesforce"


def test_seeds_derived_from_hint_only():
    a = registry.by_name("Harvest")
    assert a["seeds"][0] == "https://help.getharvest.com/api-v2"
    assert registry.by_name("Paygent Connect")["seeds"] == []


# ---------------- fetch helpers
def test_quote_matching_exact_and_fuzzy():
    page = "To authenticate, send your API key in the Authorization header as a Bearer token. " * 2
    assert fetch.quote_in_text("send your API key in the Authorization header", page)
    assert not fetch.quote_in_text("OAuth 2.0 authorization code flow is required", page)
    assert not fetch.quote_in_text("", page)


def test_parse_html_strips_scripts_and_collects_links():
    d = fetch.parse_html('<title>T</title><script>evil()</script><p>Hello</p><a href="/x">X</a>',
                         "https://a.com/docs")
    assert "evil" not in d["text"] and "Hello" in d["text"]
    assert d["links"][0]["url"] == "https://a.com/x"


def test_fetch_retries_then_records_error(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "CACHE", tmp_path / "c")
    monkeypatch.setattr(fetch, "LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(fetch, "MIN_INTERVAL", 0)
    calls = {"n": 0}

    def handler(req):
        calls["n"] += 1
        if req.url.path == "/robots.txt":
            return httpx.Response(404)
        return httpx.Response(503)

    async def go():
        f = fetch.Fetcher()
        f.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        orig = asyncio.sleep
        monkeypatch.setattr(asyncio, "sleep", lambda s: orig(0))
        r = await f.get("https://x.test/page", retries=2)
        await f.close()
        return r
    r = asyncio.run(go())
    assert r["error"] == "http_503" and calls["n"] == 4  # robots + 3 attempts


def test_network_failure_not_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "CACHE", tmp_path / "c")
    monkeypatch.setattr(fetch, "LOG", tmp_path / "log.jsonl")
    monkeypatch.setattr(fetch, "MIN_INTERVAL", 0)

    def handler(req):
        raise httpx.ConnectError("down")

    async def go():
        f = fetch.Fetcher()
        f.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        orig = asyncio.sleep
        monkeypatch.setattr(asyncio, "sleep", lambda s: orig(0))
        r = await f.get("https://y.test/p", retries=0)
        await f.close()
        return r
    r = asyncio.run(go())
    assert r["error"].startswith("ConnectError") and not list((tmp_path / "c").glob("*"))


def test_robots_disallow_is_respected(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "CACHE", tmp_path / "c")
    monkeypatch.setattr(fetch, "LOG", tmp_path / "log.jsonl")

    def handler(req):
        if req.url.path == "/robots.txt":
            return httpx.Response(200, text="User-agent: *\nDisallow: /")
        raise AssertionError("must not fetch disallowed page")

    async def go():
        f = fetch.Fetcher()
        f.client = httpx.AsyncClient(transport=httpx.MockTransport(handler))
        r = await f.get("https://z.test/secret")
        await f.close()
        return r
    assert asyncio.run(go())["error"] == "blocked_by_robots_txt"


# ---------------- schema / invalid output
def test_invalid_llm_output_rejected():
    with pytest.raises(Exception):
        Extraction.model_validate({"auth": {"methods": ["Magic"]}})
    with pytest.raises(Exception):
        Extraction.model_validate({"access": {"tier": "kinda_free"}})


def test_default_extraction_is_unknown_not_negative():
    x = Extraction()
    assert x.access.tier == "unknown" and x.mcp.official == "unknown" and x.api.breadth == "Unknown"


# ---------------- Stage 5 rules
def mk(**kw) -> Extraction:
    x = Extraction()
    x.identity.identity_confirmed = "yes"
    x.api.protocols = kw.get("protocols", ["REST"])
    x.access.tier = kw.get("tier", "free_self_serve")
    x.auth.methods = kw.get("auth", ["OAuth2"])
    return x


@pytest.mark.parametrize("tier,verdict,group", [
    ("free_self_serve", "READY", "BUILD NOW"),
    ("trial_self_serve", "READY", "BUILD NOW"),
    ("paid_plan", "CONDITIONAL", "BUILD WITH PREREQUISITES"),
    ("admin_approval", "CONDITIONAL", "BUILD WITH PREREQUISITES"),
    ("partner_or_sales", "GATED", "OUTREACH REQUIRED"),
    ("unknown", "UNKNOWN", "RESEARCH FURTHER"),
])
def test_verdict_rules(tier, verdict, group):
    a = stages.assess(mk(tier=tier))
    assert a.verdict == verdict and a.group == group


def test_no_interface_and_identity_rules():
    assert stages.assess(mk(protocols=["none"])).verdict == "NO_SUPPORTED_INTERFACE"
    x = mk(); x.identity.identity_confirmed = "no"
    assert stages.assess(x).verdict == "UNKNOWN"
    assert stages.assess(mk(protocols=[])).verdict == "UNKNOWN"


def test_snippets_respect_budget():
    t = "intro " * 200 + "oauth token scope " * 300
    assert len(stages.snippets(t, 3000)) < 3600


# ---------------- Level 2 compare + reconcile
@pytest.mark.parametrize("a,b,field,exp", [
    (["OAuth2"], ["OAuth2"], "auth_methods", "agree"),
    (["OAuth2"], ["OAuth2", "API key"], "auth_methods", "partial"),
    (["OAuth2"], ["API key"], "auth_methods", "contradiction"),
    ([], ["API key"], "auth_methods", "insufficient"),
    ("free_self_serve", "trial_self_serve", "access_tier", "partial"),
    ("free_self_serve", "partner_or_sales", "access_tier", "contradiction"),
    ("unknown", "paid_plan", "access_tier", "insufficient"),
])
def test_compare(a, b, field, exp):
    assert verify.compare(a, b, field) == exp


def rec(pass_name, tier, claims, auth=("OAuth2",)):
    x = mk(tier=tier, auth=list(auth))
    x.claims = [Claim(field=f, value="v", url="https://d.test", quote="q", verified=v) for f, v in claims]
    return AppRecord(id=1, name="Salesforce", category="CRM and Sales", pass_name=pass_name,
                     researched_at="t", extraction=x, assessment=stages.assess(x))


def test_reconcile_gap_fill_uses_verified_b():
    a = rec("a", "unknown", [])
    b = rec("b", "paid_plan", [("access.tier", True)])
    x, ch = verify.reconcile(a, b)
    assert x.access.tier == "paid_plan" and ch[0]["rule"].startswith("R1")


def test_reconcile_does_not_take_unverified_b():
    a = rec("a", "unknown", [])
    b = rec("b", "paid_plan", [("access.tier", False)])
    x, ch = verify.reconcile(a, b)
    assert x.access.tier == "unknown" and not ch


def test_reconcile_abstains_on_unverified_conflict():
    a = rec("a", "free_self_serve", [("access.tier", False)])
    b = rec("b", "partner_or_sales", [("access.tier", False)])
    x, ch = verify.reconcile(a, b)
    assert x.access.tier == "unknown" and ch[0]["rule"].startswith("R4")


def test_reconcile_keeps_a_when_both_verified():
    a = rec("a", "free_self_serve", [("access.tier", True)])
    b = rec("b", "partner_or_sales", [("access.tier", True)])
    x, _ = verify.reconcile(a, b)
    assert x.access.tier == "free_self_serve"


def test_reconcile_never_mutates_first_pass():
    a = rec("a", "unknown", [])
    b = rec("b", "paid_plan", [("access.tier", True)])
    verify.reconcile(a, b)
    assert a.extraction.access.tier == "unknown"


# ---------------- Level 3 sampling + scoring
def fake_final():
    out = {}
    for ap in registry.load():
        out[ap["id"]] = {"id": ap["id"], "category": ap["category"],
                         "agreement": {"auth_methods": "contradiction" if ap["id"] % 7 == 0 else "agree"}}
    return out


def test_audit_sample_is_stratified_and_reproducible():
    s1, s2 = verify.audit_sample(fake_final()), verify.audit_sample(fake_final())
    assert s1 == s2 and len(s1) == 20
    cats = [registry.CATEGORIES[(i - 1) // 10] for i in s1]
    assert all(cats.count(c) == 2 for c in registry.CATEGORIES)


def test_score_pending_without_labels(tmp_path, monkeypatch):
    monkeypatch.setattr(verify, "AUDIT", tmp_path)
    with (tmp_path / "human_audit_worksheet.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, verify.AUDIT_COLS); w.writeheader()
        w.writerow({"app_id": 1, "field": "access_tier", "first_pass": "unknown", "corrected": "paid_plan"})
    assert verify.score({})["status"] == "pending"


def test_score_accuracy_formula_and_unknown_not_credited(tmp_path, monkeypatch):
    monkeypatch.setattr(verify, "AUDIT", tmp_path)
    rows = [("1", "access_tier", "unknown", "paid_plan", "paid_plan"),
            ("1", "auth_methods", "OAuth2", "API key; OAuth2", "OAuth2; API key"),
            ("2", "access_tier", "free_self_serve", "free_self_serve", "free_self_serve"),
            ("2", "official_mcp", "yes", "yes", "no")]
    with (tmp_path / "human_audit_worksheet.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, verify.AUDIT_COLS); w.writeheader()
        for i, f, fp, co, gt in rows:
            w.writerow({"app_id": i, "app": "x", "field": f, "first_pass": fp, "second_pass": "",
                        "corrected": co, "human_ground_truth": gt, "reviewer": "me"})
    r = verify.score({})
    assert r["status"] == "measured" and r["fields_evaluated"] == 4
    assert r["first_pass_accuracy"] == 0.25      # only row 3
    assert r["corrected_accuracy"] == 0.75       # rows 1,2,3
    assert r["corrected_app_exact"] == 0.5       # app 1 all right, app 2 not
    assert r["first_pass_unknown"] == 1


def test_reconcile_both_failed_is_all_unknown():
    a = rec("a", "free_self_serve", []); a.error = "boom"
    x, ch = verify.reconcile(a, None)
    assert x.access.tier == "unknown" and ch[0]["rule"].startswith("R0")


def test_union_never_mixes_none_with_protocols():
    a = rec("a", "free_self_serve", [])
    a.extraction.api.protocols = ["REST"]
    b = rec("b", "free_self_serve", [("api.protocols", True)])
    b.extraction.api.protocols = ["REST", "none", "GraphQL"]
    x, ch = verify.reconcile(a, b)
    assert x.api.protocols == ["GraphQL", "REST"]
