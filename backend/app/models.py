"""Pydantic data models for Composio Access Atlas 100-App Research & Verification Engine.
Strictly defines schema for application research records, analytics, agent tasks, and verification audits.
"""
from __future__ import annotations
from typing import List, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, HttpUrl


class EvidenceItem(BaseModel):
    url: str
    claim: str
    source_type: Literal["official_docs", "api_reference", "github_repo", "developer_portal", "help_center"] = "official_docs"


class AppRecord(BaseModel):
    id: int = Field(..., ge=1, le=100, description="Canonical ID 1-100")
    app_name: str = Field(..., description="Application name")
    category: str = Field(..., description="Category out of 10 assignment categories")
    website: str = Field(..., description="Starting hint / official website URL")
    description: str = Field(..., description="One-line functional description")
    
    # Authentication
    auth_methods: List[str] = Field(default_factory=list, description="List of supported auth methods e.g. OAuth2, API Key, Basic, PAT")
    primary_auth: str = Field(..., description="Primary or dominant authentication method")
    auth_details: str = Field(..., description="Detailed technical explanation of authentication mechanism")
    multiple_auth_supported: bool = Field(default=False, description="Whether multiple auth methods are supported")
    
    # API Surface & Protocol
    api_type: str = Field(..., description="Protocol: REST, GraphQL, gRPC, Bot API, Local CLI, etc.")
    api_surface: str = Field(..., description="API breadth description: data, webhooks, management, etc.")
    
    # MCP Availability
    official_mcp: Literal["Yes", "No", "Unknown"] = Field("Unknown", description="Official 1st-party MCP server availability")
    community_mcp: Literal["Yes", "No", "Unknown"] = Field("Unknown", description="Community MCP server availability")
    mcp_details: Optional[str] = Field(None, description="Details or repository/endpoint for MCP if present")
    
    # Access & Gating Tiers
    access_tier: Literal[
        "Free self-serve",
        "Trial self-serve",
        "Paid self-serve",
        "Admin approval",
        "Partner approval",
        "Contact sales",
        "Unknown"
    ] = Field(..., description="Classification of developer credential acquisition path")
    
    free_trial_available: bool = Field(default=False)
    paid_plan_required: bool = Field(default=False)
    admin_approval_required: bool = Field(default=False)
    partnership_required: bool = Field(default=False)
    
    # Buildability
    buildability: Literal[
        "Build Now",
        "Build With Prerequisites",
        "Outreach Required",
        "Blocked / Unknown"
    ] = Field(..., description="Composio agent toolkit buildability verdict")
    
    main_blocker: str = Field(..., description="Primary integration blocker or friction point")
    recommended_next_step: str = Field(..., description="Actionable recommendation for Composio product/engineering")
    
    # Evidence & Verification
    confidence_score: Literal["High", "Medium", "Low"] = Field("High")
    documentation_urls: List[str] = Field(default_factory=list, description="Official documentation URLs")
    evidence_excerpts: List[EvidenceItem] = Field(default_factory=list, description="Verified documentation claims and excerpts")
    research_timestamp: str = Field(..., description="ISO 8601 timestamp of research")
    verification_status: Literal["Human Verified", "Agent Verified", "Pending Review"] = Field("Human Verified")
    
    # Comparison & Audit fields
    first_pass_auth: Optional[str] = None
    first_pass_access: Optional[str] = None
    first_pass_surface: Optional[str] = None
    disagreement_flag: bool = False
    audit_notes: Optional[str] = None


class VerificationAuditEntry(BaseModel):
    app_id: int
    app_name: str
    category: str
    stratified_sample: bool = True
    first_pass_prediction: Dict[str, str]
    second_pass_verification: Dict[str, str]
    human_ground_truth: Dict[str, str]
    agreed_fields: List[str]
    discrepancies: List[str]
    error_type: Optional[str] = None
    correction_applied: Optional[str] = None
    evidence_urls: List[str]
    notes: str


class AccuracyMetrics(BaseModel):
    sample_size: int
    total_fields_evaluated: int
    first_pass_correct: int
    first_pass_accuracy: float
    second_pass_correct: int
    second_pass_accuracy: float
    human_verified_count: int
    error_taxonomy: Dict[str, int]
    methodology_statement: str


class AnalyticsSummary(BaseModel):
    total_apps: int = 100
    categories_count: int = 10
    reviewed_count: int
    evidence_coverage_pct: float
    
    # Distributions
    auth_distribution: Dict[str, int]
    access_distribution: Dict[str, int]
    buildability_distribution: Dict[str, int]
    api_type_distribution: Dict[str, int]
    mcp_availability_counts: Dict[str, int]
    
    # Category Breakdowns
    category_metrics: List[Dict[str, Any]]
    
    # Priority Segments
    quick_wins: List[Dict[str, Any]]
    prerequisites_required: List[Dict[str, Any]]
    outreach_required: List[Dict[str, Any]]
    blocked_or_unknown: List[Dict[str, Any]]
    
    # Common Blockers
    common_blockers: List[Dict[str, Any]]


class ResearchJobRequest(BaseModel):
    app_id: int


class ResearchJobStatus(BaseModel):
    job_id: str
    app_id: int
    app_name: str
    status: Literal["queued", "discovering", "researching", "verifying", "completed", "failed"]
    current_step: str
    progress_pct: int
    result: Optional[AppRecord] = None
    logs: List[str] = Field(default_factory=list)
    error: Optional[str] = None
