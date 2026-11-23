"""Export all 100 apps x 6 core fields (600 rows) from data/final/atlas.json.
Read-only: does not re-run research or modify any stored prediction.

    python -m agent.export_full
"""
from __future__ import annotations

import csv, json
from pathlib import Path

from .schema import CORE_FIELDS
from .verify import FIELD_CLAIM

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "composio_100_apps_full_export.csv"
COLS = ["app_id", "app", "category", "field", "first_pass", "second_pass", "corrected",
        "pass_agreement", "corrected_is_unknown", "evidence_status", "official_doc_urls",
        "supporting_excerpt", "first_pass_researched_at", "pass_a_error", "pass_b_error",
        "correction_rule", "flags", "human_review_status"]


def fmt(v):
    if v is None:
        return ""
    return "; ".join(v) if isinstance(v, list) else str(v)


def unknown(v):
    return v in (None, [], "", "unknown", "Unknown", "UNKNOWN")


def main():
    atlas = json.loads((ROOT / "data" / "final" / "atlas.json").read_text())
    rows = []
    for a in sorted(atlas["apps"], key=lambda r: r["id"]):
        claims = a["extraction"]["claims"]
        for f in CORE_FIELDS:
            key = FIELD_CLAIM.get(f, "access")  # verdict is derived from access tier
            ev = [c for c in claims if c["field"].lower().startswith(key)]
            ver = [c for c in ev if c.get("verified")]
            status = ("verified_quote" if ver else
                      "quote_not_found_on_page" if ev else "NO_EVIDENCE")
            src = ver or ev
            corr = [c["rule"] for c in a["corrections"] if c["field"] in (f, "*")]
            rows.append({
                "app_id": a["id"], "app": a["name"], "category": a["category"], "field": f,
                "first_pass": fmt(a["first_pass"][f]) or "(pass A failed)" if a["pass_a_error"] else fmt(a["first_pass"][f]),
                "second_pass": fmt(a["second_pass"][f]),
                "corrected": fmt(a["fields"][f]),
                "pass_agreement": a["agreement"][f],
                "corrected_is_unknown": "yes" if unknown(a["fields"][f]) else "no",
                "evidence_status": status,
                "official_doc_urls": " ".join(dict.fromkeys(c["url"] for c in src[:3])) or "NO_EVIDENCE",
                "supporting_excerpt": (src[0]["quote"][:400] if src else "NO_EVIDENCE"),
                "first_pass_researched_at": a["researched_at"],
                "pass_a_error": a["pass_a_error"] or "", "pass_b_error": a["pass_b_error"] or "",
                "correction_rule": " | ".join(corr),
                "flags": "; ".join(a["flags"]),
                "human_review_status": "not reviewed",
            })
    with OUT.open("w", newline="") as fh:
        w = csv.DictWriter(fh, COLS)
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {OUT} ({len(rows)} rows)")


if __name__ == "__main__":
    main()
