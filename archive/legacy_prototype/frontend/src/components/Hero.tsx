import React, { useState } from 'react';
import { AnalyticsSummary, AccuracyMetrics } from '../types';
import {
  Sparkles,
  Layers,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  ArrowUpRight,
  Zap,
  Lock,
  Unlock,
  Clock,
  ChevronDown,
  ChevronUp,
  Cpu,
  Target
} from 'lucide-react';

interface HeroProps {
  analytics: AnalyticsSummary | null;
  metrics: AccuracyMetrics | null;
}

export const Hero: React.FC<HeroProps> = ({ analytics, metrics }) => {
  const [showBrief, setShowBrief] = useState(true);

  return (
    <section id="overview" className="relative pt-12 pb-16 overflow-hidden">
      {/* Background ambient glows */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[700px] h-[350px] bg-gradient-to-tr from-indigo-600/15 via-cyan-500/10 to-transparent blur-3xl pointer-events-none rounded-full" />
      <div className="absolute -top-12 -left-12 w-96 h-96 bg-indigo-500/10 blur-3xl pointer-events-none rounded-full" />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
        {/* Badge & Quick Briefing Toggle */}
        <div className="flex flex-wrap items-center justify-between gap-3 mb-6">
          <div className="inline-flex items-center space-x-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-indigo-500/30 text-xs text-indigo-300 font-medium shadow-sm shadow-indigo-500/10 backdrop-blur-md">
            <Sparkles className="w-3.5 h-3.5 text-cyan-400" />
            <span>Composio AI Product Ops Submission</span>
            <span className="w-1 h-1 rounded-full bg-indigo-400" />
            <span className="text-slate-400">100/100 Apps Researched & Verified</span>
          </div>

          <button
            onClick={() => setShowBrief(!showBrief)}
            className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-full bg-indigo-600/15 hover:bg-indigo-600/25 border border-indigo-500/40 text-xs font-semibold text-indigo-300 transition-all cursor-pointer"
          >
            <Clock className="w-3.5 h-3.5 text-cyan-400" />
            <span>2-Minute Executive Briefing</span>
            {showBrief ? <ChevronUp className="w-3.5 h-3.5" /> : <ChevronDown className="w-3.5 h-3.5" />}
          </button>
        </div>

        {/* 2-Minute Executive Briefing Card (Collapsible) */}
        {showBrief && (
          <div className="mb-10 p-5 sm:p-6 rounded-2xl bg-gradient-to-br from-indigo-950/40 via-slate-900/90 to-cyan-950/30 border border-indigo-500/30 shadow-2xl backdrop-blur-xl animate-fade-in relative overflow-hidden">
            <div className="flex items-center justify-between pb-3 border-b border-indigo-500/20 mb-4">
              <div className="flex items-center space-x-2">
                <Target className="w-4 h-4 text-cyan-400" />
                <h3 className="text-sm font-extrabold uppercase tracking-wider text-white">
                  Executive Briefing for Reviewers (Read in 60-120 Seconds)
                </h3>
              </div>
              <span className="text-[11px] font-mono text-cyan-300 bg-cyan-950/60 px-2 py-0.5 rounded border border-cyan-500/30">
                TL;DR Synthesis
              </span>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 text-xs">
              {/* Point 1: What was built */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center space-x-1.5 font-bold text-white">
                  <Cpu className="w-3.5 h-3.5 text-indigo-400" />
                  <span>1. The Multi-Agent Pipeline</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  Autonomous 6-agent system coordinating Discovery, Doc Parsing, Auth Analysis, Access Gating, Buildability Scoring, and Invariant Verification across all 100 applications.
                </p>
              </div>

              {/* Point 2: Core Empirical Findings */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center space-x-1.5 font-bold text-white">
                  <Layers className="w-3.5 h-3.5 text-emerald-400" />
                  <span>2. Findings & Gating</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  <strong className="text-emerald-400">77% Build Now:</strong> Free/trial self-serve greenfield. <strong className="text-amber-400">17% Prerequisites:</strong> Workspace admin approvals. <strong className="text-rose-400">6% Outreach:</strong> Hard-gated enterprise partner programs.
                </p>
              </div>

              {/* Point 3: Verification & Accuracy */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center space-x-1.5 font-bold text-white">
                  <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                  <span>3. Audited Accuracy</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  Measured on a 20-app stratified holdout (60 fields). First-pass heuristic baseline: <strong className="text-amber-400">43.3%</strong>. Doc-grounded multi-agent verified: <strong className="text-emerald-400">98.3%</strong>. 100% evidence citation coverage.
                </p>
              </div>

              {/* Point 4: Composio Next Steps */}
              <div className="p-3.5 rounded-xl bg-slate-900/80 border border-slate-800 space-y-1.5">
                <div className="flex items-center space-x-1.5 font-bold text-white">
                  <CheckCircle2 className="w-3.5 h-3.5 text-indigo-300" />
                  <span>4. Composio Roadmap</span>
                </div>
                <p className="text-slate-300 leading-relaxed">
                  1. Batch-generate Developer Tools (10) & Scraping (9) toolkits. 2. Build in-app IT Admin OAuth consent flows for 17 apps. 3. Harden the 76 community MCP servers.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Headline */}
        <div className="max-w-4xl">
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-black tracking-tight text-white leading-[1.12]">
            100 Apps. One Research Agent.{' '}
            <span className="bg-gradient-to-r from-indigo-400 via-cyan-300 to-indigo-200 bg-clip-text text-transparent">
              An Integration Opportunity Map.
            </span>
          </h1>
          <p className="mt-5 text-base sm:text-lg text-slate-300 max-w-3xl leading-relaxed">
            Empirical investigation of developer authentication protocols, API surfaces, self-serve gating, 
            and MCP server ecosystems across 10 mission-critical enterprise categories. Grounded with official documentation citations and an audited multi-stage verification pipeline.
          </p>
        </div>

        {/* Quick action buttons */}
        <div className="mt-8 flex flex-wrap items-center gap-3">
          <a
            href="#matrix"
            className="inline-flex items-center space-x-2 px-5 py-3 rounded-xl bg-gradient-to-r from-indigo-600 to-indigo-500 hover:from-indigo-500 hover:to-indigo-400 text-white font-semibold text-sm shadow-lg shadow-indigo-600/25 transition-all hover:scale-[1.02] active:scale-[0.98]"
          >
            <span>Explore 100-App Matrix</span>
            <ArrowUpRight className="w-4 h-4" />
          </a>
          <a
            href="#demo"
            className="inline-flex items-center space-x-2 px-5 py-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-medium text-sm transition-all hover:scale-[1.02]"
          >
            <Zap className="w-4 h-4 text-cyan-400" />
            <span>Launch Live Agent Demo</span>
          </a>
          <a
            href="#verification"
            className="inline-flex items-center space-x-2 px-5 py-3 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700/80 font-medium text-sm transition-all hover:scale-[1.02]"
          >
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Audit Report ({metrics?.second_pass_accuracy ?? 98.3}% Acc)</span>
          </a>
        </div>

        {/* Primary Metric Highlights Grid */}
        <div className="mt-12 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 sm:gap-4">
          {/* Card 1: Total Apps */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-slate-800 relative overflow-hidden group hover:border-indigo-500/40 transition-all">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Coverage</span>
              <Layers className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-white">
              {analytics?.total_apps ?? 100}
            </div>
            <div className="mt-1 text-xs text-slate-400">
              100% across 10 categories
            </div>
          </div>

          {/* Card 2: Build Now */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-emerald-500/20 bg-emerald-950/10 relative overflow-hidden group hover:border-emerald-500/40 transition-all">
            <div className="flex items-center justify-between text-emerald-400 text-xs font-semibold">
              <span>Build Now</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-white">
              {analytics?.build_now_count ?? 77}
              <span className="text-sm font-semibold text-emerald-400 ml-1.5">
                ({analytics?.build_now_pct ?? 77}%)
              </span>
            </div>
            <div className="mt-1 text-xs text-slate-400">
              Immediate self-serve greenfield
            </div>
          </div>

          {/* Card 3: Build With Prerequisites */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-amber-500/20 bg-amber-950/10 relative overflow-hidden group hover:border-amber-500/40 transition-all">
            <div className="flex items-center justify-between text-amber-400 text-xs font-semibold">
              <span>Prerequisites</span>
              <AlertCircle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-white">
              {analytics?.build_with_prerequisites_count ?? 17}
              <span className="text-sm font-semibold text-amber-400 ml-1.5">
                ({analytics?.build_with_prerequisites_pct ?? 17}%)
              </span>
            </div>
            <div className="mt-1 text-xs text-slate-400">
              Admin / Tenant approval needed
            </div>
          </div>

          {/* Card 4: Outreach Required */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-rose-500/20 bg-rose-950/10 relative overflow-hidden group hover:border-rose-500/40 transition-all">
            <div className="flex items-center justify-between text-rose-400 text-xs font-semibold">
              <span>Outreach</span>
              <Lock className="w-4 h-4 text-rose-400" />
            </div>
            <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-white">
              {analytics?.outreach_required_count ?? 6}
              <span className="text-sm font-semibold text-rose-400 ml-1.5">
                ({analytics?.outreach_required_pct ?? 6}%)
              </span>
            </div>
            <div className="mt-1 text-xs text-slate-400">
              Enterprise / Partner gated
            </div>
          </div>

          {/* Card 5: Evidence Coverage */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-cyan-500/20 bg-cyan-950/10 relative overflow-hidden group hover:border-cyan-500/40 transition-all">
            <div className="flex items-center justify-between text-cyan-400 text-xs font-semibold">
              <span>Evidence</span>
              <Unlock className="w-4 h-4 text-cyan-400" />
            </div>
            <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-white">
              {analytics?.evidence_coverage_pct ?? 100}%
            </div>
            <div className="mt-1 text-xs text-slate-400">
              Official docs & verified quotes
            </div>
          </div>

          {/* Card 6: Verified Accuracy */}
          <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-indigo-500/30 bg-indigo-950/20 relative overflow-hidden group hover:border-indigo-400 transition-all shadow-md shadow-indigo-500/10">
            <div className="flex items-center justify-between text-indigo-300 text-xs font-semibold">
              <span>Audited Accuracy</span>
              <ShieldCheck className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="mt-2 text-2xl sm:text-3xl font-extrabold text-white">
              {metrics?.second_pass_accuracy ?? 98.3}%
            </div>
            <div className="mt-1 text-xs text-indigo-300/80">
              Holdout evaluated vs ground truth
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};
