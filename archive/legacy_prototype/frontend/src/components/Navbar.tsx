import React, { useState, useEffect } from 'react';
import { Layers, Database, Sparkles, CheckCircle2, Download, Terminal, BarChart3, ShieldCheck, Cpu } from 'lucide-react';
import { checkBackendHealth, downloadJsonFile, downloadCsvFile } from '../services/api';
import { AppRecord } from '../types';

interface NavbarProps {
  apps: AppRecord[];
  activeSection: string;
}

export const Navbar: React.FC<NavbarProps> = ({ apps, activeSection }) => {
  const [backendLive, setBackendLive] = useState<boolean | null>(null);

  useEffect(() => {
    checkBackendHealth().then(isLive => setBackendLive(isLive));
  }, []);

  const navItems = [
    { id: 'overview', label: 'Overview', icon: BarChart3 },
    { id: 'insights', label: 'Insights', icon: Sparkles },
    { id: 'landscape', label: 'Landscape', icon: Layers },
    { id: 'matrix', label: '100-App Matrix', icon: Database },
    { id: 'architecture', label: 'Architecture', icon: Cpu },
    { id: 'demo', label: 'Live Agent', icon: Terminal },
    { id: 'verification', label: 'Verification (98.3%)', icon: ShieldCheck },
    { id: 'recommendations', label: 'Roadmap', icon: CheckCircle2 },
  ];

  return (
    <header className="sticky top-0 z-50 w-full border-b border-slate-800/80 bg-[#080b13]/85 backdrop-blur-xl transition-all">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 via-indigo-500 to-cyan-400 p-0.5 shadow-lg shadow-indigo-500/20 flex items-center justify-center">
            <div className="w-full h-full bg-[#080b13] rounded-[10px] flex items-center justify-center">
              <Layers className="w-5 h-5 text-cyan-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-extrabold text-base tracking-tight bg-gradient-to-r from-white via-slate-200 to-indigo-300 bg-clip-text text-transparent">
                Composio Access Atlas
              </span>
              <span className="px-1.5 py-0.5 text-[10px] font-semibold bg-indigo-500/20 text-indigo-400 border border-indigo-500/30 rounded-md">
                100 Apps
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">AI Integration Feasibility & Verification Matrix</p>
          </div>
        </div>

        {/* Navigation Links */}
        <nav className="hidden lg:flex items-center space-x-1">
          {navItems.map(item => {
            const Icon = item.icon;
            const isActive = activeSection === item.id;
            return (
              <a
                key={item.id}
                href={`#${item.id}`}
                className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                  isActive
                    ? 'text-white bg-indigo-500/20 border border-indigo-500/30 shadow-sm shadow-indigo-500/10'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
                }`}
              >
                <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </a>
            );
          })}
        </nav>

        {/* Actions & Status */}
        <div className="flex items-center space-x-2 sm:space-x-3">
          {/* Backend Status Pill */}
          <div
            title={backendLive ? 'FastAPI Backend Online' : 'Running on Embedded Offline Dataset'}
            className="flex items-center space-x-1.5 px-2.5 py-1 rounded-full text-[11px] font-medium bg-slate-900 border border-slate-800"
          >
            <span
              className={`w-2 h-2 rounded-full ${
                backendLive === true
                  ? 'bg-emerald-400 shadow-sm shadow-emerald-400/80 animate-pulse'
                  : backendLive === false
                  ? 'bg-amber-400'
                  : 'bg-slate-500'
              }`}
            />
            <span className="text-slate-300 text-[11px] hidden sm:inline">
              {backendLive === true ? 'API Live' : 'Embedded DB'}
            </span>
          </div>

          {/* Quick Exports */}
          <button
            onClick={() => downloadJsonFile(apps)}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-slate-800/90 hover:bg-slate-700 text-slate-200 border border-slate-700/80 transition-colors"
            title="Export JSON"
          >
            <Download className="w-3.5 h-3.5 text-indigo-400" />
            <span className="hidden sm:inline">JSON</span>
          </button>
          <button
            onClick={() => downloadCsvFile(apps)}
            className="flex items-center space-x-1 px-2.5 py-1.5 rounded-lg text-xs font-medium bg-indigo-600 hover:bg-indigo-500 text-white font-semibold transition-all shadow-sm shadow-indigo-600/30"
            title="Export CSV"
          >
            <Download className="w-3.5 h-3.5 text-white" />
            <span className="hidden sm:inline">CSV</span>
          </button>
        </div>
      </div>
    </header>
  );
};
