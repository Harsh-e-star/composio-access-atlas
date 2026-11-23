"""Database service layer supporting SQLite and JSON data stores with thread-safe access.
"""
from __future__ import annotations
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
DB_PATH = DATA_DIR / "apps.db"
JSON_PATH = DATA_DIR / "apps.json"


def get_db_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_all_apps() -> List[Dict[str, Any]]:
    if not DB_PATH.exists() or not JSON_PATH.exists():
        # Fallback to importing
        from app.dataset import ALL_APPS
        return ALL_APPS
        
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM apps ORDER BY id ASC")
    rows = cur.fetchall()
    conn.close()
    
    result = []
    for r in rows:
        d = dict(r)
        d["auth_methods"] = json.loads(d["auth_methods"]) if d.get("auth_methods") else []
        d["documentation_urls"] = json.loads(d["documentation_urls"]) if d.get("documentation_urls") else []
        d["evidence_excerpts"] = json.loads(d["evidence_excerpts"]) if d.get("evidence_excerpts") else []
        d["free_trial_available"] = bool(d["free_trial_available"])
        d["paid_plan_required"] = bool(d["paid_plan_required"])
        d["admin_approval_required"] = bool(d["admin_approval_required"])
        d["partnership_required"] = bool(d["partnership_required"])
        d["multiple_auth_supported"] = bool(d["multiple_auth_supported"])
        d["disagreement_flag"] = bool(d.get("disagreement_flag", 0))
        result.append(d)
        
    return result


def get_app_by_id(app_id: int) -> Optional[Dict[str, Any]]:
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM apps WHERE id = ?", (app_id,))
    row = cur.fetchone()
    conn.close()
    
    if not row:
        return None
        
    d = dict(row)
    d["auth_methods"] = json.loads(d["auth_methods"]) if d.get("auth_methods") else []
    d["documentation_urls"] = json.loads(d["documentation_urls"]) if d.get("documentation_urls") else []
    d["evidence_excerpts"] = json.loads(d["evidence_excerpts"]) if d.get("evidence_excerpts") else []
    d["free_trial_available"] = bool(d["free_trial_available"])
    d["paid_plan_required"] = bool(d["paid_plan_required"])
    d["admin_approval_required"] = bool(d["admin_approval_required"])
    d["partnership_required"] = bool(d["partnership_required"])
    d["multiple_auth_supported"] = bool(d["multiple_auth_supported"])
    d["disagreement_flag"] = bool(d.get("disagreement_flag", 0))
    return d


def update_app_record(app_id: int, updated: Dict[str, Any]) -> bool:
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("""
    UPDATE apps SET
        primary_auth = ?,
        auth_methods = ?,
        auth_details = ?,
        api_type = ?,
        api_surface = ?,
        official_mcp = ?,
        community_mcp = ?,
        access_tier = ?,
        buildability = ?,
        main_blocker = ?,
        recommended_next_step = ?,
        confidence_score = ?,
        documentation_urls = ?,
        evidence_excerpts = ?,
        research_timestamp = ?,
        verification_status = ?
    WHERE id = ?
    """, (
        updated.get("primary_auth"),
        json.dumps(updated.get("auth_methods", [])),
        updated.get("auth_details"),
        updated.get("api_type"),
        updated.get("api_surface"),
        updated.get("official_mcp"),
        updated.get("community_mcp"),
        updated.get("access_tier"),
        updated.get("buildability"),
        updated.get("main_blocker"),
        updated.get("recommended_next_step"),
        updated.get("confidence_score"),
        json.dumps(updated.get("documentation_urls", [])),
        json.dumps(updated.get("evidence_excerpts", [])),
        updated.get("research_timestamp"),
        updated.get("verification_status"),
        app_id
    ))
    
    conn.commit()
    conn.close()
    
    # Also sync apps.json
    all_apps = get_all_apps()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_apps, f, indent=2, ensure_ascii=False)
        
    return True
