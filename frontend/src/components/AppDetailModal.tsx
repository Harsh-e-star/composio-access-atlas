import React, { useState } from 'react';
import { AppRecord } from '../types';
import {
  X,
  ExternalLink,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Lock,
  Cpu,
  Layers,
  Terminal,
  Clock,
  Sparkles,
  Zap,
  Globe,
  Key,
  Database
} from 'lucide-react';
import { triggerResearch } from '../services/api';

interface AppDetailModalProps {
  app: AppRecord | null;
  onClose: () => void;
  onTriggerResearch?: (appId: number) => void;
}

export const AppDetailModal: React.FC<AppDetailModalProps> = ({ app, onClose, onTriggerResearch }) => {
  const [triggering, setTriggering] = useState(false);

  if (!app) return null;

  const handleRunResearch = async () => {
    setTriggering(true);
    if (onTriggerResearch) {
      onTriggerResearch(app.id);
    } else {
      await triggerResearch(app.id);
    }
    setTriggering(false);
  };

  const getBuildabilityBadge = (verdict: string) => {
    switch (verdict) {
      case 'Build Now':
        return 'bg-emerald-500/20 text-emerald-400 border-emerald-500/40';
      case 'Build With Prerequisites':
        return 'bg-amber-500/20 text-amber-400 border-amber-500/40';
      case 'Outreach Required':
        return 'bg-rose-500/20 text-rose-400 border-rose-500/40';
      default:
        return 'bg-slate-700/40 text-slate-400 border-slate-600';
    }
  };

  const getAccessBadge = (tier: string) => {
    if (tier.includes('Free')) return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
    if (tier.includes('Trial')) return 'bg-teal-500/10 text-teal-300 border-teal-500/30';
    if (tier.includes('Paid')) return 'bg-cyan-500/10 text-cyan-300 border-cyan-500/30';
    if (tier.includes('Admin')) return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
    return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6 lg:p-8 bg-black/80 backdrop-blur-md animate-fade-in">
      <div
        className="glass-panel w-full max-w-4xl max-h-[90vh] rounded-2xl border border-slate-700/80 shadow-2xl flex flex-col overflow-hidden bg-[#0c101c]"
        onClick={e => e.stopPropagation()}
      >
        {/* Modal Header */}
        <div className="p-6 border-b border-slate-800 flex items-start justify-between bg-slate-900/60">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-indigo-600 to-cyan-500 p-0.5 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
              <div className="w-full h-full bg-slate-900 rounded-[14px] flex items-center justify-center font-black text-white text-lg">
                {app.id}
              </div>
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <h2 className="text-xl sm:text-2xl font-black text-white">{app.app_name}</h2>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-semibold border ${getBuildabilityBadge(app.buildability)}`}>
                  {app.buildability}
                </span>
                <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium border ${getAccessBadge(app.access_tier)}`}>
                  {app.access_tier}
                </span>
              </div>
              <div className="flex items-center space-x-3 mt-1 text-xs text-slate-400">
                <span className="text-indigo-400 font-medium">{app.category}</span>
                <span>•</span>
                <a
                  href={app.website}
                  target="_blank"
                  rel="noreferrer"
                  className="hover:text-cyan-400 inline-flex items-center space-x-1"
                >
                  <span>{app.website.replace('https://', '').replace('www.', '').split('/')[0]}</span>
                  <ExternalLink className="w-3 h-3" />
                </a>
              </div>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-2 rounded-xl text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body (Scrollable) */}
        <div className="p-6 overflow-y-auto space-y-6 text-sm text-slate-300">
          {/* Description */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Application Scope & Profile
            </span>
            <p className="text-slate-200 text-sm">{app.description}</p>
          </div>

          {/* Technical Specifications Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* Box 1: Auth Specifications */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 text-indigo-400 font-bold text-xs uppercase tracking-wider">
                <Key className="w-4 h-4" />
                <span>Authentication Protocol</span>
              </div>
              <div>
                <span className="text-xs text-slate-400">Primary Method:</span>
                <span className="text-white font-semibold ml-2 text-sm">{app.primary_auth}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400">All Supported:</span>
                <div className="flex flex-wrap gap-1.5 mt-1">
                  {app.auth_methods.map((m, idx) => (
                    <span key={idx} className="px-2 py-0.5 rounded-md bg-indigo-950/60 text-indigo-300 border border-indigo-500/30 text-xs font-mono">
                      {m}
                    </span>
                  ))}
                </div>
              </div>
              <p className="text-xs text-slate-400 pt-2 border-t border-slate-800/80 leading-relaxed">
                {app.auth_details}
              </p>
            </div>

            {/* Box 2: API Protocol & Surface */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 text-cyan-400 font-bold text-xs uppercase tracking-wider">
                <Database className="w-4 h-4" />
                <span>API Architecture & Surface</span>
              </div>
              <div>
                <span className="text-xs text-slate-400">API Protocol:</span>
                <span className="text-white font-semibold ml-2 font-mono text-xs">{app.api_type}</span>
              </div>
              <div>
                <span className="text-xs text-slate-400 block mb-1">Resource Breadth:</span>
                <p className="text-xs text-slate-300 font-mono bg-slate-950/80 p-2.5 rounded-lg border border-slate-800/80">
                  {app.api_surface}
                </p>
              </div>
            </div>

            {/* Box 3: MCP Server Availability */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 text-purple-400 font-bold text-xs uppercase tracking-wider">
                <Cpu className="w-4 h-4" />
                <span>Model Context Protocol (MCP)</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-400">Official MCP:</span>
                  <span className={`font-bold ml-1.5 ${app.official_mcp === 'Yes' ? 'text-emerald-400' : 'text-slate-500'}`}>
                    {app.official_mcp}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Community MCP:</span>
                  <span className={`font-bold ml-1.5 ${app.community_mcp === 'Yes' ? 'text-cyan-400' : 'text-slate-500'}`}>
                    {app.community_mcp}
                  </span>
                </div>
              </div>
              {app.mcp_details && (
                <p className="text-xs text-slate-300 pt-1 text-[11px] leading-relaxed">
                  <strong className="text-slate-400">Server detail:</strong> {app.mcp_details}
                </p>
              )}
            </div>

            {/* Box 4: Gating Flags & Constraints */}
            <div className="p-4 rounded-xl bg-slate-900/50 border border-slate-800 space-y-2">
              <div className="flex items-center space-x-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
                <Lock className="w-4 h-4" />
                <span>Gating & Account Rules</span>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs">
                <div>
                  <span className="text-slate-400">Free/Trial:</span>
                  <span className={`font-semibold ml-1.5 ${app.free_trial_available ? 'text-emerald-400' : 'text-slate-500'}`}>
                    {app.free_trial_available ? 'Available' : 'No'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Paid Plan:</span>
                  <span className={`font-semibold ml-1.5 ${app.paid_plan_required ? 'text-amber-400' : 'text-slate-500'}`}>
                    {app.paid_plan_required ? 'Required' : 'No'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Admin Approval:</span>
                  <span className={`font-semibold ml-1.5 ${app.admin_approval_required ? 'text-amber-400' : 'text-slate-500'}`}>
                    {app.admin_approval_required ? 'Required' : 'No'}
                  </span>
                </div>
                <div>
                  <span className="text-slate-400">Partnership:</span>
                  <span className={`font-semibold ml-1.5 ${app.partnership_required ? 'text-rose-400' : 'text-slate-500'}`}>
                    {app.partnership_required ? 'Required' : 'No'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Blockers & Next Step */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-rose-950/20 border border-rose-500/30">
              <span className="text-xs font-bold text-rose-400 uppercase tracking-wider block mb-1">
                Main Integration Blocker / Friction Point
              </span>
              <p className="text-xs text-rose-200/90 leading-relaxed font-medium">{app.main_blocker}</p>
            </div>
            <div className="p-4 rounded-xl bg-indigo-950/20 border border-indigo-500/30">
              <span className="text-xs font-bold text-indigo-400 uppercase tracking-wider block mb-1">
                Recommended Composio Next Step
              </span>
              <p className="text-xs text-indigo-200/90 leading-relaxed font-medium">{app.recommended_next_step}</p>
            </div>
          </div>

          {/* Documentation URLs */}
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <Globe className="w-3.5 h-3.5 text-cyan-400" />
              <span>Official Developer Documentation URLs ({app.documentation_urls.length})</span>
            </h4>
            <div className="space-y-1.5">
              {app.documentation_urls.map((url, idx) => (
                <a
                  key={idx}
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900 border border-slate-800 hover:border-indigo-500/40 text-xs text-indigo-300 transition-colors group"
                >
                  <span className="truncate max-w-[650px] font-mono">{url}</span>
                  <ExternalLink className="w-3.5 h-3.5 text-slate-500 group-hover:text-indigo-400 shrink-0 ml-2" />
                </a>
              ))}
            </div>
          </div>

          {/* Evidence Excerpts */}
          <div>
            <h4 className="text-xs font-bold text-slate-400 uppercase tracking-wider mb-2 flex items-center space-x-1.5">
              <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
              <span>Verified Evidence & Exact Documentation Excerpts ({app.evidence_excerpts.length})</span>
            </h4>
            <div className="space-y-2">
              {app.evidence_excerpts.map((ev, idx) => (
                <div key={idx} className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 text-xs space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="px-2 py-0.5 rounded bg-indigo-950 text-indigo-300 font-mono text-[10px]">
                      {ev.source_type}
                    </span>
                    <a
                      href={ev.url}
                      target="_blank"
                      rel="noreferrer"
                      className="text-slate-400 hover:text-cyan-400 flex items-center space-x-1 text-[11px]"
                    >
                      <span className="truncate max-w-[300px]">{ev.url}</span>
                      <ExternalLink className="w-3 h-3 ml-0.5" />
                    </a>
                  </div>
                  <p className="text-slate-200 font-medium italic pt-1 text-[12px] leading-relaxed">
                    "{ev.claim}"
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Metadata Footer */}
          <div className="pt-4 border-t border-slate-800 flex flex-wrap items-center justify-between text-xs text-slate-500 gap-2">
            <div className="flex items-center space-x-4">
              <span>Status: <strong className="text-emerald-400">{app.verification_status}</strong></span>
              <span>Confidence: <strong className="text-white">{app.confidence_score}</strong></span>
              <span>Researched: <strong className="text-slate-400">{app.research_timestamp.split('T')[0]}</strong></span>
            </div>
          </div>
        </div>

        {/* Modal Footer */}
        <div className="p-4 border-t border-slate-800 bg-slate-900/80 flex items-center justify-between">
          <span className="text-xs text-slate-400 font-mono">App #{app.id} • {app.app_name}</span>
          <div className="flex items-center space-x-3">
            <button
              onClick={onClose}
              className="px-4 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:bg-slate-800 transition-colors"
            >
              Close
            </button>
            <button
              onClick={handleRunResearch}
              disabled={triggering}
              className="inline-flex items-center space-x-1.5 px-4 py-2 rounded-xl text-xs font-semibold bg-indigo-600 hover:bg-indigo-500 text-white transition-all shadow-md shadow-indigo-600/30"
            >
              <Zap className="w-3.5 h-3.5" />
              <span>{triggering ? 'Queuing Agent...' : 'Trigger Re-Research in Agent'}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
