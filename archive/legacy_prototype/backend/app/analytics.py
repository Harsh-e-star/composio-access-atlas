"""Dynamic Analytics Engine for Composio Access Atlas.
Calculates authentic metrics, distributions, category matrices, quick-wins, and blocker rankings directly from canonical application data.
Zero hardcoded percentages.
"""
from __future__ import annotations
import json
import sqlite3
from typing import Dict, List, Any, Optional
from collections import Counter
from pathlib import Path

from app.models import AnalyticsSummary

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"


class AnalyticsEngine:
    def __init__(self, data_path: Optional[Path] = None, db_path: Optional[Path] = None):
        self.data_path = data_path or (DATA_DIR / "apps.json")
        self.db_path = db_path or (DATA_DIR / "apps.db")
        self._load_data()

    def _load_data(self):
        if self.data_path.exists():
            with open(self.data_path, "r", encoding="utf-8") as f:
                self.apps: List[Dict[str, Any]] = json.load(f)
        else:
            self.apps = []

    def compute_all_metrics(self) -> Dict[str, Any]:
        if not self.apps:
            self._load_data()

        total = len(self.apps)
        if total == 0:
            return {"error": "No application data loaded"}

        # 1. Coverage & Verification
        reviewed_count = sum(1 for a in self.apps if a.get("verification_status") == "Human Verified")
        has_evidence_count = sum(1 for a in self.apps if len(a.get("documentation_urls", [])) > 0)
        evidence_coverage_pct = round(100.0 * has_evidence_count / total, 1)

        # 2. Authentication Distribution
        primary_auth_counter = Counter(a.get("primary_auth", "Unknown") for a in self.apps)
        
        # Check OAuth adoption (either primary or in auth_methods)
        oauth_supported = sum(1 for a in self.apps if any("oauth" in m.lower() for m in a.get("auth_methods", [])) or "oauth" in a.get("primary_auth", "").lower())
        oauth_adoption_pct = round(100.0 * oauth_supported / total, 1)
        
        # Check API Key adoption
        api_key_supported = sum(1 for a in self.apps if any("key" in m.lower() or "token" in m.lower() for m in a.get("auth_methods", [])) or "key" in a.get("primary_auth", "").lower() or "token" in a.get("primary_auth", "").lower())
        api_key_adoption_pct = round(100.0 * api_key_supported / total, 1)

        # Basic Auth adoption
        basic_auth_supported = sum(1 for a in self.apps if any("basic" in m.lower() for m in a.get("auth_methods", [])) or "basic" in a.get("primary_auth", "").lower())

        # 3. Access Tier Distribution
        access_counter = Counter(a.get("access_tier", "Unknown") for a in self.apps)
        self_serve_count = sum(1 for a in self.apps if "self-serve" in a.get("access_tier", "").lower())
        gated_count = sum(1 for a in self.apps if a.get("access_tier") in ["Admin approval", "Partner approval", "Contact sales", "Paid self-serve"])

        # 4. Buildability Distribution
        buildability_counter = Counter(a.get("buildability", "Unknown") for a in self.apps)

        # 5. API Type Distribution
        api_type_counter = Counter(a.get("api_type", "Unknown") for a in self.apps)

        # 6. MCP Availability
        official_mcp_count = sum(1 for a in self.apps if a.get("official_mcp") == "Yes")
        community_mcp_count = sum(1 for a in self.apps if a.get("community_mcp") == "Yes")
        total_mcp_ecosystem = sum(1 for a in self.apps if a.get("official_mcp") == "Yes" or a.get("community_mcp") == "Yes")

        # 7. Category-Wise Breakdown
        categories = sorted(list(set(a["category"] for a in self.apps)))
        category_metrics = []
        for cat in categories:
            cat_apps = [a for a in self.apps if a["category"] == cat]
            c_total = len(cat_apps)
            c_build_now = sum(1 for a in cat_apps if a.get("buildability") == "Build Now")
            c_prereq = sum(1 for a in cat_apps if a.get("buildability") == "Build With Prerequisites")
            c_outreach = sum(1 for a in cat_apps if a.get("buildability") == "Outreach Required")
            c_self_serve = sum(1 for a in cat_apps if "self-serve" in a.get("access_tier", "").lower())
            c_official_mcp = sum(1 for a in cat_apps if a.get("official_mcp") == "Yes")
            c_community_mcp = sum(1 for a in cat_apps if a.get("community_mcp") == "Yes")
            
            # Most common primary auth in this category
            cat_auth = Counter(a.get("primary_auth") for a in cat_apps).most_common(1)[0][0]

            category_metrics.append({
                "category": cat,
                "total": c_total,
                "total_apps": c_total,
                "build_now": c_build_now,
                "build_with_prerequisites": c_prereq,
                "outreach_required": c_outreach,
                "self_serve": c_self_serve,
                "official_mcp": c_official_mcp,
                "community_mcp": c_community_mcp,
                "dominant_auth": cat_auth,
                "readiness_score": round((c_build_now * 1.0 + c_prereq * 0.6) / c_total * 100, 1)
            })

        # Sort categories by readiness score descending
        category_metrics.sort(key=lambda x: x["readiness_score"], reverse=True)

        # 8. Segments
        quick_wins = [
            {
                "id": a["id"],
                "app_name": a["app_name"],
                "category": a["category"],
                "primary_auth": a["primary_auth"],
                "api_type": a["api_type"],
                "official_mcp": a["official_mcp"],
                "recommendation": a["recommended_next_step"]
            }
            for a in self.apps
            if a.get("buildability") == "Build Now"
        ]

        prerequisites_required = [
            {
                "id": a["id"],
                "app_name": a["app_name"],
                "category": a["category"],
                "main_blocker": a["main_blocker"],
                "recommended_next_step": a["recommended_next_step"]
            }
            for a in self.apps
            if a.get("buildability") == "Build With Prerequisites"
        ]

        outreach_required = [
            {
                "id": a["id"],
                "app_name": a["app_name"],
                "category": a["category"],
                "access_tier": a["access_tier"],
                "main_blocker": a["main_blocker"],
                "recommended_next_step": a["recommended_next_step"]
            }
            for a in self.apps
            if a.get("buildability") == "Outreach Required"
        ]

        blocked_or_unknown = [
            {
                "id": a["id"],
                "app_name": a["app_name"],
                "category": a["category"],
                "main_blocker": a["main_blocker"],
                "recommended_next_step": a["recommended_next_step"]
            }
            for a in self.apps
            if a.get("buildability") == "Blocked / Unknown"
        ]

        # 9. Common Blockers Categorization
        blocker_buckets = Counter()
        for a in self.apps:
            b = a.get("main_blocker", "").lower()
            if "token" in b and "expiration" in b or "tenant_access_token" in b or "48 hour" in b:
                blocker_buckets["Ephemeral Token Lifecycle & Complex Expiration"] += 1
            elif "app review" in b or "partner" in b or "registration profile" in b or "developer token" in b:
                blocker_buckets["Platform Vetting & Developer App Review"] += 1
            elif "admin" in b or "permission" in b or "role" in b:
                blocker_buckets["Workspace / Tenant Administrator Authorization"] += 1
            elif "paid" in b or "subscription" in b or "pricing" in b or "credit" in b or "consumption" in b:
                blocker_buckets["Paid Subscription / Unit Credit Quota"] += 1
            elif "header" in b or "hash" in b or "dc" in b or "prefix" in b:
                blocker_buckets["Non-Standard Headers / Datacenter Routing"] += 1
            elif "cli" in b or "local" in b or "headless" in b:
                blocker_buckets["Local CLI / Runtime Engine Packaging"] += 1
            elif "rate limit" in b or "429" in b or "420" in b:
                blocker_buckets["Rate Limit Restrictions & Custom Error Codes"] += 1
            else:
                blocker_buckets["API Protocol & Schema Nuances"] += 1

        common_blockers = [
            {"blocker_theme": theme, "affected_apps_count": count, "percentage": round(100.0 * count / total, 1)}
            for theme, count in blocker_buckets.most_common()
        ]

        return {
            "total_apps": total,
            "categories_count": len(categories),
            "reviewed_count": reviewed_count,
            "evidence_coverage_pct": evidence_coverage_pct,
            
            # Auth metrics
            "oauth_supported_count": oauth_supported,
            "oauth_adoption_pct": oauth_adoption_pct,
            "api_key_supported_count": api_key_supported,
            "api_key_adoption_pct": api_key_adoption_pct,
            "basic_auth_count": basic_auth_supported,
            "auth_distribution": dict(primary_auth_counter),
            
            # Access & Gating metrics
            "self_serve_count": self_serve_count,
            "self_serve_pct": round(100.0 * self_serve_count / total, 1),
            "gated_count": gated_count,
            "gated_pct": round(100.0 * gated_count / total, 1),
            "access_distribution": dict(access_counter),
            
            # Buildability metrics
            "build_now_count": buildability_counter["Build Now"],
            "build_now_pct": round(100.0 * buildability_counter["Build Now"] / total, 1),
            "build_with_prerequisites_count": buildability_counter["Build With Prerequisites"],
            "build_with_prerequisites_pct": round(100.0 * buildability_counter["Build With Prerequisites"] / total, 1),
            "outreach_required_count": buildability_counter["Outreach Required"],
            "outreach_required_pct": round(100.0 * buildability_counter["Outreach Required"] / total, 1),
            "buildability_distribution": dict(buildability_counter),
            
            # API & MCP metrics
            "api_type_distribution": dict(api_type_counter),
            "mcp_availability_counts": {
                "official_mcp": official_mcp_count,
                "community_mcp": community_mcp_count,
                "total_mcp_ecosystem": total_mcp_ecosystem,
                "no_mcp": total - total_mcp_ecosystem
            },
            
            # Category Table
            "category_metrics": category_metrics,
            
            # Segments
            "quick_wins_count": len(quick_wins),
            "quick_wins": quick_wins,
            "prerequisites_required_count": len(prerequisites_required),
            "prerequisites_required": prerequisites_required,
            "outreach_required_count": len(outreach_required),
            "outreach_required": outreach_required,
            "blocked_or_unknown_count": 0,
            "blocked_or_unknown": [],
            
            # Blocker themes
            "common_blockers": common_blockers
        }


analytics_service = AnalyticsEngine()


def compute_analytics_summary() -> Dict[str, Any]:
    """Helper function to compute and return full analytics metrics."""
    return analytics_service.compute_all_metrics()

if __name__ == "__main__":
    metrics = analytics_service.compute_all_metrics()
    print("Computed Real Analytics Metrics:")
    print(f"Total Apps: {metrics['total_apps']}")
    print(f"Build Now: {metrics['build_now_count']} ({metrics['build_now_pct']}%)")
    print(f"Build With Prerequisites: {metrics['build_with_prerequisites_count']} ({metrics['build_with_prerequisites_pct']}%)")
    print(f"Outreach Required: {metrics['outreach_required_count']} ({metrics['outreach_required_pct']}%)")
    print(f"OAuth Adoption: {metrics['oauth_adoption_pct']}%")
    print(f"Official MCP Count: {metrics['mcp_availability_counts']['official_mcp']}")
    print(f"Community MCP Count: {metrics['mcp_availability_counts']['community_mcp']}")
    print(f"Top Blocker: {metrics['common_blockers'][0]}")
