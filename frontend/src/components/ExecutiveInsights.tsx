import React from 'react';
import { AnalyticsSummary } from '../types';
import { Zap, ShieldAlert, Cpu, Network, CheckCircle, ArrowRight, Building, Key, Unlock } from 'lucide-react';

interface ExecutiveInsightsProps {
  analytics: AnalyticsSummary | null;
}

export const ExecutiveInsights: React.FC<ExecutiveInsightsProps> = ({ analytics }) => {
  return (
    <section id="insights" className="py-16 border-t border-slate-800/80 bg-[#0a0e1a]/60">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-2">
            <Zap className="w-3.5 h-3.5" />
            <span>Strategic Synthesis for Composio Product Ops</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Executive Insights & Integration Feasibility
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
            Data-backed synthesis derived from investigating all 100 enterprise targets. Highlights immediate ROI opportunities, systemic platform bottlenecks, and recommended prioritization vectors.
          </p>
        </div>

        {/* 4 Core Pillars */}
        <div className="mt-10 grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Pillar 1: The 77% Build Now Greenfield */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 hover:border-indigo-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 font-bold">
                  01
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">The 77% Self-Serve Greenfield</h3>
                  <span className="text-xs text-emerald-400 font-semibold">Immediate Execution Velocity</span>
                </div>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">
                <strong className="text-white">77 out of 100 applications</strong> can be integrated into Composio immediately without requiring partnership contracts, manual sales calls, or vendor approvals.
              </p>
              <div className="mt-4 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 space-y-2">
                <div className="flex items-center justify-between text-slate-400">
                  <span>Categories with 100% Build Now readiness:</span>
                  <span className="font-semibold text-emerald-400">Developer Tools (10/10), AI Research (9/10), Scraping (9/10)</span>
                </div>
                <div className="text-slate-400">
                  <strong className="text-slate-200">Recommendation:</strong> Launch a automated connector sprint for Developer & Infra (Supabase, Cloudflare, Netlify, Render, Vercel) and Web Scraping (Firecrawl, Apify, Tavily, SerpApi).
                </div>
              </div>
            </div>
            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span>Ready Connectors: <strong className="text-white">77 Apps</strong></span>
              <span className="text-emerald-400 flex items-center">High ROI <ArrowRight className="w-3 h-3 ml-1" /></span>
            </div>
          </div>

          {/* Pillar 2: The MCP Reality vs Ecosystem Demand */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 hover:border-indigo-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400 font-bold">
                  02
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">The MCP Reality Gap</h3>
                  <span className="text-xs text-cyan-400 font-semibold">14 Official vs 76 Community Servers</span>
                </div>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">
                Only <strong className="text-white">14 apps</strong> host official first-party Model Context Protocol servers (e.g. Apify, Firecrawl, GitHub, Sentry, Reducto, Consensus, Neo4j). However, <strong className="text-white">76 apps</strong> possess active community MCP implementations in open source.
              </p>
              <div className="mt-4 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 space-y-2">
                <div className="text-slate-400">
                  <strong className="text-slate-200">The Composio Advantage:</strong> Community servers frequently lack managed multi-tenant auth, automatic OAuth token refresh, and robust rate limit handling.
                </div>
                <div className="text-slate-400">
                  By providing managed, compliant execution wrapping these 76 open-source specs, Composio can immediately become the default runtime for AI agents.
                </div>
              </div>
            </div>
            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span>Community Demand: <strong className="text-white">76/100 Apps</strong></span>
              <span className="text-cyan-400 flex items-center">Standardization Opportunity <ArrowRight className="w-3 h-3 ml-1" /></span>
            </div>
          </div>

          {/* Pillar 3: OAuth2 vs API Key Complexity */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 hover:border-indigo-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 font-bold">
                  03
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">Auth Infrastructure Dichotomy</h3>
                  <span className="text-xs text-indigo-400 font-semibold">61% OAuth2 vs 39% Keys / Tokens</span>
                </div>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">
                <strong className="text-white">61% of target applications</strong> rely on OAuth2 (with PKCE, refresh tokens, and scope negotiation), while <strong className="text-white">39%</strong> use static API keys, Personal Access Tokens, or HTTP Basic credentials.
              </p>
              <div className="mt-4 p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 text-xs text-slate-300 space-y-2">
                <div className="text-slate-400">
                  <strong className="text-slate-200">Technical Friction:</strong> Systems like Zoho, TikTok Marketing, and Lark have aggressive token expiry windows (1-2 hours) requiring real-time proactive token lease renewal background workers.
                </div>
                <div className="text-slate-400">
                  Conversely, Data & Scraping services (90% API keys) can be shipped in hours with minimal credential management overhead.
                </div>
              </div>
            </div>
            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span>OAuth Adoption: <strong className="text-white">61.0%</strong></span>
              <span className="text-indigo-400 flex items-center">Managed Auth Moat <ArrowRight className="w-3 h-3 ml-1" /></span>
            </div>
          </div>

          {/* Pillar 4: The 6% Gated Frontier */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 hover:border-indigo-500/30 transition-all flex flex-col justify-between">
            <div>
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 font-bold">
                  04
                </div>
                <div>
                  <h3 className="text-lg font-bold text-white">The Gated Frontier (6%)</h3>
                  <span className="text-xs text-rose-400 font-semibold">Enterprise & Partner Blockers</span>
                </div>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed">
                Only <strong className="text-white">6 applications</strong> are strictly blocked from self-serve development, requiring business development or verified partner contracts:
              </p>
              <div className="mt-3 grid grid-cols-2 gap-2 text-xs">
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-200 font-semibold">Amazon SP:</span>
                  <span className="text-slate-400 block text-[11px]">Developer registration & DPP audit</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-200 font-semibold">LinkedIn Ads:</span>
                  <span className="text-slate-400 block text-[11px]">Manual enterprise tier approval</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-200 font-semibold">Salesforce B2C:</span>
                  <span className="text-slate-400 block text-[11px]">Account Executive contract only</span>
                </div>
                <div className="p-2 rounded-lg bg-slate-900 border border-slate-800">
                  <span className="text-slate-200 font-semibold">PitchBook / Paygent:</span>
                  <span className="text-slate-400 block text-[11px]">Enterprise merchant verification</span>
                </div>
              </div>
            </div>
            <div className="mt-5 pt-4 border-t border-slate-800/80 flex items-center justify-between text-xs text-slate-400">
              <span>Outreach Targets: <strong className="text-rose-400">6 Apps</strong></span>
              <span className="text-rose-400 flex items-center">BizDev Pipeline <ArrowRight className="w-3 h-3 ml-1" /></span>
            </div>
          </div>
        </div>

        {/* Priority Roadmap Callout Banner */}
        <div className="mt-8 p-6 rounded-2xl bg-gradient-to-r from-indigo-900/30 via-slate-900 to-indigo-950/40 border border-indigo-500/30 flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="space-y-1">
            <h4 className="text-base font-bold text-white flex items-center space-x-2">
              <CheckCircle className="w-5 h-5 text-emerald-400" />
              <span>Recommended Composio Rollout Strategy</span>
            </h4>
            <p className="text-xs sm:text-sm text-slate-300 max-w-2xl">
              <strong className="text-indigo-300">Phase 1:</strong> Batch-ship the 77 self-serve connectors starting with Developer Tools & Scraping. <strong className="text-indigo-300">Phase 2:</strong> Build tenant-level admin invitation workflows for the 17 prerequisite apps. <strong className="text-indigo-300">Phase 3:</strong> Establish strategic partner agreements for LinkedIn Ads & Amazon SP.
            </p>
          </div>
          <a
            href="#recommendations"
            className="whitespace-nowrap px-4 py-2.5 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white font-semibold text-xs transition-all shadow-md shadow-indigo-600/30"
          >
            View Detailed Roadmap
          </a>
        </div>
      </div>
    </section>
  );
};
