import React, { useState, useMemo } from 'react';
import { AppRecord, BuildabilityVerdict, AccessTier, MCPStatus } from '../types';
import {
  Search,
  Filter,
  Download,
  ExternalLink,
  ChevronUp,
  ChevronDown,
  Layers,
  Sparkles,
  ShieldCheck,
  CheckCircle2,
  AlertCircle,
  Lock,
  Cpu,
  Eye,
  RotateCcw
} from 'lucide-react';
import { downloadJsonFile, downloadCsvFile } from '../services/api';
import { AppDetailModal } from './AppDetailModal';

interface AppMatrixProps {
  apps: AppRecord[];
  onSelectAppForDemo?: (app: AppRecord) => void;
}

export const AppMatrix: React.FC<AppMatrixProps> = ({ apps, onSelectAppForDemo }) => {
  // State
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedBuildability, setSelectedBuildability] = useState<string>('All');
  const [selectedAccessTier, setSelectedAccessTier] = useState<string>('All');
  const [selectedAuth, setSelectedAuth] = useState<string>('All');
  const [selectedMcp, setSelectedMcp] = useState<string>('All');

  // Sorting
  const [sortField, setSortField] = useState<keyof AppRecord>('id');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('asc');

  // Modal State
  const [inspectedApp, setInspectedApp] = useState<AppRecord | null>(null);

  // Extract unique filter options
  const categories = useMemo(() => ['All', ...Array.from(new Set(apps.map(a => a.category))).sort()], [apps]);
  const buildabilityOptions = ['All', 'Build Now', 'Build With Prerequisites', 'Outreach Required'];
  const accessOptions = [
    'All',
    'Free self-serve',
    'Trial self-serve',
    'Paid self-serve',
    'Admin approval',
    'Partner approval',
    'Contact sales',
  ];
  const authOptions = ['All', 'OAuth2', 'API Key', 'HTTP Basic', 'PAT', 'Local CLI', 'Custom'];
  const mcpOptions = ['All', 'Official MCP (14)', 'Community MCP (76)', 'No MCP Server (10)'];

  // Filtering & Sorting logic
  const filteredApps = useMemo(() => {
    return apps.filter(app => {
      // Search
      if (searchQuery.trim()) {
        const q = searchQuery.toLowerCase().trim();
        const matchesName = app.app_name.toLowerCase().includes(q);
        const matchesDesc = app.description.toLowerCase().includes(q);
        const matchesCat = app.category.toLowerCase().includes(q);
        const matchesBlocker = app.main_blocker.toLowerCase().includes(q);
        const matchesProtocol = app.api_type.toLowerCase().includes(q);
        const matchesAuth = app.primary_auth.toLowerCase().includes(q);
        if (!matchesName && !matchesDesc && !matchesCat && !matchesBlocker && !matchesProtocol && !matchesAuth) {
          return false;
        }
      }

      // Category
      if (selectedCategory !== 'All' && app.category !== selectedCategory) {
        return false;
      }

      // Buildability
      if (selectedBuildability !== 'All' && app.buildability !== selectedBuildability) {
        return false;
      }

      // Access Tier
      if (selectedAccessTier !== 'All' && app.access_tier !== selectedAccessTier) {
        return false;
      }

      // Auth
      if (selectedAuth !== 'All') {
        const matchesPrimary = app.primary_auth.toLowerCase().includes(selectedAuth.toLowerCase());
        const matchesAny = app.auth_methods.some(m => m.toLowerCase().includes(selectedAuth.toLowerCase()));
        if (!matchesPrimary && !matchesAny) return false;
      }

      // MCP
      if (selectedMcp !== 'All') {
        if (selectedMcp.includes('Official') && app.official_mcp !== 'Yes') return false;
        if (selectedMcp.includes('Community') && app.community_mcp !== 'Yes') return false;
        if (selectedMcp.includes('No MCP') && (app.official_mcp === 'Yes' || app.community_mcp === 'Yes')) return false;
      }

      return true;
    }).sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];

      if (aVal === bVal) return 0;
      if (aVal === null || aVal === undefined) return 1;
      if (bVal === null || bVal === undefined) return -1;

      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
      }

      const strA = String(aVal).toLowerCase();
      const strB = String(bVal).toLowerCase();
      return sortDirection === 'asc' ? strA.localeCompare(strB) : strB.localeCompare(strA);
    });
  }, [
    apps,
    searchQuery,
    selectedCategory,
    selectedBuildability,
    selectedAccessTier,
    selectedAuth,
    selectedMcp,
    sortField,
    sortDirection,
  ]);

  const handleSort = (field: keyof AppRecord) => {
    if (sortField === field) {
      setSortDirection(prev => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const handleResetFilters = () => {
    setSearchQuery('');
    setSelectedCategory('All');
    setSelectedBuildability('All');
    setSelectedAccessTier('All');
    setSelectedAuth('All');
    setSelectedMcp('All');
  };

  const hasActiveFilters =
    searchQuery !== '' ||
    selectedCategory !== 'All' ||
    selectedBuildability !== 'All' ||
    selectedAccessTier !== 'All' ||
    selectedAuth !== 'All' ||
    selectedMcp !== 'All';

  const getBuildBadge = (verdict: string) => {
    switch (verdict) {
      case 'Build Now':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'Build With Prerequisites':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Outreach Required':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      default:
        return 'bg-slate-700/40 text-slate-400 border-slate-600';
    }
  };

  const getAccessBadge = (tier: string) => {
    if (tier.includes('Free')) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20';
    if (tier.includes('Trial')) return 'text-teal-300 bg-teal-500/10 border-teal-500/20';
    if (tier.includes('Paid')) return 'text-cyan-300 bg-cyan-500/10 border-cyan-500/20';
    if (tier.includes('Admin')) return 'text-amber-400 bg-amber-500/10 border-amber-500/20';
    return 'text-rose-400 bg-rose-500/10 border-rose-500/20';
  };

  return (
    <section id="matrix" className="py-16 border-t border-slate-800/80 bg-[#080b13]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <div className="flex flex-col lg:flex-row lg:items-end justify-between mb-8 gap-4">
          <div className="max-w-3xl">
            <div className="inline-flex items-center space-x-2 text-xs font-semibold uppercase tracking-wider text-indigo-400 mb-2">
              <Layers className="w-3.5 h-3.5" />
              <span>Full Canonical Dataset</span>
            </div>
            <h2 className="text-2xl sm:text-4xl font-extrabold text-white tracking-tight">
              100-App Research & Verification Matrix
            </h2>
            <p className="mt-2 text-slate-400 text-sm leading-relaxed">
              Complete catalog of investigated targets across 10 categories. Filter by authentication protocols, gating barriers, MCP readiness, or live full-text search.
            </p>
          </div>

          {/* Quick Exports */}
          <div className="flex items-center space-x-3 shrink-0">
            <button
              onClick={() => downloadJsonFile(filteredApps)}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-slate-900 hover:bg-slate-800 text-slate-200 border border-slate-700/80 text-xs font-semibold transition-all shadow-sm"
            >
              <Download className="w-3.5 h-3.5 text-indigo-400" />
              <span>Export JSON ({filteredApps.length})</span>
            </button>
            <button
              onClick={() => downloadCsvFile(filteredApps)}
              className="flex items-center space-x-1.5 px-3.5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-semibold transition-all shadow-md shadow-indigo-600/30"
            >
              <Download className="w-3.5 h-3.5 text-white" />
              <span>Export CSV ({filteredApps.length})</span>
            </button>
          </div>
        </div>

        {/* Filter Controls Box */}
        <div className="glass-panel rounded-2xl p-4 sm:p-5 border border-slate-800 mb-6 space-y-4">
          {/* Top Bar: Search + Category Quick Filter */}
          <div className="flex flex-col md:flex-row items-center gap-3">
            {/* Search Input */}
            <div className="relative w-full md:w-96">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500" />
              <input
                type="text"
                placeholder="Search app name, protocol, blocker, description..."
                value={searchQuery}
                onChange={e => setSearchQuery(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-900/90 border border-slate-800 focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-xs text-white placeholder-slate-500 outline-none transition-all"
              />
              {searchQuery && (
                <button
                  onClick={() => setSearchQuery('')}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-xs text-slate-500 hover:text-white"
                >
                  ✕
                </button>
              )}
            </div>

            {/* Quick Stats & Reset */}
            <div className="w-full md:w-auto flex items-center justify-between md:justify-end space-x-3 ml-auto text-xs text-slate-400">
              <span>
                Showing <strong className="text-white font-mono">{filteredApps.length}</strong> of{' '}
                <strong className="text-white font-mono">100</strong> apps
              </span>
              {hasActiveFilters && (
                <button
                  onClick={handleResetFilters}
                  className="flex items-center space-x-1 text-xs text-indigo-400 hover:text-indigo-300 font-semibold transition-colors"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                  <span>Reset Filters</span>
                </button>
              )}
            </div>
          </div>

          {/* Secondary Dropdown Filter Row */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-5 gap-3 pt-3 border-t border-slate-800/80">
            {/* Category Dropdown */}
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Category</label>
              <select
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 outline-none focus:border-indigo-500"
              >
                {categories.map(c => (
                  <option key={c} value={c}>{c}</option>
                ))}
              </select>
            </div>

            {/* Buildability Dropdown */}
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Buildability</label>
              <select
                value={selectedBuildability}
                onChange={e => setSelectedBuildability(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 outline-none focus:border-indigo-500"
              >
                {buildabilityOptions.map(b => (
                  <option key={b} value={b}>{b}</option>
                ))}
              </select>
            </div>

            {/* Access Tier Dropdown */}
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Access Tier</label>
              <select
                value={selectedAccessTier}
                onChange={e => setSelectedAccessTier(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 outline-none focus:border-indigo-500"
              >
                {accessOptions.map(a => (
                  <option key={a} value={a}>{a}</option>
                ))}
              </select>
            </div>

            {/* Primary Auth Dropdown */}
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">Auth Protocol</label>
              <select
                value={selectedAuth}
                onChange={e => setSelectedAuth(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 outline-none focus:border-indigo-500"
              >
                {authOptions.map(auth => (
                  <option key={auth} value={auth}>{auth}</option>
                ))}
              </select>
            </div>

            {/* MCP Dropdown */}
            <div>
              <label className="text-[11px] font-semibold text-slate-400 block mb-1">MCP Ecosystem</label>
              <select
                value={selectedMcp}
                onChange={e => setSelectedMcp(e.target.value)}
                className="w-full px-2.5 py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs text-slate-200 outline-none focus:border-indigo-500"
              >
                {mcpOptions.map(mcp => (
                  <option key={mcp} value={mcp}>{mcp}</option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Table Container */}
        <div className="glass-panel rounded-2xl border border-slate-800 overflow-hidden shadow-2xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="bg-slate-900/90 border-b border-slate-800 text-slate-400 font-semibold uppercase tracking-wider text-[11px]">
                  <th
                    onClick={() => handleSort('id')}
                    className="py-3.5 px-4 cursor-pointer hover:text-white transition-colors w-16"
                  >
                    <div className="flex items-center space-x-1">
                      <span>#</span>
                      {sortField === 'id' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('app_name')}
                    className="py-3.5 px-4 cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center space-x-1">
                      <span>App Name</span>
                      {sortField === 'app_name' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th
                    onClick={() => handleSort('category')}
                    className="py-3.5 px-4 cursor-pointer hover:text-white transition-colors hidden md:table-cell"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Category</span>
                      {sortField === 'category' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th className="py-3.5 px-4">Auth Protocol</th>
                  <th className="py-3.5 px-4 hidden lg:table-cell">Access Tier</th>
                  <th className="py-3.5 px-4 hidden sm:table-cell">API Surface</th>
                  <th className="py-3.5 px-4">MCP Status</th>
                  <th
                    onClick={() => handleSort('buildability')}
                    className="py-3.5 px-4 cursor-pointer hover:text-white transition-colors"
                  >
                    <div className="flex items-center space-x-1">
                      <span>Buildability</span>
                      {sortField === 'buildability' && (sortDirection === 'asc' ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />)}
                    </div>
                  </th>
                  <th className="py-3.5 px-4 text-right">Evidence</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/80">
                {filteredApps.length === 0 ? (
                  <tr>
                    <td colSpan={9} className="py-12 text-center text-slate-400">
                      <AlertCircle className="w-8 h-8 text-slate-500 mx-auto mb-2" />
                      <p className="text-sm font-semibold text-slate-300">No applications match your filter criteria.</p>
                      <button
                        onClick={handleResetFilters}
                        className="mt-2 text-xs text-indigo-400 hover:text-indigo-300 underline"
                      >
                        Reset all filters
                      </button>
                    </td>
                  </tr>
                ) : (
                  filteredApps.map(app => (
                    <tr
                      key={app.id}
                      onClick={() => setInspectedApp(app)}
                      className="hover:bg-slate-800/40 cursor-pointer transition-colors group"
                    >
                      {/* ID */}
                      <td className="py-3.5 px-4 font-mono text-slate-500 text-xs">
                        #{app.id}
                      </td>

                      {/* App Name */}
                      <td className="py-3.5 px-4 font-semibold text-white">
                        <div className="flex items-center space-x-2">
                          <span className="group-hover:text-cyan-300 transition-colors">{app.app_name}</span>
                          <span className="text-[10px] text-slate-500 hidden sm:inline truncate max-w-[150px]">
                            {app.description.slice(0, 35)}...
                          </span>
                        </div>
                      </td>

                      {/* Category */}
                      <td className="py-3.5 px-4 text-slate-300 hidden md:table-cell">
                        <span className="px-2 py-0.5 rounded-md bg-slate-900 border border-slate-800 text-[11px]">
                          {app.category}
                        </span>
                      </td>

                      {/* Auth */}
                      <td className="py-3.5 px-4">
                        <div className="flex items-center space-x-1.5">
                          <span className="font-mono text-xs text-indigo-300 font-medium">
                            {app.primary_auth}
                          </span>
                          {app.auth_methods.length > 1 && (
                            <span className="text-[10px] px-1 rounded bg-indigo-950/80 text-indigo-400 border border-indigo-500/30">
                              +{app.auth_methods.length - 1}
                            </span>
                          )}
                        </div>
                      </td>

                      {/* Access Tier */}
                      <td className="py-3.5 px-4 hidden lg:table-cell">
                        <span className={`px-2 py-0.5 rounded-full text-[11px] font-medium border ${getAccessBadge(app.access_tier)}`}>
                          {app.access_tier}
                        </span>
                      </td>

                      {/* API Surface */}
                      <td className="py-3.5 px-4 hidden sm:table-cell text-slate-300">
                        <span className="font-mono text-[11px] text-slate-300 truncate max-w-[180px] block" title={app.api_surface}>
                          {app.api_type} ({app.api_surface.slice(0, 24)}...)
                        </span>
                      </td>

                      {/* MCP */}
                      <td className="py-3.5 px-4">
                        {app.official_mcp === 'Yes' ? (
                          <span className="px-2 py-0.5 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/30 text-[10px] font-bold">
                            Official MCP
                          </span>
                        ) : app.community_mcp === 'Yes' ? (
                          <span className="px-2 py-0.5 rounded-md bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 text-[10px] font-medium">
                            Community MCP
                          </span>
                        ) : (
                          <span className="text-[11px] text-slate-600 font-mono">None</span>
                        )}
                      </td>

                      {/* Buildability */}
                      <td className="py-3.5 px-4">
                        <span className={`px-2.5 py-0.5 rounded-full text-[11px] font-semibold border ${getBuildBadge(app.buildability)}`}>
                          {app.buildability}
                        </span>
                      </td>

                      {/* Evidence & Action */}
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end space-x-2">
                          <span className="px-2 py-0.5 rounded bg-slate-900 border border-slate-800 text-[10px] text-slate-400 font-mono hidden sm:inline">
                            {app.evidence_excerpts.length} quotes
                          </span>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setInspectedApp(app);
                            }}
                            className="p-1.5 rounded-lg bg-slate-800/80 hover:bg-slate-700 text-indigo-400 hover:text-white transition-colors"
                            title="Inspect Evidence & Citations"
                          >
                            <Eye className="w-3.5 h-3.5" />
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        {/* Modal Inspector Component */}
        {inspectedApp && (
          <AppDetailModal
            app={inspectedApp}
            onClose={() => setInspectedApp(null)}
            onTriggerResearch={(id) => {
              if (onSelectAppForDemo) {
                onSelectAppForDemo(inspectedApp);
              }
              setInspectedApp(null);
            }}
          />
        )}
      </div>
    </section>
  );
};
