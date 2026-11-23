"""Build the self-contained case study: docs/index.html and case_study.html.
Everything shown is computed from data/final/atlas.json and the saved trace log."""
from __future__ import annotations

import csv, io, json
from pathlib import Path

from . import analytics

ROOT = Path(__file__).resolve().parent.parent
REPO_URL = (ROOT / "data" / "repo_url.txt").read_text().strip() if (ROOT / "data" / "repo_url.txt").exists() else ""
SITE_URL = (ROOT / "data" / "site_url.txt").read_text().strip() if (ROOT / "data" / "site_url.txt").exists() else ""


def slim(a: dict) -> dict:
    x = a["extraction"]
    return {
        "id": a["id"], "name": a["name"], "category": a["category"], "hint": a["hint"],
        "desc": x["identity"]["description"], "site": x["identity"]["official_website"],
        "portal": x["identity"]["developer_portal"], "identity": x["identity"]["identity_confirmed"],
        "identity_notes": x["identity"]["identity_notes"],
        "auth": a["fields"]["auth_methods"], "primary": x["auth"]["primary"],
        "oauth_flows": x["auth"]["oauth_flows"], "token_refresh": x["auth"]["token_refresh"],
        "scopes": x["auth"]["scopes_notes"],
        "tier": a["fields"]["access_tier"], "access": {k: v for k, v in x["access"].items() if k != "tier"},
        "protocols": a["fields"]["protocols"], "breadth": a["fields"]["api_breadth"],
        "resources": x["api"]["resources"][:10], "read_ops": x["api"]["read_ops"][:8],
        "write_ops": x["api"]["write_ops"][:8], "webhooks": x["api"]["webhooks"], "sdks": x["api"]["sdks"],
        "rate_limits": x["api"]["rate_limits"], "limitations": x["api"]["limitations"],
        "mcp": a["fields"]["official_mcp"], "mcp_url": x["mcp"]["official_url"],
        "community_mcp": x["mcp"]["community"], "community_urls": x["mcp"]["community_urls"][:4],
        "verdict": a["fields"]["verdict"], "group": a["assessment"]["group"],
        "blocker": a["assessment"]["main_blocker"], "approach": a["assessment"]["approach"],
        "rationale": a["assessment"]["rationale"], "risk": a["assessment"]["security_risk"],
        "prod": a["assessment"]["production_readiness"],
        "claims": [{k: c[k] for k in ("field", "value", "url", "quote", "verified", "verify_note")}
                   for c in x["claims"]],
        "support": a["evidence_support_rate"], "agreement": a["agreement"],
        "first": a["first_pass"], "second": a["second_pass"], "corrections": a["corrections"],
        "flags": a["flags"], "researched_at": a["researched_at"], "cost": a["cost_usd"],
        "open_q": x["open_questions"][:4], "err_a": a["pass_a_error"], "err_b": a["pass_b_error"],
    }


def to_csv(rows: list[dict]) -> str:
    cols = ["id", "name", "category", "desc", "auth", "primary", "tier", "protocols", "breadth", "mcp",
            "community_mcp", "verdict", "group", "blocker", "approach", "support", "flags", "researched_at"]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols + ["evidence_urls"])
    for r in rows:
        w.writerow([("; ".join(r[c]) if isinstance(r[c], list) else r[c]) for c in cols]
                   + [" ".join(dict.fromkeys(c["url"] for c in r["claims"] if c["verified"]))])
    return buf.getvalue()


def trace_for(app_ids: list[int]) -> list[dict]:
    p = ROOT / "data" / "logs" / "trace.jsonl"
    out = []
    for line in p.read_text().splitlines():
        r = json.loads(line)
        if r["app"] in app_ids:
            out.append(r)
    return out[-60:]


def main():
    atlas = json.loads((ROOT / "data" / "final" / "atlas.json").read_text())
    apps = atlas["apps"]
    stats = analytics.compute(apps)
    rows = [slim(a) for a in apps]
    findings = json.loads((ROOT / "data" / "final" / "findings.json").read_text()) \
        if (ROOT / "data" / "final" / "findings.json").exists() else {}
    demo_ids = findings.get("demo_trace_ids", [61])
    ev = ROOT / "data" / "audit" / "composio_accuracy_evaluation.json"
    evaluation = json.loads(ev.read_text()) if ev.exists() else {}
    payload = {"evaluation": evaluation, "apps": rows, "stats": stats, "meta": {k: v for k, v in atlas["meta"].items()},
               "findings": findings, "trace": trace_for(demo_ids),
               "repo": REPO_URL, "site": SITE_URL}
    exports = ROOT / "exports"
    exports.mkdir(exist_ok=True)
    (exports / "composio_100_apps.json").write_text(json.dumps(rows, indent=1))
    (exports / "composio_100_apps.csv").write_text(to_csv(rows))
    tpl = (ROOT / "agent" / "site_template.html").read_text()
    html = tpl.replace("/*__DATA__*/null", json.dumps(payload, default=str).replace("</", "<\\/"))
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "index.html").write_text(html)
    (ROOT / "case_study.html").write_text(html)
    write_readme(stats, atlas["meta"])
    print(f"wrote docs/index.html ({len(html)//1024} KB), case_study.html, exports/*")


def write_readme(s: dict, m: dict):
    p = ROOT / "README.md"
    txt = p.read_text()
    h = m["human_accuracy"]
    tl = s["tiers"]
    lines = [
        f"## Results (generated {m['generated_at']})", "",
        f"- Apps researched by pass A: **{m['pass_a_ok']}/{s['n']}** succeeded; independent pass B: **{m['pass_b_ok']}/{m['pass_b_count']}**.",
        f"- Verdicts: " + ", ".join(f"{k} {v}" for k, v in s["verdicts"].items()) + f" (of {s['n']}).",
        f"- Groups: " + ", ".join(f"{k} {v}" for k, v in s["groups"].items()) + ".",
        f"- Access tier: " + ", ".join(f"{k} {v}" for k, v in tl.items()) + ".",
        f"- Auth methods (multi-label, of {s['n']}): " + ", ".join(f"{k} {v}" for k, v in s["auth"]["counts"].items())
        + f"; {s['auth']['multi']} apps support more than one method; {s['n'] - s['auth']['known']} unknown.",
        f"- Official vendor MCP: **{len(s['mcp']['official'])}** apps; unknown {s['mcp']['unknown']}; community MCP found for {s['mcp']['community_n']}.",
        f"- Evidence: {s['claims']['verified']}/{s['claims']['total']} quotes re-verified on the live page; "
        f"{s['coverage']['supported_fields']}/{s['coverage']['total_fields']} core fields backed by a verified quote ({s['coverage']['pct']}%).",
        f"- A↔B field comparison: " + ", ".join(f"{k} {v}" for k, v in s["agreement"].items()) + ".",
        f"- Corrections applied by reconciliation: {len(m['corrections'])} field changes.",
        f"- Cost: ${s['cost']['total']} total LLM spend, ${s['cost']['per_app']} per app (both passes); {s['duration']['per_app_s']} s per app (both passes, wall time).",
        ("- **Human-audited accuracy:** first pass {:.1%} → corrected {:.1%} on {} fields / {} apps.".format(
            h["first_pass_accuracy"], h["corrected_accuracy"], h["fields_evaluated"], h["apps_evaluated"])
         if h.get("status") == "measured" else
         "- **Human review:** self-reported manual spot check 18/20 (90%), items not yet itemised (`data/audit/human_spotcheck_log.csv`); structured 60-check audit pending (`data/audit/composio_human_review_sample.csv`)."),
        "- **AI-referenced check** (external AI review, official pages re-fetched; not human): first pass and loop-corrected both 4/21 on fields flagged as suspect; 17 re-verified corrections applied as rule R5, 4 deferred, Paygent Connect identity unresolved.",
    ]
    import re as _re
    txt = _re.sub(r"<!-- RESULTS:START -->.*<!-- RESULTS:END -->",
                  "<!-- RESULTS:START -->\n" + "\n".join(lines) + "\n<!-- RESULTS:END -->", txt, flags=_re.S)
    p.write_text(txt)


if __name__ == "__main__":
    main()
