import React, { useState } from 'react';
import {
  Cpu,
  Search,
  BookOpen,
  Key,
  Database,
  ShieldCheck,
  CheckCircle2,
  Users,
  BarChart3,
  Monitor,
  Terminal,
  ArrowDown,
  Layers,
  Sparkles,
  FileCode,
  Zap
} from 'lucide-react';

export const AgentArchitecture: React.FC = () => {
  const [selectedAgent, setSelectedAgent] = useState<number>(0);

  const agents = [
    {
      id: 1,
      title: 'Agent 1: Discovery Agent',
      short: 'Discovery',
      icon: Search,
      color: 'indigo',
      purpose: 'Index & Locate Official Developer Documentation',
      tools: ['Tavily / Google Search API', 'Developer Domain Resolver', 'Robots.txt parser', 'Deep URL Normalizer'],
      inputs: 'Canonical App Name, Category, Starting Website Domain Hint',
      outputs: 'Official documentation index URLs, developer portal sign-up paths, API pricing pages, MCP repository URLs',
      logic: 'Executes targeted queries matching official developer subdomains (docs.*, developer.*, api.*). Discards third-party blogs or SEO aggregators.',
    },
    {
      id: 2,
      title: 'Agent 2: Documentation Research Agent',
      short: 'Doc Research',
      icon: BookOpen,
      color: 'cyan',
      purpose: 'Extract API Protocol Architecture & Surface Breadth',
      tools: ['Playwright Headless Browser', 'BeautifulSoup HTML AST Extractor', 'OpenAPI / Swagger parser', 'DOM Reader'],
      inputs: 'Discovered documentation index and developer guide URLs',
      outputs: 'Protocol classification (REST vs GraphQL vs gRPC vs Local CLI), resource surface area (data, webhooks, administration)',
      logic: 'Analyzes endpoint tables and schema schemas. Distinguishes GraphQL-only apps (Linear, Plain) from REST APIs.',
    },
    {
      id: 3,
      title: 'Agent 3: Authentication Agent',
      short: 'Authentication',
      icon: Key,
      color: 'purple',
      purpose: 'Analyze Credential Types & Token Lifecycle',
      tools: ['Regex Pattern Matcher', 'OAuth2 Scope Parser', 'Header Inspector', 'Token Lifetime Heuristics'],
      inputs: 'Authentication documentation sections and code snippet examples',
      outputs: 'OAuth2 (with PKCE / Refresh), API Key, HTTP Basic (with base64/dummy pass), PAT, Service Account, and token expiry hours',
      logic: 'Extracts exact Authorization headers (`Bearer`, `Basic`, `X-API-Key`). Flags ephemeral token windows (e.g. Zoho 1-hr, TikTok 24-hr).',
    },
    {
      id: 4,
      title: 'Agent 4: Access Classification Agent',
      short: 'Access Gating',
      icon: Database,
      color: 'amber',
      purpose: 'Determine Developer Onboarding & Barrier Tiers',
      tools: ['Pricing Matrix Inspector', 'Registration Flow Analyzer', 'Permission Hierarchy Parser'],
      inputs: 'Account sign-up documentation, pricing plans, and partner portal policies',
      outputs: 'Free self-serve, Trial self-serve, Paid self-serve, Admin approval, Partner approval, Contact sales',
      logic: 'Evaluates whether developer sandboxes are free (Salesforce Developer Edition, HubSpot), require enterprise contracts (LinkedIn Ads, Amazon SP), or workspace admin consent (Lark, Slack).',
    },
    {
      id: 5,
      title: 'Agent 5: Buildability Agent',
      short: 'Buildability',
      icon: CheckCircle2,
      color: 'emerald',
      purpose: 'Assess Composio Agent Toolkit Build Feasibility',
      tools: ['Blocker Taxonomy Matcher', 'Actionable Recommendation Synthesizer', 'Complexity Scorer'],
      inputs: 'Synthesized protocol, auth mechanism, gating barriers, and official MCP presence',
      outputs: 'Build Now vs Build With Prerequisites vs Outreach Required vs Blocked / Unknown; primary blocker; recommended next step',
      logic: 'Applies rigorous business logic. If self-serve & documented: Build Now. If admin consent required: Build With Prerequisites. If partner-locked: Outreach Required.',
    },
    {
      id: 6,
      title: 'Agent 6: Evidence Verification Agent',
      short: 'Verification',
      icon: ShieldCheck,
      color: 'rose',
      purpose: 'Multi-Stage Invariant Checking & Contradiction Detection',
      tools: ['JSON Schema Validator', 'HTTP Status Code Verifier', 'Claim-to-Citation Matcher', 'Contradiction Detector'],
      inputs: 'Extracted fields, citation URLs, and excerpt quotes',
      outputs: 'Stage 1-4 validation passes, flagged discrepancies, and automated review worksheets for human adjudication',
      logic: 'Asserts that any app claiming Official MCP must have documented evidence mentioning MCP. Verifies all documentation URLs return HTTP 200.',
    },
  ];

  return (
    <section id="architecture" className="py-16 border-t border-slate-800/80 bg-[#0a0e1a]/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-2">
            <Cpu className="w-3.5 h-3.5" />
            <span>Autonomous Multi-Agent Pipeline</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Research & Verification Agent Architecture
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
            The multi-agent system decomposes application research into specialized, deterministic stages with strict verification invariants to eliminate hallucination.
          </p>
        </div>

        {/* Visual Pipeline Flow Diagram */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 mb-10 overflow-x-auto">
          <div className="flex items-center justify-between min-w-[850px] relative">
            {/* Connecting horizontal line */}
            <div className="absolute top-1/2 left-8 right-8 -translate-y-1/2 h-0.5 bg-gradient-to-r from-indigo-500 via-cyan-500 to-emerald-500 z-0 opacity-40" />

            {/* Input node */}
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-12 h-12 rounded-2xl bg-slate-900 border border-slate-700 flex items-center justify-center text-white font-bold shadow-lg shadow-black/40">
                <FileCode className="w-5 h-5 text-indigo-400" />
              </div>
              <span className="text-xs font-bold text-white mt-2">100 Apps</span>
              <span className="text-[10px] text-slate-500">Seed Queue</span>
            </div>

            {/* 6 Agents */}
            {agents.map((ag, idx) => {
              const Icon = ag.icon;
              const isSelected = selectedAgent === idx;
              return (
                <div
                  key={ag.id}
                  onClick={() => setSelectedAgent(idx)}
                  className="relative z-10 flex flex-col items-center cursor-pointer group transition-all"
                >
                  <div
                    className={`w-12 h-12 rounded-2xl flex items-center justify-center transition-all ${
                      isSelected
                        ? 'bg-gradient-to-tr from-indigo-600 to-cyan-500 text-white shadow-lg shadow-indigo-500/30 scale-110 ring-2 ring-indigo-400'
                        : 'bg-slate-900 border border-slate-800 text-slate-400 group-hover:text-white group-hover:border-slate-700'
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                  </div>
                  <span className={`text-xs font-bold mt-2 transition-colors ${isSelected ? 'text-cyan-400' : 'text-slate-300'}`}>
                    {ag.short}
                  </span>
                  <span className="text-[10px] text-slate-500 font-mono">Agent {ag.id}</span>
                </div>
              );
            })}

            {/* Output: Analytics & UI */}
            <div className="relative z-10 flex flex-col items-center">
              <div className="w-12 h-12 rounded-2xl bg-emerald-950/40 border border-emerald-500/40 flex items-center justify-center text-emerald-400 font-bold shadow-lg shadow-emerald-500/10">
                <Monitor className="w-5 h-5" />
              </div>
              <span className="text-xs font-bold text-white mt-2">Dashboard</span>
              <span className="text-[10px] text-emerald-400">Verified UI</span>
            </div>
          </div>
        </div>

        {/* Selected Agent Deep Dive Card */}
        <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-indigo-500/30 bg-[#0c101c] relative overflow-hidden">
          <div className="absolute top-0 right-0 w-80 h-80 bg-indigo-500/10 blur-3xl pointer-events-none rounded-full" />

          <div className="flex flex-col lg:flex-row lg:items-start justify-between gap-6 relative z-10">
            <div className="max-w-2xl space-y-4">
              <div className="flex items-center space-x-3">
                <span className="px-3 py-1 rounded-full text-xs font-mono font-bold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                  Agent {agents[selectedAgent].id} of 6
                </span>
                <h3 className="text-xl sm:text-2xl font-black text-white">
                  {agents[selectedAgent].title}
                </h3>
              </div>
              <p className="text-slate-300 text-sm font-medium leading-relaxed">
                {agents[selectedAgent].purpose}
              </p>

              {/* Extraction Logic */}
              <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 space-y-1.5">
                <span className="text-slate-400 font-semibold block uppercase tracking-wider text-[11px]">
                  Execution Logic & Guardrails:
                </span>
                <p className="leading-relaxed">{agents[selectedAgent].logic}</p>
              </div>

              {/* Tooling */}
              <div>
                <span className="text-xs font-semibold text-slate-400 block mb-2 uppercase tracking-wider">
                  Active Tooling & Libraries
                </span>
                <div className="flex flex-wrap gap-2">
                  {agents[selectedAgent].tools.map((t, idx) => (
                    <span
                      key={idx}
                      className="px-2.5 py-1 rounded-lg bg-slate-900 border border-slate-800 text-xs font-mono text-cyan-300"
                    >
                      {t}
                    </span>
                  ))}
                </div>
              </div>
            </div>

            {/* Inputs / Outputs Panel */}
            <div className="w-full lg:w-80 shrink-0 space-y-3 p-5 rounded-xl bg-slate-900/90 border border-slate-800 text-xs">
              <div className="space-y-1">
                <span className="text-slate-500 uppercase tracking-wider font-bold text-[10px] block">
                  Input Contract
                </span>
                <p className="text-slate-300 font-mono text-[11px] leading-relaxed">
                  {agents[selectedAgent].inputs}
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 space-y-1">
                <span className="text-slate-500 uppercase tracking-wider font-bold text-[10px] block">
                  Output Contract
                </span>
                <p className="text-emerald-300 font-mono text-[11px] leading-relaxed">
                  {agents[selectedAgent].outputs}
                </p>
              </div>
              <div className="pt-3 border-t border-slate-800 flex items-center justify-between text-[11px] text-slate-400">
                <span>Hallucination Filter:</span>
                <span className="text-emerald-400 font-semibold">Active</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
