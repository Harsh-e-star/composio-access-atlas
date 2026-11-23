"""Pattern analysis over the reconciled dataset. Every number carries its denominator."""
from __future__ import annotations

from collections import Counter, defaultdict

from . import registry

AUTH = ["OAuth2", "API key", "Bearer/PAT", "Basic", "Service account/JWT", "Other"]
TIERS = ["free_self_serve", "trial_self_serve", "paid_plan", "admin_approval", "partner_or_sales", "unknown"]
VERDICTS = ["READY", "CONDITIONAL", "GATED", "NO_SUPPORTED_INTERFACE", "UNKNOWN"]


def pct(n, d):
    return round(100 * n / d, 1) if d else None


def compute(apps: list[dict]) -> dict:
    N = len(apps)
    F = lambda a, k: a["fields"][k]
    auth = Counter(m for a in apps for m in F(a, "auth_methods"))
    auth_known = sum(1 for a in apps if F(a, "auth_methods"))
    multi = sum(1 for a in apps if len(F(a, "auth_methods")) > 1)
    only = Counter(F(a, "auth_methods")[0] for a in apps if len(F(a, "auth_methods")) == 1)
    tiers = Counter(F(a, "access_tier") for a in apps)
    verdicts = Counter(F(a, "verdict") for a in apps)
    groups = Counter(a["assessment"]["group"] for a in apps)
    cat = {}
    for c in registry.CATEGORIES:
        rows = [a for a in apps if a["category"] == c]
        v = Counter(F(a, "verdict") for a in rows)
        t = Counter(F(a, "access_tier") for a in rows)
        cat[c] = {"n": len(rows), "verdicts": {k: v.get(k, 0) for k in VERDICTS},
                  "tiers": {k: t.get(k, 0) for k in TIERS},
                  "self_serve": t["free_self_serve"] + t["trial_self_serve"],
                  "gated": t["partner_or_sales"], "conditional": t["paid_plan"] + t["admin_approval"],
                  "official_mcp": sum(1 for a in rows if F(a, "official_mcp") == "yes"),
                  "oauth": sum(1 for a in rows if "OAuth2" in F(a, "auth_methods"))}
    blockers = Counter(a["assessment"]["main_blocker"] for a in apps
                       if a["assessment"]["verdict"] in ("CONDITIONAL", "GATED", "NO_SUPPORTED_INTERFACE"))
    mcp_off = [a["name"] for a in apps if F(a, "official_mcp") == "yes"]
    # heuristic evidence strength: official MCP URL is on the vendor's own domain / repo and mentions mcp
    def _vendor_hosted(a):
        import re as _re
        from urllib.parse import urlparse
        u = (a["extraction"]["mcp"]["official_url"] or "").lower()
        site = (a["extraction"]["identity"]["official_website"] or "").lower()
        host = urlparse(u).netloc
        sd = ".".join(urlparse(site).netloc.split(".")[-2:])
        tok = _re.sub(r"[^a-z]", "", a["name"].lower().split()[0])[:5]
        return "mcp" in u and bool((sd and sd in host) or tok in host or ("github.com" in host and tok in u))
    mcp_strong = sum(1 for a in apps if F(a, "official_mcp") == "yes" and _vendor_hosted(a))
    mcp_unknown = sum(1 for a in apps if F(a, "official_mcp") == "unknown")
    comm = [a for a in apps if a["extraction"]["mcp"]["community"] == "yes"]
    comm_by_cat = Counter(a["category"] for a in comm)
    agree = Counter(v for a in apps for v in a["agreement"].values())
    fields_total = N * 5
    supported = sum(sum(a["fields_supported"].values()) for a in apps)
    unknown_fields = sum(1 for a in apps for k in ("auth_methods", "access_tier", "protocols", "api_breadth", "official_mcp")
                         if a["fields"][k] in ([], "unknown", "Unknown"))
    costs = [a["cost_usd"] for a in apps if a["cost_usd"]]
    durs = [a["duration_s"] for a in apps if a["duration_s"]]
    claims = [c for a in apps for c in a["extraction"]["claims"]]
    admin = [a["name"] for a in apps if F(a, "access_tier") == "admin_approval"
             or a["extraction"]["access"]["admin_approval_required"] == "yes"]
    outreach = [a["name"] for a in apps if a["assessment"]["group"] == "OUTREACH REQUIRED"]
    research = [a["name"] for a in apps if a["assessment"]["group"] == "RESEARCH FURTHER"]
    build_now = [a["name"] for a in apps if a["assessment"]["group"] == "BUILD NOW"]
    prereq = [a["name"] for a in apps if a["assessment"]["group"] == "BUILD WITH PREREQUISITES"]
    # lowest friction: READY + static key/PAT (no OAuth app registration needed)
    low_friction = [a["name"] for a in apps if F(a, "verdict") == "READY"
                    and set(F(a, "auth_methods")) & {"API key", "Bearer/PAT"}]
    oauth_only_ready = [a["name"] for a in apps if F(a, "verdict") == "READY"
                        and F(a, "auth_methods") == ["OAuth2"]]
    custom_over_mcp = [a["name"] for a in apps if F(a, "official_mcp") != "yes"
                       and F(a, "verdict") in ("READY", "CONDITIONAL") and a["fields"]["api_breadth"] == "Broad"]
    return {
        "n": N,
        "auth": {"counts": {k: auth.get(k, 0) for k in AUTH}, "known": auth_known, "multi": multi,
                 "single_method": dict(only)},
        "tiers": {k: tiers.get(k, 0) for k in TIERS},
        "verdicts": {k: verdicts.get(k, 0) for k in VERDICTS},
        "groups": dict(groups), "categories": cat, "blockers": blockers.most_common(),
        "mcp": {"official": mcp_off, "vendor_hosted": mcp_strong, "unknown": mcp_unknown, "community_n": len(comm),
                "community_by_cat": dict(comm_by_cat)},
        "agreement": dict(agree),
        "coverage": {"supported_fields": supported, "total_fields": fields_total,
                     "pct": pct(supported, fields_total), "unknown_fields": unknown_fields},
        "claims": {"total": len(claims), "verified": sum(1 for c in claims if c["verified"])},
        "cost": {"total": round(sum(costs), 2), "per_app": round(sum(costs) / len(costs), 3) if costs else None},
        "duration": {"per_app_s": round(sum(durs) / len(durs), 1) if durs else None},
        "lists": {"admin": admin, "outreach": outreach, "research": research, "build_now": build_now,
                  "prereq": prereq, "low_friction": low_friction, "oauth_only_ready": oauth_only_ready,
                  "custom_over_mcp": custom_over_mcp},
        "flags": Counter(f for a in apps for f in a["flags"]),
    }
