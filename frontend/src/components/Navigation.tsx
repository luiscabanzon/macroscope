import React from 'react';
import { Network, Globe, Building2, ExternalLink, Activity } from 'lucide-react';

export type ActiveTab = 'macro' | 'micro' | 'graph';

interface NavigationProps {
  activeTab: ActiveTab;
  onTabChange: (tab: ActiveTab) => void;
}

export const Navigation: React.FC<NavigationProps> = ({ activeTab, onTabChange }) => {
  return (
    <header className="border-b border-slate-800 bg-slate-900/80 backdrop-blur-md sticky top-0 z-40">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand */}
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-emerald-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-emerald-500/20">
            <Activity className="w-5 h-5 text-slate-950 stroke-[2.5]" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="text-lg font-bold tracking-tight text-white">MacroScope</span>
              <span className="text-[10px] uppercase font-semibold px-1.5 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                Keyless
              </span>
            </div>
            <p className="text-xs text-slate-400 hidden sm:block">Open Macro & Market Intelligence</p>
          </div>
        </div>

        {/* View Switcher Tabs */}
        <nav className="flex items-center bg-slate-950/60 p-1 rounded-xl border border-slate-800/80 space-x-1">
          <button
            onClick={() => onTabChange('graph')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'graph'
                ? 'bg-slate-800 text-white shadow-sm shadow-black/40 border border-slate-700/60'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <Network className="w-4 h-4 text-cyan-400" />
            <span>Company Graph</span>
            <span className="w-2 h-2 rounded-full bg-cyan-400 animate-pulse ml-1" />
          </button>

          <button
            onClick={() => onTabChange('macro')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'macro'
                ? 'bg-slate-800 text-white shadow-sm shadow-black/40 border border-slate-700/60'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <Globe className="w-4 h-4 text-emerald-400" />
            <span>Macro View</span>
          </button>

          <button
            onClick={() => onTabChange('micro')}
            className={`flex items-center space-x-2 px-3.5 py-1.5 rounded-lg text-sm font-medium transition-all ${
              activeTab === 'micro'
                ? 'bg-slate-800 text-white shadow-sm shadow-black/40 border border-slate-700/60'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-900/60'
            }`}
          >
            <Building2 className="w-4 h-4 text-purple-400" />
            <span>Micro View</span>
            <span className="text-[10px] text-purple-300 font-semibold px-1 py-0.2 rounded bg-purple-500/20">
              v2
            </span>
          </button>
        </nav>

        {/* API Docs link */}
        <div className="hidden md:flex items-center space-x-4">
          <a
            href="http://127.0.0.1:8000/docs"
            target="_blank"
            rel="noreferrer"
            className="flex items-center space-x-1.5 text-xs font-medium text-slate-400 hover:text-slate-200 transition-colors px-2.5 py-1.5 rounded-lg hover:bg-slate-800/60 border border-transparent hover:border-slate-700/60"
          >
            <span>OpenAPI Docs</span>
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
        </div>
      </div>
    </header>
  );
};
