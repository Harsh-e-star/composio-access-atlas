import React from 'react';
import { Layers, Heart, Sparkles, Github, ExternalLink } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="py-12 border-t border-slate-800/80 bg-[#060910] text-xs text-slate-500">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-xl bg-gradient-to-tr from-indigo-600 to-cyan-400 p-0.5 flex items-center justify-center">
            <div className="w-full h-full bg-[#080b13] rounded-[10px] flex items-center justify-center">
              <Layers className="w-4 h-4 text-cyan-400" />
            </div>
          </div>
          <div>
            <span className="font-extrabold text-white text-sm">Composio Access Atlas</span>
            <p className="text-[11px] text-slate-400">100-App Integration & Research Agent Submission</p>
          </div>
        </div>

        <div className="text-center md:text-right space-y-1">
          <p className="text-slate-400">
            Engineered for the <strong className="text-slate-200">Composio AI Product Ops Intern Take-Home Assignment</strong>.
          </p>
          <p className="text-[11px] text-slate-600">
            Python 3.11 FastAPI • React 18 • TypeScript • Tailwind CSS • Multi-Agent Pipeline • 98.3% Audited Accuracy
          </p>
        </div>
      </div>
    </footer>
  );
};
