"""Accuracy evaluation with honest labels.

1. AI-referenced (external AI review, sources re-fetched by us): first pass vs the
   verification loop's reconciled output BEFORE the R5 layer (otherwise corrected values
   would trivially match the reference they were corrected to). Small, non-random
   sample: these fields were selected by the reviewer because they looked suspect.
2. Human: self-reported spot check (18/20) kept separately; documented rows in
   data/audit/human_spotcheck_log.csv are scored only when filled in by the human.
"""
import csv, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
A = ROOT / "data" / "audit"


def norm(v):
    if v is None:
        return []
    if isinstance(v, list):
        return sorted(x.lower() for x in v)
    return sorted(p.strip().lower() for p in str(v).split(";") if p.strip())


def pre_r5(app, field):
    for c in app["corrections"]:
        if c["rule"].startswith("R5") and c["field"] == field:
            return c["from"]
    return app["fields"][field]


def main():
    atlas = json.loads((ROOT / "data" / "final" / "atlas.json").read_text())
    apps = {a["name"]: a for a in atlas["apps"]}
    dec = json.loads((A / "external_ai_review" / "correction_decisions.json").read_text())
    refs = [(d["app"], d["field"], d["proposed"], "correction") for d in dec
            if d["decision"] == "ACCEPTED" and d["field"] != "*"]
    for r in csv.DictReader(open(A / "external_ai_review" / "composio_reviewer_style_ai_audit_600.csv", encoding="utf-8-sig")):
        if r["adjudication_status"] == "SOURCE_CHECKED_CONFIRMATION":
            refs.append((r["app"], r["field"], r["suggested_reference_value"], "confirmation"))
    rows = []
    for app, field, ref, kind in refs:
        a = apps[app]
        fp, rc = a["first_pass"][field], pre_r5(a, field)
        rows.append({"app": app, "field": field, "kind": kind, "ai_reference": ref,
                     "first_pass": "; ".join(fp) if isinstance(fp, list) else fp,
                     "loop_corrected_pre_R5": "; ".join(rc) if isinstance(rc, list) else rc,
                     "first_pass_match": norm(fp) == norm(ref) and bool(norm(ref)),
                     "corrected_match": norm(rc) == norm(ref) and bool(norm(ref))})
    n = len(rows)
    fpk = sum(r["first_pass_match"] for r in rows); ck = sum(r["corrected_match"] for r in rows)
    human = json.loads((A / "human_review_status.json").read_text())
    log = [r for r in csv.DictReader(open(A / "human_spotcheck_log.csv")) if r["human_verdict"].strip()]
    documented = {"rows_documented": len(log),
                  "correct": sum(r["human_verdict"].strip().lower() == "correct" for r in log)}
    res = {
        "ai_referenced": {
            "label": "AI-referenced (external AI review; official sources re-fetched by pipeline). NOT human ground truth.",
            "sample": "Non-random: fields the reviewer flagged as suspect, plus 4 confirmations. Biased toward errors.",
            "n_fields": n, "first_pass_correct": fpk, "corrected_correct": ck,
            "first_pass_accuracy": round(fpk / n, 3), "corrected_accuracy": round(ck / n, 3),
            "note": "Corrected = verification-loop output before applying these reference corrections (no leakage).",
            "rows": rows},
        "human": {**human, "documented_rows": documented},
    }
    (A / "composio_accuracy_evaluation.json").write_text(json.dumps(res, indent=1))
    with open(A / "composio_ai_referenced_rows.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"AI-referenced: first pass {fpk}/{n}, loop-corrected {ck}/{n}")
    print(f"human: {human['label']}; documented rows {documented}")


if __name__ == "__main__":
    main()
