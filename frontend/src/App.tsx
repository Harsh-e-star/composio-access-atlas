import React, { useState, useEffect } from 'react';
import { AppRecord, AnalyticsSummary, VerificationData } from './types';
import { fetchApps, fetchAnalytics, fetchVerification } from './services/api';
import { Navbar } from './components/Navbar';
import { Hero } from './components/Hero';
import { ExecutiveInsights } from './components/ExecutiveInsights';
import { IntegrationLandscape } from './components/IntegrationLandscape';
import { AppMatrix } from './components/AppMatrix';
import { AgentArchitecture } from './components/AgentArchitecture';
import { LiveAgentDemo } from './components/LiveAgentDemo';
import { VerificationReport } from './components/VerificationReport';
import { Recommendations } from './components/Recommendations';
import { Reproducibility } from './components/Reproducibility';
import { Footer } from './components/Footer';

export const App: React.FC = () => {
  const [apps, setApps] = useState<AppRecord[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsSummary | null>(null);
  const [verification, setVerification] = useState<VerificationData | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [activeSection, setActiveSection] = useState<string>('overview');
  const [demoSelectedApp, setDemoSelectedApp] = useState<AppRecord | null>(null);

  useEffect(() => {
    async function loadData() {
      try {
        const [loadedApps, loadedAnalytics, loadedVerification] = await Promise.all([
          fetchApps(),
          fetchAnalytics(),
          fetchVerification(),
        ]);
        setApps(loadedApps);
        setAnalytics(loadedAnalytics);
        setVerification(loadedVerification);
      } catch (err) {
        console.error('Failed to load initial data:', err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  // Update active section on scroll
  useEffect(() => {
    const sectionIds = [
      'overview',
      'insights',
      'landscape',
      'matrix',
      'architecture',
      'demo',
      'verification',
      'recommendations',
      'reproducibility',
    ];

    const handleScroll = () => {
      const scrollY = window.scrollY;
      for (const id of sectionIds) {
        const el = document.getElementById(id);
        if (el) {
          const top = el.offsetTop - 120;
          const height = el.offsetHeight;
          if (scrollY >= top && scrollY < top + height) {
            setActiveSection(id);
            break;
          }
        }
      }
    };

    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  const handleSelectAppForDemo = (app: AppRecord) => {
    setDemoSelectedApp(app);
    const demoEl = document.getElementById('demo');
    if (demoEl) {
      demoEl.scrollIntoView({ behavior: 'smooth' });
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#080b13] flex flex-col items-center justify-center text-slate-400">
        <div className="w-12 h-12 rounded-2xl bg-indigo-600/20 border border-indigo-500/40 flex items-center justify-center animate-pulse mb-4">
          <div className="w-5 h-5 rounded-lg bg-indigo-500 animate-spin" />
        </div>
        <p className="text-sm font-semibold text-white tracking-wide">Loading Composio Access Atlas...</p>
        <p className="text-xs text-slate-500 mt-1">Bootstrapping 100-App Canonical Dataset</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#080b13] text-slate-100 flex flex-col">
      <Navbar apps={apps} activeSection={activeSection} />

      <main className="flex-1">
        <Hero analytics={analytics} metrics={verification?.metrics ?? null} />
        <ExecutiveInsights analytics={analytics} />
        <IntegrationLandscape analytics={analytics} />
        <AppMatrix apps={apps} onSelectAppForDemo={handleSelectAppForDemo} />
        <AgentArchitecture />
        <LiveAgentDemo apps={apps} initialSelectedApp={demoSelectedApp} />
        <VerificationReport data={verification} />
        <Recommendations analytics={analytics} />
        <Reproducibility />
      </main>

      <Footer />
    </div>
  );
};

export default App;
