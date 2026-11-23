import React, { useState } from 'react';
import { AnalyticsSummary } from '../types';
import {
  CheckCircle2,
  AlertCircle,
  Lock,
  HelpCircle,
  ArrowRight,
  Sparkles,
  ExternalLink,
  Zap,
  ShieldCheck,
  Building
} from 'lucide-react';

interface RecommendationsProps {
  analytics: AnalyticsSummary | null;
}

export const Recommendations: React.FC<RecommendationsProps> = ({ analytics }) => {
  const [activeTab, setActiveTab] = useState<'quick_wins' | 'prerequisites' | 'outreach'>('quick_wins');

  if (!analytics) return null;

  return (
    <section id="recommendations" className="py-16 border-t border-slate-800/80 bg-[#080b13]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-10">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-2">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Product Operations Strategic Roadmap</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Prioritized Integration Roadmap
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
            Actionable categorization for Composio engineering and product ops. Balances immediate developer velocity against high-friction enterprise gating.
          </p>
        </div>

        {/* Tab Selection Navigation */}
        <div className="flex flex-wrap gap-3 mb-8">
          <button
            onClick={() => setActiveTab('quick_wins')}
            className={`flex items-center space-x-2 px-5 py-3 rounded-xl font-bold text-xs transition-all ${
              activeTab === 'quick_wins'
                ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-lg shadow-emerald-500/10'
                : 'bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            <span>1. Quick Wins ({analytics.quick_wins.length} Apps)</span>
          </button>

          <button
            onClick={() => setActiveTab('prerequisites')}
            className={`flex items-center space-x-2 px-5 py-3 rounded-xl font-bold text-xs transition-all ${
              activeTab === 'prerequisites'
                ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 shadow-lg shadow-amber-500/10'
                : 'bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <AlertCircle className="w-4 h-4 text-amber-400" />
            <span>2. Build With Prerequisites ({analytics.prerequisites_required.length} Apps)</span>
          </button>

          <button
            onClick={() => setActiveTab('outreach')}
            className={`flex items-center space-x-2 px-5 py-3 rounded-xl font-bold text-xs transition-all ${
              activeTab === 'outreach'
                ? 'bg-rose-500/20 text-rose-400 border border-rose-500/40 shadow-lg shadow-rose-500/10'
                : 'bg-slate-900/80 text-slate-400 hover:text-white border border-slate-800'
            }`}
          >
            <Lock className="w-4 h-4 text-rose-400" />
            <span>3. Partnership Required ({analytics.outreach_required.length} Apps)</span>
          </button>
        </div>

        {/* Tab 1: Quick Wins */}
        {activeTab === 'quick_wins' && (
          <div className="space-y-6 animate-fade-in">
            <div className="glass-panel rounded-2xl p-6 border border-emerald-500/30 bg-emerald-950/10">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center space-x-2">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>Quadrant 1: Immediate Self-Serve Velocity (77 Applications)</span>
              </h3>
              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed max-w-4xl">
                These applications provide unencumbered developer access through self-serve registration, free tiers, or standard developer sandboxes. Composio can author, test, and release toolkits immediately.
              </p>
              <div className="mt-4 pt-4 border-t border-emerald-500/20 text-xs text-emerald-300 flex items-center space-x-2">
                <strong>Recommended Action:</strong>
                <span>Run automated OpenAPI / schema generation sprints across Developer Tools, Scraping, and Productivity categories.</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analytics.quick_wins.slice(0, 18).map(app => (
                <div key={app.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">#{app.id} {app.app_name}</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-semibold">
                      Build Now
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-[11px] text-slate-400">
                    <span className="text-indigo-400 font-mono">{app.primary_auth}</span>
                    <span>•</span>
                    <span className="text-slate-300 font-mono">{app.api_type}</span>
                  </div>
                  <p className="text-slate-400 text-[11px] italic pt-1 border-t border-slate-800">
                    {app.recommendation}
                  </p>
                </div>
              ))}
            </div>
            {analytics.quick_wins.length > 18 && (
              <p className="text-center text-xs text-slate-500 pt-2">
                Showing top 18 of {analytics.quick_wins.length} Quick Win applications. View full list in the 100-App Matrix above.
              </p>
            )}
          </div>
        )}

        {/* Tab 2: Build With Prerequisites */}
        {activeTab === 'prerequisites' && (
          <div className="space-y-6 animate-fade-in">
            <div className="glass-panel rounded-2xl p-6 border border-amber-500/30 bg-amber-950/10">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center space-x-2">
                <AlertCircle className="w-5 h-5 text-amber-400" />
                <span>Quadrant 2: Tenant & Admin Gated Integrations (17 Applications)</span>
              </h3>
              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed max-w-4xl">
                These platforms possess public, robust REST/GraphQL APIs, but individual end-users cannot install agent bots without tenant admin delegation, organization-level OAuth consent, or paid workspace seats (e.g. Jira, Zendesk, Lark, Freshdesk, Gusto).
              </p>
              <div className="mt-4 pt-4 border-t border-amber-500/20 text-xs text-amber-300 flex items-center space-x-2">
                <strong>Recommended Action:</strong>
                <span>Design in-app OAuth consent guide and workspace admin invitation flows within the Composio dashboard to eliminate user onboarding friction.</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analytics.prerequisites_required.map(app => (
                <div key={app.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">#{app.id} {app.app_name}</span>
                    <span className="px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-semibold">
                      Prerequisites
                    </span>
                  </div>
                  <div className="text-[11px] text-amber-300/90 font-medium">
                    Blocker: {app.main_blocker}
                  </div>
                  <p className="text-slate-400 text-[11px] italic pt-1 border-t border-slate-800">
                    {app.recommended_next_step}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Tab 3: Partnership Required */}
        {activeTab === 'outreach' && (
          <div className="space-y-6 animate-fade-in">
            <div className="glass-panel rounded-2xl p-6 border border-rose-500/30 bg-rose-950/10">
              <h3 className="text-lg font-bold text-white mb-2 flex items-center space-x-2">
                <Lock className="w-5 h-5 text-rose-400" />
                <span>Quadrant 3: Partner & Enterprise Gated Integrations (6 Applications)</span>
              </h3>
              <p className="text-slate-300 text-xs sm:text-sm leading-relaxed max-w-4xl">
                These 6 applications enforce strict institutional gating: partner program certification, data protection policy (DPP) audits, or direct Account Executive sales agreements.
              </p>
              <div className="mt-4 pt-4 border-t border-rose-500/20 text-xs text-rose-300 flex items-center space-x-2">
                <strong>Recommended Action:</strong>
                <span>Route these 6 accounts directly to Composio Business Development & Strategic Partnerships for official ISV agreements.</span>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {analytics.outreach_required.map(app => (
                <div key={app.id} className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="font-bold text-white text-sm">#{app.id} {app.app_name}</span>
                    <span className="px-2 py-0.5 rounded bg-rose-500/10 text-rose-400 border border-rose-500/30 text-[10px] font-semibold">
                      Outreach
                    </span>
                  </div>
                  <div className="text-[11px] text-rose-300 font-medium">
                    Gating: {app.access_tier}
                  </div>
                  <div className="text-[11px] text-slate-300">
                    Blocker: {app.main_blocker}
                  </div>
                  <p className="text-slate-400 text-[11px] italic pt-1 border-t border-slate-800">
                    {app.recommended_next_step}
                  </p>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
};
