import React from 'react';
import { Building2, Sparkles, Database, FileText } from 'lucide-react';

export const MicroPage: React.FC = () => {
  return (
    <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-6">
      <div className="w-16 h-16 rounded-3xl bg-purple-500/10 border border-purple-500/20 text-purple-400 flex items-center justify-center mx-auto shadow-2xl shadow-purple-500/10">
        <Building2 className="w-8 h-8" />
      </div>

      <div className="space-y-2">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-purple-500/10 border border-purple-500/20 text-purple-300 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Coming in Phase 4</span>
        </div>
        <h2 className="text-2xl font-bold text-white tracking-tight">Micro View: SEC EDGAR Company Deep Dive</h2>
        <p className="text-sm text-slate-400 max-w-lg mx-auto leading-relaxed">
          Zoom in on company fundamentals (10-K & 10-Q revenue, net income, operating margins, R&D intensity) directly from the SEC EDGAR Company Facts API, matched against sector trends.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 pt-6 text-left">
        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2">
          <Database className="w-5 h-5 text-cyan-400" />
          <h4 className="text-sm font-semibold text-white">Zero-Auth SEC EDGAR</h4>
          <p className="text-xs text-slate-400">Direct unauthenticated XBRL financial statement extraction for all US public companies.</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2">
          <FileText className="w-5 h-5 text-purple-400" />
          <h4 className="text-sm font-semibold text-white">Competitor Benchmarking</h4>
          <p className="text-xs text-slate-400">Side-by-side margin and growth comparisons against mapped rivals from the company graph.</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/60 border border-slate-800/80 space-y-2">
          <Sparkles className="w-5 h-5 text-emerald-400" />
          <h4 className="text-sm font-semibold text-white">Integrated Macro Context</h4>
          <p className="text-xs text-slate-400">Correlate company revenue and demand metrics directly with macroeconomic CPI, policy rate, and GDP prints.</p>
        </div>
      </div>
    </div>
  );
};
