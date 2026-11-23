import React, { useState, useEffect, useRef } from 'react';
import { AppRecord, ResearchJobStatus } from '../types';
import { triggerResearch, pollJobStatus } from '../services/api';
import {
  Terminal,
  Play,
  RotateCcw,
  CheckCircle2,
  AlertCircle,
  ExternalLink,
  ShieldCheck,
  Cpu,
  Layers,
  Sparkles,
  Zap,
  Globe,
  Key,
  Database
} from 'lucide-react';

interface LiveAgentDemoProps {
  apps: AppRecord[];
  initialSelectedApp?: AppRecord | null;
}

export const LiveAgentDemo: React.FC<LiveAgentDemoProps> = ({ apps, initialSelectedApp }) => {
  const [selectedAppId, setSelectedAppId] = useState<number>(initialSelectedApp?.id ?? 6); // Default: Firecrawl (App 6)
  const [activeJob, setActiveJob] = useState<ResearchJobStatus | null>(null);
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const logsEndRef = useRef<HTMLDivElement>(null);
  const pollTimerRef = useRef<any>(null);

  // Update selected app when passed from parent matrix
  useEffect(() => {
    if (initialSelectedApp) {
      setSelectedAppId(initialSelectedApp.id);
    }
  }, [initialSelectedApp]);

  // Auto-scroll logs
  useEffect(() => {
    logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [activeJob?.logs]);

  // Clean up poll timer on unmount
  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  const selectedApp = apps.find(a => a.id === selectedAppId) || apps[0];

  const handleStartResearch = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setErrorMsg(null);

    // Initial placeholder status
    const initialStatus: ResearchJobStatus = {
      job_id: 'init',
      app_id: selectedAppId,
      app_name: selectedApp.app_name,
      status: 'queued',
      current_step: 'Dispatching task to Discovery Agent...',
      progress_pct: 10,
      logs: [
        `[${new Date().toLocaleTimeString()}] Task queued for #${selectedApp.id} ${selectedApp.app_name}.`,
        `[${new Date().toLocaleTimeString()}] Target website: ${selectedApp.website}`,
      ],
    };
    setActiveJob(initialStatus);

    try {
      const res = await triggerResearch(selectedAppId);
      const jobId = res.job_id;

      let currentPct = 15;
      pollTimerRef.current = setInterval(async () => {
        try {
          const status = await pollJobStatus(jobId, selectedAppId);
          setActiveJob(status);

          if (status.status === 'completed' || status.status === 'failed') {
            clearInterval(pollTimerRef.current);
            setIsRunning(false);
            if (status.status === 'failed') {
              setErrorMsg(status.error || 'Agent encountered an error during research.');
            }
          }
        } catch (err: any) {
          clearInterval(pollTimerRef.current);
          setIsRunning(false);
          setErrorMsg(err.message || 'Polling error.');
        }
      }, 700);
    } catch (err: any) {
      setIsRunning(false);
      setErrorMsg(err.message || 'Failed to dispatch agent task.');
    }
  };

  return (
    <section id="demo" className="py-16 border-t border-slate-800/80 bg-[#080b13]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-10">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-2">
            <Terminal className="w-3.5 h-3.5" />
            <span>Interactive Live Execution Trigger</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Live Research Agent Runner
          </h2>
          <p className="mt-2 text-slate-400 text-sm sm:text-base leading-relaxed">
            Select any of the 100 applications to trigger the multi-agent pipeline in real-time. Watch the agents discover documentation, extract endpoints, evaluate auth mechanisms, and verify citations live.
          </p>
        </div>

        {/* Quick Pick App Pills */}
        <div className="flex items-center gap-2 overflow-x-auto pb-2 mb-4 text-xs font-semibold scrollbar-none">
          <span className="text-slate-500 text-[11px] uppercase tracking-wider shrink-0 mr-1">Quick Picks:</span>
          {[
            { id: 6, label: '#6 Firecrawl (Official MCP)' },
            { id: 1, label: '#1 Salesforce (OAuth2)' },
            { id: 21, label: '#21 Slack (Admin Appr)' },
            { id: 41, label: '#41 Shopify (API Key)' },
            { id: 73, label: '#73 Linear (GraphQL)' },
            { id: 91, label: '#91 NotebookLM (Gated)' },
            { id: 98, label: '#98 Mermaid CLI (Local Tool)' },
            { id: 100, label: '#100 Grain (AI Video)' },
          ].map(p => (
            <button
              key={p.id}
              onClick={() => { setSelectedAppId(p.id); }}
              disabled={isRunning}
              className={`px-3 py-1.5 rounded-lg border whitespace-nowrap transition-all ${
                selectedAppId === p.id
                  ? 'bg-cyan-600 text-white border-cyan-400 shadow-sm shadow-cyan-600/30'
                  : 'bg-slate-900 text-slate-300 hover:text-white border-slate-800'
              }`}
            >
              {p.label}
            </button>
          ))}
        </div>

        {/* Execution Trigger Bar */}
        <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-slate-800 mb-8 flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex flex-col sm:flex-row items-center space-y-2 sm:space-y-0 sm:space-x-4 w-full sm:w-auto">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider whitespace-nowrap">
              Select Target App:
            </span>
            <select
              value={selectedAppId}
              onChange={e => setSelectedAppId(Number(e.target.value))}
              disabled={isRunning}
              className="w-full sm:w-80 px-3.5 py-2.5 rounded-xl bg-slate-900 border border-slate-700 text-xs font-semibold text-white outline-none focus:border-cyan-500 transition-colors"
            >
              {apps.map(app => (
                <option key={app.id} value={app.id}>
                  #{app.id} {app.app_name} ({app.category})
                </option>
              ))}
            </select>
          </div>

          <div className="flex items-center space-x-3 w-full sm:w-auto justify-end">
            <button
              onClick={handleStartResearch}
              disabled={isRunning}
              className={`flex items-center justify-center space-x-2 px-6 py-2.5 rounded-xl font-bold text-xs transition-all shadow-lg ${
                isRunning
                  ? 'bg-slate-800 text-slate-500 cursor-not-allowed'
                  : 'bg-gradient-to-r from-cyan-500 to-indigo-600 hover:from-cyan-400 hover:to-indigo-500 text-white shadow-cyan-500/20 active:scale-[0.98]'
              }`}
            >
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>{isRunning ? 'Researching Live...' : `Run Research on ${selectedApp.app_name}`}</span>
            </button>
          </div>
        </div>

        {/* Error Banner */}
        {errorMsg && (
          <div className="mb-6 p-4 rounded-xl bg-rose-950/40 border border-rose-500/40 text-rose-300 text-xs flex items-center space-x-2">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
            <span>{errorMsg}</span>
          </div>
        )}

        {/* Live Runner Split Console */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          {/* Left Console: Progress & Terminal Logs (7 cols) */}
          <div className="lg:col-span-7 glass-panel rounded-2xl border border-slate-800 flex flex-col overflow-hidden h-[520px]">
            {/* Console Header */}
            <div className="p-4 bg-slate-900/90 border-b border-slate-800 flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <span className="w-3 h-3 rounded-full bg-rose-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-amber-500/80 inline-block" />
                <span className="w-3 h-3 rounded-full bg-emerald-500/80 inline-block" />
                <span className="text-xs font-mono text-slate-400 ml-2">agent_coordinator.py</span>
              </div>
              <div className="flex items-center space-x-2">
                {isRunning && (
                  <span className="flex items-center space-x-1.5 text-[11px] text-cyan-400 font-mono">
                    <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping" />
                    <span>EXECUTING</span>
                  </span>
                )}
                {activeJob?.status === 'completed' && (
                  <span className="text-[11px] text-emerald-400 font-mono font-semibold">
                    ✓ COMPLETED
                  </span>
                )}
              </div>
            </div>

            {/* Progress Bar */}
            <div className="px-4 py-3 bg-slate-950/60 border-b border-slate-800/80 space-y-1.5">
              <div className="flex items-center justify-between text-xs">
                <span className="text-slate-300 font-medium truncate max-w-[320px]">
                  {activeJob?.current_step || 'Ready to trigger autonomous research pipeline.'}
                </span>
                <span className="font-mono font-bold text-cyan-400">
                  {activeJob?.progress_pct ?? 0}%
                </span>
              </div>
              <div className="w-full h-1.5 rounded-full bg-slate-900 overflow-hidden">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-indigo-500 via-cyan-400 to-emerald-400 transition-all duration-300"
                  style={{ width: `${activeJob?.progress_pct ?? 0}%` }}
                />
              </div>
            </div>

            {/* Terminal Log Stream */}
            <div className="p-4 overflow-y-auto flex-1 font-mono text-xs space-y-2 bg-[#06080e] text-slate-300">
              {!activeJob ? (
                <div className="h-full flex flex-col items-center justify-center text-slate-600 text-center">
                  <Terminal className="w-10 h-10 mb-2 opacity-40" />
                  <p>Agent runner idle.</p>
                  <p className="text-[11px] text-slate-700">Click "Run Research" above to initiate autonomous multi-agent analysis.</p>
                </div>
              ) : (
                <>
                  {activeJob.logs.map((log, idx) => {
                    const isError = log.includes('ERROR');
                    const isStage = log.includes('Agent ');
                    const isSuccess = log.includes('complete') || log.includes('0 contradictions');
                    return (
                      <div
                        key={idx}
                        className={`leading-relaxed text-[11px] ${
                          isError
                            ? 'text-rose-400'
                            : isSuccess
                            ? 'text-emerald-400 font-semibold'
                            : isStage
                            ? 'text-cyan-300'
                            : 'text-slate-300'
                        }`}
                      >
                        {log}
                      </div>
                    );
                  })}
                  <div ref={logsEndRef} />
                </>
              )}
            </div>
          </div>

          {/* Right Console: Extracted Results & Verified Citations (5 cols) */}
          <div className="lg:col-span-5 glass-panel rounded-2xl border border-slate-800 p-5 flex flex-col justify-between overflow-y-auto h-[520px]">
            <div>
              <div className="flex items-center justify-between pb-3 border-b border-slate-800 mb-4">
                <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                  <ShieldCheck className="w-4 h-4 text-emerald-400" />
                  <span>Extracted Findings & Citations</span>
                </h3>
                <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-indigo-500/10 text-indigo-300 border border-indigo-500/30">
                  App #{selectedApp.id}
                </span>
              </div>

              {/* Result Summary */}
              <div className="space-y-3 text-xs">
                <div>
                  <span className="text-slate-400 text-[11px] block">Application</span>
                  <div className="text-white font-bold text-base flex items-center space-x-2">
                    <span>{selectedApp.app_name}</span>
                    <span className="text-xs text-indigo-400 font-normal">({selectedApp.category})</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 pt-2">
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Primary Auth</span>
                    <span className="font-semibold text-indigo-300 font-mono text-xs">{selectedApp.primary_auth}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Access Tier</span>
                    <span className="font-semibold text-emerald-400 text-xs">{selectedApp.access_tier}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">API Protocol</span>
                    <span className="font-semibold text-cyan-300 font-mono text-xs">{selectedApp.api_type}</span>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-900 border border-slate-800">
                    <span className="text-[10px] text-slate-500 block">Buildability</span>
                    <span className="font-semibold text-emerald-400 text-xs">{selectedApp.buildability}</span>
                  </div>
                </div>

                {/* Blocker & Recommendation */}
                <div className="p-3 rounded-lg bg-slate-900/90 border border-slate-800 space-y-1">
                  <span className="text-[10px] text-amber-400 font-bold block uppercase tracking-wider">
                    Primary Blocker / Caveat
                  </span>
                  <p className="text-slate-300 text-[11px] leading-relaxed">
                    {selectedApp.main_blocker}
                  </p>
                </div>

                {/* Evidence Excerpts */}
                <div className="pt-2">
                  <span className="text-[10px] text-slate-500 font-bold block uppercase tracking-wider mb-1.5">
                    Verified Excerpt ({selectedApp.evidence_excerpts.length} citations)
                  </span>
                  {selectedApp.evidence_excerpts.slice(0, 2).map((ev, idx) => (
                    <div key={idx} className="p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 text-[11px] mb-1.5">
                      <p className="text-slate-200 italic">"{ev.claim}"</p>
                      <a
                        href={ev.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-indigo-400 hover:text-cyan-300 flex items-center space-x-1 mt-1 text-[10px]"
                      >
                        <span className="truncate max-w-[260px]">{ev.url}</span>
                        <ExternalLink className="w-2.5 h-2.5" />
                      </a>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            <div className="pt-3 border-t border-slate-800 text-[11px] text-slate-500 flex items-center justify-between">
              <span>Verification Status:</span>
              <span className="font-semibold text-emerald-400">{selectedApp.verification_status}</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
