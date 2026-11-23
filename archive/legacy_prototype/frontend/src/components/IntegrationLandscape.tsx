import React from 'react';
import { AnalyticsSummary } from '../types';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  Tooltip,
  Legend
} from 'recharts';
import { Layers, PieChart as PieIcon, BarChart2, ShieldCheck, Lock, Cpu } from 'lucide-react';

interface IntegrationLandscapeProps {
  analytics: AnalyticsSummary | null;
}

const COLORS = {
  emerald: '#10b981',
  indigo: '#6366f1',
  cyan: '#06b6d4',
  amber: '#f59e0b',
  rose: '#f43f5e',
  purple: '#a855f7',
  slate: '#64748b',
};

const CustomTooltip = ({ active, payload, label }: any) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900/95 border border-slate-700 p-3 rounded-xl shadow-xl backdrop-blur-md text-xs">
        <p className="font-bold text-white mb-1">{label || payload[0].name}</p>
        {payload.map((entry: any, index: number) => (
          <div key={`item-${index}`} className="flex items-center space-x-2 text-slate-300">
            <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: entry.color || entry.fill }} />
            <span className="text-slate-400 capitalize">{entry.name}:</span>
            <span className="font-semibold text-white">{entry.value}</span>
            {entry.payload?.percentage !== undefined && (
              <span className="text-slate-400">({entry.payload.percentage}%)</span>
            )}
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export const IntegrationLandscape: React.FC<IntegrationLandscapeProps> = ({ analytics }) => {
  if (!analytics) return null;

  // 1. Auth Distribution Data
  const authData = Object.entries(analytics.auth_distribution).map(([name, value]) => ({
    name,
    count: value,
    percentage: Math.round((value / analytics.total_apps) * 100),
  }));

  // 2. Buildability Donut Data
  const buildabilityData = [
    { name: 'Build Now', value: analytics.build_now_count, color: COLORS.emerald },
    { name: 'Build With Prerequisites', value: analytics.build_with_prerequisites_count, color: COLORS.amber },
    { name: 'Outreach Required', value: analytics.outreach_required_count, color: COLORS.rose },
  ];

  // 3. Self-Serve vs Gated Data
  const accessData = [
    { name: 'Free Self-Serve', value: analytics.access_distribution['Free self-serve'] || 0, color: '#10b981' },
    { name: 'Trial Self-Serve', value: analytics.access_distribution['Trial self-serve'] || 0, color: '#34d399' },
    { name: 'Paid Self-Serve', value: analytics.access_distribution['Paid self-serve'] || 0, color: '#06b6d4' },
    { name: 'Admin Approval', value: analytics.access_distribution['Admin approval'] || 0, color: '#f59e0b' },
    { name: 'Partner Approval', value: analytics.access_distribution['Partner approval'] || 0, color: '#f43f5e' },
    { name: 'Contact Sales', value: analytics.access_distribution['Contact sales'] || 0, color: '#e11d48' },
  ];

  // 4. Category Readiness
  const categoryData = analytics.category_metrics.map(c => ({
    name: c.category.replace('&', '+').replace('Infrastructure', 'Infra').replace('Productivity + Projects', 'Projects'),
    fullName: c.category,
    readiness: c.readiness_score,
    buildNow: c.build_now,
    prerequisites: c.build_with_prerequisites,
    outreach: c.outreach_required,
  }));

  // 5. MCP Distribution
  const mcpData = [
    { name: 'Community MCP Available', count: analytics.mcp_availability_counts.community_mcp, color: COLORS.cyan },
    { name: 'Official 1st-Party MCP', count: analytics.mcp_availability_counts.official_mcp, color: COLORS.emerald },
    { name: 'No MCP Server', count: analytics.mcp_availability_counts.no_mcp, color: COLORS.slate },
  ];

  // 6. Blockers
  const blockerData = analytics.common_blockers.slice(0, 6).map(b => ({
    name: b.blocker_theme,
    count: b.affected_apps_count,
    percentage: b.percentage,
  }));

  return (
    <section id="landscape" className="py-16 border-t border-slate-800/80 bg-[#080b13]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-2">
            <BarChart2 className="w-3.5 h-3.5" />
            <span>Quantitative Analytics Engine</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            The 100-App Integration Landscape
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
            Macro analysis of authentication mechanisms, gating hurdles, protocol diversity, and open-source MCP adoption across the entire canonical dataset.
          </p>
        </div>

        {/* Charts Grid: Row 1 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Chart 1: Buildability Donut */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <PieIcon className="w-4 h-4 text-emerald-400" />
                  <span>Buildability Verdict Distribution</span>
                </h3>
                <p className="text-xs text-slate-400 mt-1">Classification of immediate agent toolkit feasibility</p>
              </div>
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                77% Build Now
              </span>
            </div>

            <div className="h-64 sm:h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie
                    data={buildabilityData}
                    cx="50%"
                    cy="50%"
                    innerRadius={65}
                    outerRadius={95}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {buildabilityData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip content={<CustomTooltip />} />
                </PieChart>
              </ResponsiveContainer>
            </div>

            <div className="grid grid-cols-3 gap-2 pt-4 border-t border-slate-800/80 text-center">
              <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-[11px] text-slate-400 block">Build Now</span>
                <span className="text-base font-extrabold text-emerald-400">{analytics.build_now_count} apps</span>
              </div>
              <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-[11px] text-slate-400 block">Prerequisites</span>
                <span className="text-base font-extrabold text-amber-400">{analytics.build_with_prerequisites_count} apps</span>
              </div>
              <div className="p-2 rounded-xl bg-slate-900/60 border border-slate-800">
                <span className="text-[11px] text-slate-400 block">Outreach</span>
                <span className="text-base font-extrabold text-rose-400">{analytics.outreach_required_count} apps</span>
              </div>
            </div>
          </div>

          {/* Chart 2: Authentication Distribution */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div className="flex items-center justify-between mb-4">
              <div>
                <h3 className="text-base font-bold text-white flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-indigo-400" />
                  <span>Primary Authentication Protocols</span>
                </h3>
                <p className="text-xs text-slate-400 mt-1">Dominant credential mechanisms required for API integration</p>
              </div>
              <span className="px-2.5 py-1 rounded-full text-xs font-bold bg-indigo-500/10 text-indigo-400 border border-indigo-500/20">
                61% OAuth2
              </span>
            </div>

            <div className="h-64 sm:h-72 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={authData} layout="vertical" margin={{ top: 5, right: 30, left: 40, bottom: 5 }}>
                  <XAxis type="number" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <YAxis type="category" dataKey="name" stroke="#64748b" tick={{ fill: '#e2e8f0', fontSize: 11 }} width={90} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" fill="#6366f1" radius={[0, 6, 6, 0]}>
                    {authData.map((_, index) => (
                      <Cell key={`bar-${index}`} fill={index === 0 ? '#6366f1' : index === 1 ? '#06b6d4' : '#a855f7'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="flex items-center justify-between pt-4 border-t border-slate-800/80 text-xs text-slate-400">
              <span>OAuth2 Support: <strong className="text-indigo-400">{analytics.oauth_adoption_pct}%</strong></span>
              <span>API Key / Token: <strong className="text-cyan-400">{analytics.api_key_adoption_pct}%</strong></span>
              <span>Basic / Custom: <strong className="text-purple-400">6%</strong></span>
            </div>
          </div>
        </div>

        {/* Charts Grid: Row 2 */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Chart 3: Access Gating Tiers */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Lock className="w-4 h-4 text-cyan-400" />
                  <span>Developer Access Tiers</span>
                </h3>
                <span className="text-xs font-semibold text-emerald-400">77% Self-Serve</span>
              </div>
              <p className="text-xs text-slate-400 mb-4">Gating friction encountered when acquiring API keys or app credentials</p>
            </div>

            <div className="space-y-3 my-2">
              {accessData.map((item, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-300">{item.name}</span>
                    <span className="font-semibold text-white">{item.value} apps ({item.value}%)</span>
                  </div>
                  <div className="w-full h-2 rounded-full bg-slate-900 overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all duration-500"
                      style={{ width: `${item.value}%`, backgroundColor: item.color }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-800/80 text-xs text-slate-400">
              <strong className="text-emerald-400">77%</strong> can be provisioned through automated self-serve portals.
            </div>
          </div>

          {/* Chart 4: MCP Ecosystem Adoption */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Cpu className="w-4 h-4 text-cyan-400" />
                  <span>MCP Ecosystem Landscape</span>
                </h3>
                <span className="text-xs font-semibold text-cyan-400">90% Coverage Potential</span>
              </div>
              <p className="text-xs text-slate-400 mb-4">Official first-party servers vs active open-source community packages</p>
            </div>

            <div className="h-56 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={mcpData} margin={{ top: 10, right: 10, left: -20, bottom: 25 }}>
                  <XAxis dataKey="name" angle={-15} textAnchor="end" stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 10 }} />
                  <YAxis stroke="#64748b" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                  <Tooltip content={<CustomTooltip />} />
                  <Bar dataKey="count" fill="#06b6d4" radius={[6, 6, 0, 0]}>
                    {mcpData.map((entry, index) => (
                      <Cell key={`mcp-${index}`} fill={entry.color} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>

            <div className="pt-4 border-t border-slate-800/80 text-xs text-slate-400">
              Only 14 official vendors, but <strong className="text-cyan-400">76 community implementations</strong> exist ready to be hardened.
            </div>
          </div>

          {/* Chart 5: Top Common Integration Blockers */}
          <div className="glass-panel rounded-2xl p-6 border border-slate-800 flex flex-col justify-between">
            <div>
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <Layers className="w-4 h-4 text-amber-400" />
                  <span>Integration Friction Taxonomy</span>
                </h3>
                <span className="text-xs font-semibold text-amber-400">Top Blocker Themes</span>
              </div>
              <p className="text-xs text-slate-400 mb-4">Systemic hurdles identified during deep documentation extraction</p>
            </div>

            <div className="space-y-3 my-1">
              {blockerData.map((item, idx) => (
                <div key={idx} className="space-y-1">
                  <div className="flex items-center justify-between text-xs">
                    <span className="text-slate-300 truncate max-w-[200px]" title={item.name}>{item.name}</span>
                    <span className="font-semibold text-amber-400">{item.count} apps</span>
                  </div>
                  <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-amber-500 to-rose-500"
                      style={{ width: `${(item.count / 30) * 100}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <div className="pt-4 border-t border-slate-800/80 text-xs text-slate-400">
              Top blocker: <strong className="text-white">Workspace Admin / Tenant Authorization</strong> (22 apps).
            </div>
          </div>
        </div>

        {/* Chart 6: Category Readiness Heatmap / Ranking */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-6 gap-2">
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <BarChart2 className="w-4 h-4 text-emerald-400" />
                <span>Category Integration Readiness Scoreboard</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">Readiness score calculated as: (Build Now × 1.0 + Prerequisites × 0.6) / Total Apps</p>
            </div>
            <span className="text-xs text-slate-400 font-mono">10 apps per category</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-3">
            {analytics.category_metrics.map((cat, idx) => {
              const isTop = cat.readiness_score >= 90;
              const isMid = cat.readiness_score >= 75 && cat.readiness_score < 90;
              return (
                <div
                  key={idx}
                  className={`p-4 rounded-xl border transition-all ${
                    isTop
                      ? 'bg-emerald-950/20 border-emerald-500/30'
                      : isMid
                      ? 'bg-indigo-950/20 border-indigo-500/20'
                      : 'bg-slate-900/40 border-slate-800'
                  }`}
                >
                  <div className="flex items-center justify-between text-xs mb-2">
                    <span className="font-semibold text-white truncate max-w-[140px]" title={cat.category}>
                      {cat.category}
                    </span>
                    <span
                      className={`font-mono font-bold text-xs ${
                        isTop ? 'text-emerald-400' : isMid ? 'text-indigo-400' : 'text-amber-400'
                      }`}
                    >
                      {cat.readiness_score}
                    </span>
                  </div>

                  {/* Readiness Progress Bar */}
                  <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden mb-3">
                    <div
                      className={`h-full rounded-full ${
                        isTop ? 'bg-emerald-400' : isMid ? 'bg-indigo-400' : 'bg-amber-400'
                      }`}
                      style={{ width: `${cat.readiness_score}%` }}
                    />
                  </div>

                  {/* Category breakdown stats */}
                  <div className="text-[11px] text-slate-400 space-y-1">
                    <div className="flex justify-between">
                      <span>Build Now:</span>
                      <span className="font-semibold text-emerald-400">{cat.build_now}/10</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Prerequisites:</span>
                      <span className="text-amber-400">{cat.build_with_prerequisites}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>Outreach:</span>
                      <span className={cat.outreach_required > 0 ? 'text-rose-400 font-semibold' : 'text-slate-500'}>
                        {cat.outreach_required}
                      </span>
                    </div>
                    <div className="flex justify-between pt-1 border-t border-slate-800 text-[10px]">
                      <span>Dominant:</span>
                      <span className="text-slate-300 font-mono">{cat.dominant_auth}</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
};
