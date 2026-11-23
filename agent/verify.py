"""Verification: Level 1 (deterministic), Level 2 (independent pass comparison +
evidence-based reconciliation), Level 3 (human audit worksheet + scoring).

Reconciliation rules were fixed BEFORE any human labels existed and are not tuned
against them; see README "Evaluation integrity".
"""
from __future__ import annotations

import csv, hashlib, json, re, time
from collections import Counter
from pathlib import Path

from . import registry, stages
from .schema import AppRecord, CORE_FIELDS, Extraction

ROOT = Path(__file__).resolve().parent.parent
RUNS, OUT, AUDIT = ROOT / "data" / "runs", ROOT / "data" / "final", ROOT / "data" / "audit"
URL_RE = re.compile(r"^https?://[^\s/$.?#].[^\s]*$")
ADJ_TIERS = {frozenset({"free_self_serve", "trial_self_serve"}),
             frozenset({"paid_plan", "admin_approval"})}


def load_pass(name: str) -> dict[int, AppRecord]:
    out = {}
    for p in sorted((RUNS / f"pass_{name}").glob("*.json")):
        r = AppRecord.model_validate_json(p.read_text())
        out[r.id] = r
    return out


def value(r: AppRecord | None, field: str):
    if r is None or r.error:
        return None
    x = r.extraction
    return {"auth_methods": sorted(set(x.auth.methods)), "access_tier": x.access.tier,
            "protocols": sorted(set(x.api.protocols)), "api_breadth": x.api.breadth,
            "official_mcp": x.mcp.official,
            "verdict": r.assessment.verdict if r.assessment else "UNKNOWN"}[field]


def is_unknown(v) -> bool:
    return v in (None, [], "unknown", "Unknown", "UNKNOWN")


def compare(a, b, field: str) -> str:
    if is_unknown(a) or is_unknown(b):
        return "insufficient"
    if a == b:
        return "agree"
    if isinstance(a, list):
        return "partial" if set(a) & set(b) else "contradiction"
    if field == "access_tier" and frozenset({a, b}) in ADJ_TIERS:
        return "partial"
    return "contradiction"


# ---------------------------------------------------------------- Level 1
def level1(recs: dict[int, AppRecord]) -> list[dict]:
    issues = []
    apps = {a["id"]: a for a in registry.load()}
    if set(recs) != set(apps):
        issues.append({"id": None, "check": "coverage", "detail": f"missing ids {sorted(set(apps) - set(recs))}"})
    names = Counter(r.name for r in recs.values())
    for n, c in names.items():
        if c > 1:
            issues.append({"id": None, "check": "duplicate_name", "detail": n})
    for i, r in recs.items():
        a = apps[i]
        if r.name != a["name"] or r.category != a["category"]:
            issues.append({"id": i, "check": "identity_mismatch", "detail": f"{r.name}/{r.category}"})
        if r.error:
            issues.append({"id": i, "check": "research_error", "detail": r.error}); continue
        x = r.extraction
        if x.auth.primary and x.auth.primary not in x.auth.methods:
            issues.append({"id": i, "check": "primary_auth_not_in_methods", "detail": x.auth.primary})
        if x.mcp.official == "yes" and not x.mcp.official_url:
            issues.append({"id": i, "check": "official_mcp_without_url", "detail": ""})
        elif x.mcp.official == "yes" and "mcp" not in (x.mcp.official_url or "").lower() and not any(
                c.verified and c.field.lower().startswith("mcp") and "mcp" in (c.quote + c.url).lower()
                for c in x.claims):
            issues.append({"id": i, "check": "official_mcp_weak_evidence", "detail": x.mcp.official_url})
        if x.access.tier == "free_self_serve" and x.access.paid_plan_required == "yes":
            issues.append({"id": i, "check": "tier_contradicts_paid_flag", "detail": ""})
        if x.access.tier == "free_self_serve" and x.access.partnership_or_sales_required == "yes":
            issues.append({"id": i, "check": "tier_contradicts_partner_flag", "detail": ""})
        for c in x.claims:
            if not URL_RE.match(c.url):
                issues.append({"id": i, "check": "bad_url", "detail": c.url[:80]})
        if x.identity.identity_confirmed != "yes":
            issues.append({"id": i, "check": "identity_unconfirmed", "detail": x.identity.identity_notes[:120]})
    return issues


# ---------------------------------------------------------------- Level 2 reconcile
FIELD_CLAIM = {"auth_methods": "auth", "access_tier": "access", "protocols": "api.protocol",
               "api_breadth": "api.breadth", "official_mcp": "mcp"}


def supported(r: AppRecord | None, field: str) -> bool:
    if r is None or r.error:
        return False
    k = FIELD_CLAIM[field]
    return any(c.verified and c.field.lower().startswith(k) for c in r.extraction.claims)


def reconcile(a: AppRecord | None, b: AppRecord | None) -> tuple[Extraction, list[dict]]:
    """Start from pass A; change a field only when the evidence rules say so."""
    base = a if a and not a.error else (b if b and not b.error else None)
    changes = []
    if base is None:
        changes.append({"field": "*", "rule": "R0 both passes failed; all fields unknown", "from": None, "to": None})
        return Extraction(), changes
    x = base.extraction.model_copy(deep=True)
    if base is b:
        changes.append({"field": "*", "rule": "R0 pass A failed; pass B used", "from": None, "to": "pass B"})
        return x, changes
    for field in ["auth_methods", "access_tier", "protocols", "api_breadth", "official_mcp"]:
        va, vb = value(a, field), value(b, field)
        rel = compare(va, vb, field)
        sa, sb = supported(a, field), supported(b, field)
        new, rule = None, None
        if rel in ("agree",) or vb is None:
            continue
        if is_unknown(va) and not is_unknown(vb) and sb:
            new, rule = vb, "R1 gap-fill: A unknown, B has verified evidence"
        elif rel == "partial" and isinstance(va, list) and sb and set(vb) - set(va):
            u = set(va) | set(vb)
            if len(u) > 1:
                u.discard("none")  # 'no public API' cannot coexist with real protocols
            new, rule = sorted(u), "R2 union: B adds methods backed by verified evidence"
            if new == sorted(va):
                new, rule = None, None
        elif rel in ("contradiction", "partial") and not isinstance(va, list) and sb and not sa:
            new, rule = vb, "R3 override: only B's value has verified evidence"
        elif rel == "contradiction" and not sa and not sb:
            new, rule = ("unknown" if not isinstance(va, list) else []), "R4 abstain: conflicting and neither verified"
        if rule is None:
            continue
        changes.append({"field": field, "rule": rule, "from": va, "to": new})
        if field == "auth_methods":
            x.auth.methods = new
        elif field == "access_tier":
            x.access.tier = new
        elif field == "protocols":
            x.api.protocols = new
        elif field == "api_breadth":
            x.api.breadth = new if new != "unknown" else "Unknown"
        elif field == "official_mcp":
            x.mcp.official = new
            if new == "yes" and b:
                x.mcp.official_url = b.extraction.mcp.official_url
        # carry B's verified claims for the changed field as evidence
        k = FIELD_CLAIM[field]
        x.claims += [c for c in b.extraction.claims if c.verified and c.field.lower().startswith(k)]
    if not set(x.auth.methods) & {x.auth.primary}:
        x.auth.primary = x.auth.methods[0] if x.auth.methods else None
    return x, changes


# ---------------------------------------------------------------- Level 3
def audit_sample(final: dict, n_per_cat: int = 2, seed: str = "atlas-2026") -> list[int]:
    """Deterministic stratified sample: per category, 1 app with an A/B disagreement
    (if any) + the rest by seeded hash order. Fixed seed => reproducible."""
    picks = []
    by_cat: dict[str, list] = {}
    for r in final.values():
        by_cat.setdefault(r["category"], []).append(r)
    for cat in registry.CATEGORIES:
        rows = sorted(by_cat.get(cat, []),
                      key=lambda r: hashlib.sha256(f"{seed}:{r['id']}".encode()).hexdigest())
        dis = [r for r in rows if any(v in ("contradiction", "partial") for v in r["agreement"].values())]
        chosen = dis[:1]
        for r in rows:
            if len(chosen) >= n_per_cat:
                break
            if r not in chosen:
                chosen.append(r)
        picks += [r["id"] for r in chosen]
    return sorted(picks)


AUDIT_COLS = ["app_id", "app", "category", "field", "first_pass", "second_pass", "corrected",
              "source_urls", "supporting_excerpt", "human_ground_truth", "first_pass_correct",
              "corrected_correct", "error_category", "correction_note", "reviewer", "review_date"]
ERROR_CATS = "wrong_value|missing_value|over_inclusion|source_misread|outdated_source|identity_error|unresolvable"


def fmt(v):
    return "; ".join(v) if isinstance(v, list) else ("" if v is None else str(v))


def write_worksheet(final: dict, ids: list[int], a: dict, b: dict):
    AUDIT.mkdir(parents=True, exist_ok=True)
    path = AUDIT / "human_audit_worksheet.csv"
    if path.exists() and any(row.get("human_ground_truth") for row in csv.DictReader(path.open())):
        print(f"! {path} already has human labels — not overwriting")
        return path
    with path.open("w", newline="") as fh:
        w = csv.DictWriter(fh, AUDIT_COLS)
        w.writeheader()
        for i in ids:
            r = final[i]
            for field in CORE_FIELDS:
                k = FIELD_CLAIM.get(field, "access")
                ev = [c for c in r["extraction"]["claims"] if c["verified"] and c["field"].lower().startswith(k)]
                w.writerow({"app_id": i, "app": r["name"], "category": r["category"], "field": field,
                            "first_pass": fmt(value(a.get(i), field)),
                            "second_pass": fmt(value(b.get(i), field)),
                            "corrected": fmt(r["fields"][field]),
                            "source_urls": " ".join(dict.fromkeys(c["url"] for c in ev[:3])),
                            "supporting_excerpt": ev[0]["quote"][:300] if ev else ""})
    return path


def score(final: dict) -> dict:
    """Accuracy from HUMAN labels only. Returns {'status': 'pending'} if none."""
    path = AUDIT / "human_audit_worksheet.csv"
    if not path.exists():
        return {"status": "pending", "reason": "worksheet not generated"}
    rows = [r for r in csv.DictReader(path.open()) if r["human_ground_truth"].strip()]
    if not rows:
        return {"status": "pending", "reason": "no human labels entered yet",
                "worksheet": "data/audit/human_audit_worksheet.csv"}

    def norm(v: str):
        parts = sorted(p.strip().lower() for p in re.split(r"[;,]", v) if p.strip())
        return parts

    def correct(pred: str, truth: str) -> bool:
        # Unknown is never credited as correct (unless truth itself is 'unknown').
        return norm(pred) == norm(truth)

    res = {"status": "measured", "fields_evaluated": len(rows),
           "apps_evaluated": len({r["app_id"] for r in rows}),
           "reviewers": sorted({r["reviewer"] for r in rows if r["reviewer"]})}
    for col in ("first_pass", "second_pass", "corrected"):
        ok = [correct(r[col], r["human_ground_truth"]) for r in rows]
        res[f"{col}_accuracy"] = round(sum(ok) / len(ok), 4)
        res[f"{col}_correct"] = sum(ok)
        unk = [r for r in rows if is_unknown(r[col].strip() or None)]
        res[f"{col}_unknown"] = len(unk)
        by_app: dict[str, list] = {}
        for r, k in zip(rows, ok):
            by_app.setdefault(r["app_id"], []).append(k)
        res[f"{col}_app_exact"] = round(sum(all(v) for v in by_app.values()) / len(by_app), 4)
    per_field = {}
    for f in CORE_FIELDS:
        fr = [r for r in rows if r["field"] == f]
        if fr:
            per_field[f] = {c: round(sum(correct(r[c], r["human_ground_truth"]) for r in fr) / len(fr), 3)
                            for c in ("first_pass", "corrected")} | {"n": len(fr)}
    res["per_field"] = per_field
    res["errors"] = [{k: r[k] for k in ("app", "field", "first_pass", "corrected", "human_ground_truth",
                                        "error_category", "correction_note", "source_urls")}
                     for r in rows if not correct(r["corrected"], r["human_ground_truth"])
                     or not correct(r["first_pass"], r["human_ground_truth"])]
    return res


# ---------------------------------------------------------------- main
def main():
    a, b = load_pass("a"), load_pass("b")
    OUT.mkdir(parents=True, exist_ok=True)
    final, corrections = {}, []
    for app in registry.load():
        i = app["id"]
        ra, rb = a.get(i), b.get(i)
        if ra is None and rb is None:
            continue
        x, changes = reconcile(ra, rb)
        asm = stages.assess(x, app["category"])
        agreement = {f: compare(value(ra, f), value(rb, f), f) for f in CORE_FIELDS}
        flags = []
        if any(v == "contradiction" for v in agreement.values()):
            flags.append("contradiction")
        if asm.verdict == "UNKNOWN":
            flags.append("unresolved")
        if x.identity.identity_confirmed != "yes":
            flags.append("identity_unconfirmed")
        if any("R4" in c["rule"] for c in changes):
            flags.append("needs_human_review")
        if x.mcp.official == "yes" and "mcp" not in (x.mcp.official_url or "").lower() and not any(
                c.verified and c.field.lower().startswith("mcp") and "mcp" in (c.quote + c.url).lower()
                for c in x.claims):
            flags.append("official_mcp_weak_evidence")
        claims = x.claims
        sup = round(sum(1 for c in claims if c.verified) / len(claims), 3) if claims else None
        rec = {
            "id": i, "name": app["name"], "category": app["category"], "hint": app["hint"],
            "extraction": json.loads(x.model_dump_json()), "assessment": json.loads(asm.model_dump_json()),
            "fields": {"auth_methods": sorted(set(x.auth.methods)), "access_tier": x.access.tier,
                       "protocols": sorted(set(x.api.protocols)), "api_breadth": x.api.breadth,
                       "official_mcp": x.mcp.official, "verdict": asm.verdict},
            "first_pass": {f: value(ra, f) for f in CORE_FIELDS},
            "second_pass": {f: value(rb, f) for f in CORE_FIELDS},
            "agreement": agreement, "corrections": changes, "flags": flags,
            "evidence_support_rate": sup,
            "fields_supported": {f: supported_x(x, f) for f in FIELD_CLAIM},
            "researched_at": (ra or rb).researched_at,
            "cost_usd": round(sum(r.cost_usd or 0 for r in (ra, rb) if r), 4),
            "duration_s": round(sum(r.duration_s for r in (ra, rb) if r), 1),
            "pass_a_error": ra.error if ra else "not run", "pass_b_error": rb.error if rb else "not run",
            "sources": (ra.sources if ra else []),
        }
        final[i] = rec
        corrections += [{"id": i, "app": app["name"], **c} for c in changes]
    issues = level1({**{i: r for i, r in a.items()}})
    ids = audit_sample(final) if len(final) >= 20 else sorted(final)
    ws = write_worksheet(final, ids, a, b)
    acc = score(final)
    meta = {"generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pass_a_count": len(a), "pass_a_ok": sum(1 for r in a.values() if not r.error),
            "pass_b_count": len(b), "pass_b_ok": sum(1 for r in b.values() if not r.error),
            "audit_sample_ids": ids, "level1_issues": issues, "human_accuracy": acc,
            "corrections": corrections}
    (OUT / "atlas.json").write_text(json.dumps({"meta": meta, "apps": list(final.values())}, indent=1, default=str))
    # immutable snapshot of the first pass, as produced
    (OUT / "first_pass_snapshot.json").write_text(json.dumps(
        {i: json.loads(r.model_dump_json()) for i, r in a.items()}, indent=1))
    agg = Counter(v for r in final.values() for v in r["agreement"].values())
    print(f"final records: {len(final)}  pass A ok {meta['pass_a_ok']}/{len(a)}  pass B ok {meta['pass_b_ok']}/{len(b)}")
    print(f"level1 issues: {Counter(i['check'] for i in issues)}")
    print(f"A-vs-B field agreement: {dict(agg)}")
    print(f"corrections applied: {Counter(c['rule'][:2] for c in corrections)}")
    print(f"audit sample ({len(ids)}): {ids}\nworksheet: {ws}\nhuman accuracy: {acc.get('status')}")


def supported_x(x: Extraction, field: str) -> bool:
    k = FIELD_CLAIM[field]
    return any(c.verified and c.field.lower().startswith(k) for c in x.claims)
