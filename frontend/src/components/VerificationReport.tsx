import React, { useState } from 'react';
import { VerificationData, VerificationAuditEntry } from '../types';
import {
  ShieldCheck,
  CheckCircle2,
  XCircle,
  AlertTriangle,
  ExternalLink,
  Filter,
  Layers,
  Sparkles,
  ArrowRight,
  HelpCircle,
  FileCheck
} from 'lucide-react';

interface VerificationReportProps {
  data: VerificationData | null;
}

export const VerificationReport: React.FC<VerificationReportProps> = ({ data }) => {
  const [selectedErrorFilter, setSelectedErrorFilter] = useState<string>('All');

  if (!data) return null;

  const { metrics, stages, audit_ledger } = data;

  const errorTaxonomyList = Object.entries(metrics.error_taxonomy || {});

  const filteredEntries = audit_ledger.filter(entry => {
    if (selectedErrorFilter === 'All') return true;
    if (selectedErrorFilter === 'Correct') return entry.discrepancies.length === 0;
    if (selectedErrorFilter === 'Corrected') return entry.discrepancies.length > 0;
    return entry.error_type === selectedErrorFilter;
  });

  return (
    <section id="verification" className="py-16 border-t border-slate-800/80 bg-[#0a0e1a]/70">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-12">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-emerald-400 mb-2">
            <ShieldCheck className="w-3.5 h-3.5" />
            <span>Audited Ground-Truth Evaluation</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Independent Verification & Accuracy Report
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
            Multi-stage validation results measured against a 20-application stratified holdout across all 10 categories. 
            Empirically documents genuine model errors, second-pass agent corrections, and first-party evidence adjudication.
          </p>
        </div>

        {/* Accuracy Comparison Banner */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-10">
          {/* Card 1: Sample Size */}
          <div className="glass-panel rounded-2xl p-5 border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 block mb-1">Stratified Holdout</span>
            <div className="text-3xl font-black text-white">
              {metrics.sample_size} <span className="text-sm font-normal text-slate-400">apps</span>
            </div>
            <p className="text-[11px] text-slate-400 mt-1">2 apps per category • 60 total fields</p>
          </div>

          {/* Card 2: First-Pass Baseline */}
          <div className="glass-panel rounded-2xl p-5 border border-amber-500/30 bg-amber-950/10">
            <div className="flex items-center justify-between text-amber-400 text-xs font-semibold mb-1">
              <span>First-Pass Baseline</span>
              <AlertTriangle className="w-4 h-4 text-amber-400" />
            </div>
            <div className="text-3xl font-black text-white">
              {metrics.first_pass_accuracy}%
            </div>
            <p className="text-[11px] text-amber-300/80 mt-1">
              {metrics.first_pass_correct}/60 fields (naive heuristic predictions)
            </p>
          </div>

          {/* Card 3: Second-Pass Multi-Agent Verified */}
          <div className="glass-panel rounded-2xl p-5 border border-emerald-500/40 bg-emerald-950/20 shadow-lg shadow-emerald-500/10">
            <div className="flex items-center justify-between text-emerald-400 text-xs font-bold mb-1">
              <span>Multi-Agent Verified</span>
              <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            </div>
            <div className="text-3xl font-black text-emerald-400">
              {metrics.second_pass_accuracy}%
            </div>
            <p className="text-[11px] text-emerald-300 mt-1">
              {metrics.second_pass_correct}/60 fields (doc-grounded agent verification)
            </p>
          </div>

          {/* Card 4: Human Verified */}
          <div className="glass-panel rounded-2xl p-5 border border-indigo-500/30 bg-indigo-950/10">
            <div className="flex items-center justify-between text-indigo-300 text-xs font-semibold mb-1">
              <span>Adjudicated Sample</span>
              <FileCheck className="w-4 h-4 text-indigo-400" />
            </div>
            <div className="text-3xl font-black text-white">
              {metrics.human_verified_count} <span className="text-sm font-normal text-slate-400">apps</span>
            </div>
            <p className="text-[11px] text-indigo-300/80 mt-1">100% evaluated against official docs</p>
          </div>
        </div>

        {/* 6 Verification Stages Status Grid */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 mb-10">
          <h3 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
            <Layers className="w-4 h-4 text-cyan-400" />
            <span>The 6-Stage Automated Verification Architecture</span>
          </h3>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
            {Object.entries(stages).map(([key, stg], idx) => (
              <div key={key} className="p-3.5 rounded-xl bg-slate-900/70 border border-slate-800 text-xs space-y-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-slate-200">Stage {idx + 1}: {stg.name.split('&')[0]}</span>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold uppercase bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
                    {stg.status}
                  </span>
                </div>
                <p className="text-[11px] text-slate-400 pt-1">
                  {stg.passed_count !== undefined && `${stg.passed_count}/${stg.total_count} passing invariants`}
                  {stg.contradictions_detected !== undefined && `Detected: ${stg.contradictions_detected} contradictions`}
                  {stg.sample_size !== undefined && `Sample size: ${stg.sample_size} apps checked`}
                  {stg.human_verified_count !== undefined && `Human confirmed: ${stg.human_verified_count} apps`}
                </p>
              </div>
            ))}
          </div>
        </div>

        {/* Error Taxonomy Analysis */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800 mb-10">
          <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 gap-2">
            <div>
              <h3 className="text-base font-bold text-white flex items-center space-x-2">
                <AlertTriangle className="w-4 h-4 text-amber-400" />
                <span>Error Taxonomy & Correction Analysis</span>
              </h3>
              <p className="text-xs text-slate-400 mt-1">Categorization of failure modes discovered during first-pass heuristics</p>
            </div>
            <span className="text-xs text-slate-500 font-mono">19 total discrepancies resolved</span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {errorTaxonomyList.map(([errorName, count], idx) => (
              <div
                key={idx}
                onClick={() => setSelectedErrorFilter(errorName)}
                className={`p-3.5 rounded-xl border cursor-pointer transition-all ${
                  selectedErrorFilter === errorName
                    ? 'bg-indigo-950/50 border-indigo-500 shadow-md shadow-indigo-500/10'
                    : 'bg-slate-900/60 border-slate-800 hover:border-slate-700'
                }`}
              >
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-semibold text-slate-200">{errorName}</span>
                  <span className="font-bold text-amber-400 bg-amber-500/10 px-2 py-0.5 rounded text-[11px]">
                    {count}
                  </span>
                </div>
                <span className="text-[10px] text-slate-500">Click to filter holdout cases</span>
              </div>
            ))}
          </div>
        </div>

        {/* Holdout Audit Ledger Table */}
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
          <div className="p-4 bg-slate-900/90 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
            <div>
              <h4 className="text-sm font-bold text-white">Stratified Holdout Adjudication Ledger</h4>
              <p className="text-xs text-slate-400">Comparing First-Pass vs Multi-Agent Verified vs Human Ground Truth</p>
            </div>

            {/* Error Filter Pills */}
            <div className="flex items-center space-x-2 text-xs">
              <span className="text-slate-500">Filter:</span>
              <button
                onClick={() => setSelectedErrorFilter('All')}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  selectedErrorFilter === 'All' ? 'bg-indigo-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                All (20)
              </button>
              <button
                onClick={() => setSelectedErrorFilter('Corrected')}
                className={`px-2.5 py-1 rounded-lg text-xs font-semibold transition-colors ${
                  selectedErrorFilter === 'Corrected' ? 'bg-amber-600 text-white' : 'bg-slate-800 text-slate-400 hover:text-white'
                }`}
              >
                Corrected Only
              </button>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-950/80 border-b border-slate-800 text-slate-400 uppercase text-[10px] font-mono tracking-wider">
                  <th className="py-3 px-4 w-12">#</th>
                  <th className="py-3 px-4">Application</th>
                  <th className="py-3 px-4">First-Pass Prediction</th>
                  <th className="py-3 px-4">Verified Ground Truth</th>
                  <th className="py-3 px-4">Error Type & Correction</th>
                  <th className="py-3 px-4 text-right">Evidence Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredEntries.map(entry => {
                  const hasDiscrepancy = entry.discrepancies.length > 0;
                  return (
                    <tr key={entry.app_id} className="hover:bg-slate-800/30 transition-colors">
                      <td className="py-3 px-4 font-mono text-slate-500 text-xs">
                        #{entry.app_id}
                      </td>
                      <td className="py-3 px-4">
                        <div className="font-bold text-white">{entry.app_name}</div>
                        <span className="text-[10px] text-slate-500">{entry.category}</span>
                      </td>
                      <td className="py-3 px-4">
                        <div className="space-y-0.5 text-[11px] font-mono text-slate-400">
                          <div>Auth: <span className="text-slate-300">{entry.first_pass_prediction.auth}</span></div>
                          <div>Access: <span className="text-slate-300">{entry.first_pass_prediction.access}</span></div>
                          <div>Surface: <span className="text-slate-300">{entry.first_pass_prediction.surface}</span></div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        <div className="space-y-0.5 text-[11px] font-mono">
                          <div>Auth: <span className="text-emerald-300 font-semibold">{entry.human_ground_truth.auth}</span></div>
                          <div>Access: <span className="text-emerald-300 font-semibold">{entry.human_ground_truth.access}</span></div>
                          <div>Surface: <span className="text-emerald-300 font-semibold">{entry.human_ground_truth.surface}</span></div>
                        </div>
                      </td>
                      <td className="py-3 px-4">
                        {hasDiscrepancy ? (
                          <div className="space-y-1">
                            <span className="inline-block px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/30 text-[10px] font-semibold">
                              {entry.error_type}
                            </span>
                            <p className="text-[11px] text-slate-300 italic">{entry.correction_applied}</p>
                          </div>
                        ) : (
                          <span className="inline-flex items-center space-x-1 text-emerald-400 text-xs font-semibold">
                            <CheckCircle2 className="w-3.5 h-3.5" />
                            <span>100% Concordant</span>
                          </span>
                        )}
                      </td>
                      <td className="py-3 px-4 text-right">
                        {entry.evidence_urls.length > 0 && (
                          <a
                            href={entry.evidence_urls[0]}
                            target="_blank"
                            rel="noreferrer"
                            className="inline-flex items-center space-x-1 text-indigo-400 hover:text-cyan-300 text-xs font-mono"
                          >
                            <span>Citation</span>
                            <ExternalLink className="w-3 h-3" />
                          </a>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </section>
  );
};
