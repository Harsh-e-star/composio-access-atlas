"""Strict research schema. Tri-state fields keep 'unknown' distinct from 'no'."""
from __future__ import annotations

from typing import Literal, Optional
from pydantic import BaseModel, Field, field_validator

Tri = Literal["yes", "no", "unknown"]
AuthMethod = Literal["OAuth2", "API key", "Bearer/PAT", "Basic", "Service account/JWT", "Other"]
AccessTier = Literal["free_self_serve", "trial_self_serve", "paid_plan", "admin_approval",
                     "partner_or_sales", "unknown"]
Protocol = Literal["REST", "GraphQL", "gRPC", "SOAP", "WebSocket", "CLI/library", "none"]
Breadth = Literal["Broad", "Medium", "Limited", "Unknown"]
Verdict = Literal["READY", "CONDITIONAL", "GATED", "NO_SUPPORTED_INTERFACE", "UNKNOWN"]
Group = Literal["BUILD NOW", "BUILD WITH PREREQUISITES", "OUTREACH REQUIRED", "RESEARCH FURTHER"]

# Fields compared across passes and checked by humans.
CORE_FIELDS = ["auth_methods", "access_tier", "protocols", "api_breadth", "official_mcp", "verdict"]


class Identity(BaseModel):
    official_website: Optional[str] = None
    developer_portal: Optional[str] = None
    description: str = ""
    identity_confirmed: Tri = "unknown"
    identity_notes: str = ""


class Auth(BaseModel):
    methods: list[AuthMethod] = []
    primary: Optional[AuthMethod] = None
    oauth_flows: str = ""
    token_refresh: str = ""
    scopes_notes: str = ""


class Access(BaseModel):
    tier: AccessTier = "unknown"
    free_credentials: Tri = "unknown"
    trial_available: Tri = "unknown"
    paid_plan_required: Tri = "unknown"
    admin_approval_required: Tri = "unknown"
    provider_app_review: Tri = "unknown"
    partnership_or_sales_required: Tri = "unknown"
    sandbox_available: Tri = "unknown"
    production_restrictions: str = ""


class Api(BaseModel):
    protocols: list[Protocol] = []
    breadth: Breadth = "Unknown"
    resources: list[str] = []
    read_ops: list[str] = []
    write_ops: list[str] = []
    webhooks: Tri = "unknown"
    sdks: Tri = "unknown"
    rate_limits: str = ""
    limitations: str = ""


class Mcp(BaseModel):
    official: Tri = "unknown"
    official_url: Optional[str] = None
    community: Tri = "unknown"
    community_urls: list[str] = []


class Claim(BaseModel):
    field: str
    value: str
    url: str
    quote: str = ""
    # filled by Stage 6
    verified: Optional[bool] = None
    verify_note: str = ""


class Extraction(BaseModel):
    """What an LLM research pass must return."""
    identity: Identity = Identity()
    auth: Auth = Auth()
    access: Access = Access()
    api: Api = Api()
    mcp: Mcp = Mcp()
    claims: list[Claim] = []
    open_questions: list[str] = []

    @field_validator("claims")
    @classmethod
    def _cap(cls, v):
        return v[:40]


class Assessment(BaseModel):
    verdict: Verdict
    group: Group
    technical_feasibility: Literal["high", "medium", "low", "unknown"]
    credential_accessibility: Literal["self-serve", "conditional", "gated", "unknown"]
    production_readiness: Literal["open", "review_required", "restricted", "unknown"]
    security_risk: Literal["standard", "elevated", "high"]
    commercial_dependency: Tri
    approach: str
    main_blocker: str
    rationale: list[str]


class AppRecord(BaseModel):
    id: int = Field(ge=1, le=100)
    name: str
    category: str
    pass_name: str
    model: str = ""
    researched_at: str
    duration_s: float = 0
    cost_usd: Optional[float] = None
    sources: list[dict] = []          # pages actually fetched/read
    extraction: Extraction
    assessment: Optional[Assessment] = None
    evidence_support_rate: Optional[float] = None
    flags: list[str] = []
    error: Optional[str] = None
