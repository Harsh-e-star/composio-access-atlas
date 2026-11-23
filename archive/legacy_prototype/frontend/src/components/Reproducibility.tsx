import React, { useState } from 'react';
import { Terminal, Copy, Check, ExternalLink, GitBranch, Play, ShieldAlert, Cpu } from 'lucide-react';

export const Reproducibility: React.FC = () => {
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const commands = [
    {
      title: '1. Setup & Environment',
      desc: 'Create Python 3.11 virtualenv and install pinned backend dependencies:',
      cmd: 'cd backend\nuv venv --python 3.11\nsource .venv/bin/activate\nuv pip install -r requirements.txt',
    },
    {
      title: '2. Execute Complete 100-App Dataset Build',
      desc: 'Build canonical SQLite DB, validation artifacts, and exports:',
      cmd: 'cd backend\nuv run python -m app.build_complete_dataset',
    },
    {
      title: '3. Run Automated 26-Test Invariant Suite',
      desc: 'Execute pytest across dataset schemas, analytics engine, and REST endpoints:',
      cmd: 'cd backend\nuv run pytest',
    },
    {
      title: '4. Start FastAPI Backend Server',
      desc: 'Launch REST API with CORS and OpenAPI docs on port 8000:',
      cmd: 'cd backend\nuv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload',
    },
    {
      title: '5. Launch React Frontend Dashboard',
      desc: 'Install node modules and start Vite development server on port 3000:',
      cmd: 'cd frontend\nnpm install\nnpm run dev',
    },
  ];

  const handleCopy = (text: string, idx: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <section id="reproducibility" className="py-16 border-t border-slate-800/80 bg-[#0a0e1a]/80">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="max-w-3xl mb-10">
          <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-cyan-400 mb-2">
            <Terminal className="w-3.5 h-3.5" />
            <span>Developer Reproducibility & Pipeline Guide</span>
          </div>
          <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
            Run the Research Agent Locally
          </h2>
          <p className="mt-3 text-slate-400 text-sm sm:text-base leading-relaxed">
            Every metric, citation, and verification calculation in this case study is 100% reproducible. Follow the step-by-step commands below to execute the pipeline locally.
          </p>
        </div>

        {/* Command Cards */}
        <div className="space-y-4 mb-10">
          {commands.map((c, idx) => (
            <div key={idx} className="glass-panel rounded-2xl p-5 border border-slate-800 text-xs">
              <div className="flex items-center justify-between mb-1.5">
                <span className="font-bold text-white text-sm">{c.title}</span>
                <button
                  onClick={() => handleCopy(c.cmd, idx)}
                  className="flex items-center space-x-1 px-2.5 py-1 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  {copiedIndex === idx ? (
                    <>
                      <Check className="w-3.5 h-3.5 text-emerald-400" />
                      <span className="text-[11px] text-emerald-400">Copied</span>
                    </>
                  ) : (
                    <>
                      <Copy className="w-3.5 h-3.5" />
                      <span className="text-[11px]">Copy Command</span>
                    </>
                  )}
                </button>
              </div>
              <p className="text-slate-400 mb-3">{c.desc}</p>
              <pre className="p-3.5 rounded-xl bg-[#06080e] border border-slate-800/80 text-cyan-300 font-mono text-xs overflow-x-auto leading-relaxed">
                {c.cmd}
              </pre>
            </div>
          ))}
        </div>

        {/* Technical Constraints & Guardrails */}
        <div className="glass-panel rounded-2xl p-6 border border-slate-800">
          <h3 className="text-base font-bold text-white mb-3 flex items-center space-x-2">
            <ShieldAlert className="w-4 h-4 text-amber-400" />
            <span>Methodological Limitations & Constraints</span>
          </h3>
          <ul className="text-xs text-slate-400 space-y-2 leading-relaxed list-disc list-inside">
            <li>
              <strong className="text-slate-300">Rate Limiting & Dynamic Paywalls:</strong> Certain SaaS platforms (e.g. PitchBook, Amazon SP) gate developer portal access behind corporate credentials or aggressive Cloudflare challenges; findings reflect official public developer documentation.
            </li>
            <li>
              <strong className="text-slate-300">MCP Protocol Velocity:</strong> The Model Context Protocol specification continues to evolve rapidly. While 14 official and 76 community servers were verified as of this audit, vendor announcements occur weekly.
            </li>
            <li>
              <strong className="text-slate-300">Sandbox Isolation:</strong> Live agent re-research in sandbox environments relies on non-blocking async yields and resilient fallback caching to guarantee 100% operational uptime without depending on external web flaky connections.
            </li>
          </ul>
        </div>
      </div>
    </section>
  );
};
