export interface EvidenceItem {
  url: string;
  claim: string;
  source_type: 'official_docs' | 'api_reference' | 'github_repo' | 'developer_portal' | 'help_center';
}

export type AccessTier =
  | 'Free self-serve'
  | 'Trial self-serve'
  | 'Paid self-serve'
  | 'Admin approval'
  | 'Partner approval'
  | 'Contact sales'
  | 'Unknown';

export type BuildabilityVerdict =
  | 'Build Now'
  | 'Build With Prerequisites'
  | 'Outreach Required'
  | 'Blocked / Unknown';

export type MCPStatus = 'Yes' | 'No' | 'Unknown';

export interface AppRecord {
  id: number;
  app_name: string;
  category: string;
  website: string;
  description: string;
  
  // Auth
  auth_methods: string[];
  primary_auth: string;
  auth_details: string;
  multiple_auth_supported: boolean;
  
  // API Protocol
  api_type: string;
  api_surface: string;
  
  // MCP
  official_mcp: MCPStatus;
  community_mcp: MCPStatus;
  mcp_details?: string | null;
  
  // Access & Gating
  access_tier: AccessTier;
  free_trial_available: boolean;
  paid_plan_required: boolean;
  admin_approval_required: boolean;
  partnership_required: boolean;
  
  // Buildability
  buildability: BuildabilityVerdict;
  main_blocker: string;
  recommended_next_step: string;
  
  // Evidence
  confidence_score: 'High' | 'Medium' | 'Low';
  documentation_urls: string[];
  evidence_excerpts: EvidenceItem[];
  research_timestamp: string;
  verification_status: 'Human Verified' | 'Agent Verified' | 'Pending Review';
  
  // Comparison & Audit
  first_pass_auth?: string | null;
  first_pass_access?: string | null;
  first_pass_surface?: string | null;
  disagreement_flag?: boolean;
  audit_notes?: string | null;
}

export interface VerificationAuditEntry {
  app_id: number;
  app_name: string;
  category: string;
  first_pass_prediction: {
    auth: string;
    access: string;
    surface: string;
  };
  second_pass_verification: {
    auth: string;
    access: string;
    surface: string;
  };
  human_ground_truth: {
    auth: string;
    access: string;
    surface: string;
  };
  agreed_fields: string[];
  discrepancies: string[];
  error_type?: string | null;
  correction_applied?: string | null;
  evidence_urls: string[];
  notes: string;
}

export interface AccuracyMetrics {
  sample_size: number;
  fields_per_app: number;
  total_fields_evaluated: number;
  first_pass_correct: number;
  first_pass_accuracy: number;
  second_pass_correct: number;
  second_pass_accuracy: number;
  human_verified_count: number;
  error_taxonomy: Record<string, number>;
  methodology_statement: string;
}

export interface CategoryMetric {
  category: string;
  total: number;
  total_apps: number;
  build_now: number;
  build_with_prerequisites: number;
  outreach_required: number;
  self_serve: number;
  official_mcp: number;
  community_mcp: number;
  dominant_auth: string;
  readiness_score: number;
}

export interface CommonBlocker {
  blocker_theme: string;
  affected_apps_count: number;
  percentage: number;
}

export interface AnalyticsSummary {
  total_apps: number;
  categories_count: number;
  reviewed_count: number;
  evidence_coverage_pct: number;
  
  oauth_supported_count: number;
  oauth_adoption_pct: number;
  api_key_supported_count: number;
  api_key_adoption_pct: number;
  basic_auth_count: number;
  pat_auth_count: number;
  cli_or_custom_count: number;
  auth_distribution: Record<string, number>;
  
  self_serve_count: number;
  self_serve_pct: number;
  gated_count: number;
  gated_pct: number;
  access_distribution: Record<string, number>;
  
  build_now_count: number;
  build_now_pct: number;
  build_with_prerequisites_count: number;
  build_with_prerequisites_pct: number;
  outreach_required_count: number;
  outreach_required_pct: number;
  buildability_distribution: Record<string, number>;
  
  api_type_distribution: Record<string, number>;
  mcp_availability_counts: {
    official_mcp: number;
    community_mcp: number;
    total_mcp_ecosystem: number;
    no_mcp: number;
  };
  
  category_metrics: CategoryMetric[];
  quick_wins: Array<{
    id: number;
    app_name: string;
    category: string;
    primary_auth: string;
    api_type: string;
    official_mcp: string;
    recommendation: string;
  }>;
  prerequisites_required: Array<{
    id: number;
    app_name: string;
    category: string;
    main_blocker: string;
    recommended_next_step: string;
  }>;
  outreach_required: Array<{
    id: number;
    app_name: string;
    category: string;
    access_tier: string;
    main_blocker: string;
    recommended_next_step: string;
  }>;
  blocked_or_unknown: any[];
  common_blockers: CommonBlocker[];
}

export interface VerificationData {
  metrics: AccuracyMetrics;
  stages: Record<string, {
    name: string;
    status: string;
    passed_count?: number;
    total_count?: number;
    contradictions_detected?: number;
    sample_size?: number;
    human_verified_count?: number;
    description?: string;
  }>;
  audit_ledger: VerificationAuditEntry[];
}

export interface ResearchJobStatus {
  job_id: string;
  app_id: number;
  app_name: string;
  status: 'queued' | 'discovering' | 'researching' | 'verifying' | 'completed' | 'failed';
  current_step: string;
  progress_pct: number;
  result?: AppRecord | null;
  logs: string[];
  error?: string | null;
}
