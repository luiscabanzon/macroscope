import React, { useState } from 'react';
import { Search, ZoomIn, ZoomOut, RotateCcw, X } from 'lucide-react';
import { GraphNode } from '../../types/graph.ts';

export const SECTOR_COLORS: Record<string, string> = {
  'Information Technology': '#38bdf8', // sky-400
  'Communication Services': '#818cf8', // indigo-400
  'Consumer Discretionary': '#fb923c', // orange-400
  'Consumer Staples': '#facc15',       // yellow-400
  'Financials': '#34d399',             // emerald-400
  'Energy': '#f43f5e',                 // rose-500
  'Health Care': '#c084fc',            // purple-400
  'Industrials': '#2dd4bf',            // teal-400
  'Materials': '#a3e635',              // lime-400
  'Real Estate': '#fb7185',            // rose-400
  'Utilities': '#60a5fa',              // blue-400
};

export const DEFAULT_COLOR = '#94a3b8'; // slate-400

interface GraphControlsProps {
  sectors: string[];
  selectedSector: string | null;
  onSelectSector: (sector: string | null) => void;
  nodes: GraphNode[];
  onSelectCompany: (ticker: string) => void;
  onZoomIn: () => void;
  onZoomOut: () => void;
  onResetZoom: () => void;
}

export const GraphControls: React.FC<GraphControlsProps> = ({
  sectors,
  selectedSector,
  onSelectSector,
  nodes,
  onSelectCompany,
  onZoomIn,
  onZoomOut,
  onResetZoom,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showSearchResults, setShowSearchResults] = useState(false);

  const filteredNodes = searchQuery.trim()
    ? nodes.filter(
        (n) =>
          n.ticker.toLowerCase().includes(searchQuery.toLowerCase()) ||
          n.name.toLowerCase().includes(searchQuery.toLowerCase())
      ).slice(0, 8)
    : [];

  return (
    <div className="absolute top-4 left-4 right-4 z-20 pointer-events-none flex flex-col md:flex-row items-start md:items-center justify-between gap-3">
      {/* Search & Sector Bar */}
      <div className="pointer-events-auto flex flex-wrap items-center gap-2 bg-slate-900/90 backdrop-blur-md p-1.5 rounded-2xl border border-slate-800 shadow-2xl max-w-full">
        {/* Search Input */}
        <div className="relative">
          <div className="flex items-center bg-slate-950/80 px-3 py-1.5 rounded-xl border border-slate-800 focus-within:border-cyan-500/60 focus-within:ring-1 focus-within:ring-cyan-500/30 transition-all">
            <Search className="w-3.5 h-3.5 text-slate-400 mr-2 shrink-0" />
            <input
              type="text"
              placeholder="Search ticker or name..."
              value={searchQuery}
              onChange={(e) => {
                setSearchQuery(e.target.value);
                setShowSearchResults(true);
              }}
              onFocus={() => setShowSearchResults(true)}
              className="bg-transparent text-xs text-white placeholder-slate-500 focus:outline-none w-36 sm:w-48 font-medium"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                className="text-slate-400 hover:text-slate-200 ml-1"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>

          {/* Search Dropdown */}
          {showSearchResults && filteredNodes.length > 0 && (
            <div className="absolute top-full mt-1.5 left-0 w-64 bg-slate-900 border border-slate-800 rounded-xl shadow-2xl py-1.5 z-30 max-h-60 overflow-y-auto">
              {filteredNodes.map((n) => (
                <button
                  key={n.ticker}
                  onClick={() => {
                    onSelectCompany(n.ticker);
                    setShowSearchResults(false);
                    setSearchQuery('');
                  }}
                  className="w-full text-left px-3 py-2 text-xs hover:bg-slate-800 flex items-center justify-between transition-colors"
                >
                  <div>
                    <span className="font-bold text-white font-mono mr-2">{n.ticker}</span>
                    <span className="text-slate-300 truncate max-w-[120px] inline-block align-bottom">
                      {n.name}
                    </span>
                  </div>
                  <span
                    className="w-2.5 h-2.5 rounded-full shrink-0"
                    style={{ backgroundColor: SECTOR_COLORS[n.sector] ?? DEFAULT_COLOR }}
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        <div className="h-5 w-[1px] bg-slate-800 hidden sm:block" />

        {/* Sector Pills */}
        <div className="flex items-center gap-1 overflow-x-auto max-w-[calc(100vw-3rem)] sm:max-w-xl py-0.5 no-scrollbar">
          <button
            onClick={() => onSelectSector(null)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
              selectedSector === null
                ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
            }`}
          >
            All Sectors ({nodes.length})
          </button>

          {sectors.map((sector) => {
            const isSelected = selectedSector === sector;
            const color = SECTOR_COLORS[sector] ?? DEFAULT_COLOR;
            return (
              <button
                key={sector}
                onClick={() => onSelectSector(isSelected ? null : sector)}
                className={`flex items-center space-x-1.5 px-2.5 py-1 rounded-lg text-xs font-medium whitespace-nowrap transition-all ${
                  isSelected
                    ? 'bg-slate-800 text-white border border-slate-700 shadow-sm'
                    : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/50'
                }`}
              >
                <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: color }} />
                <span>{sector}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Canvas Zoom & View Controls */}
      <div className="pointer-events-auto flex items-center space-x-1 bg-slate-900/90 backdrop-blur-md p-1 rounded-xl border border-slate-800 shadow-2xl">
        <button
          onClick={onZoomIn}
          title="Zoom In"
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <ZoomIn className="w-4 h-4" />
        </button>
        <button
          onClick={onZoomOut}
          title="Zoom Out"
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <ZoomOut className="w-4 h-4" />
        </button>
        <button
          onClick={onResetZoom}
          title="Reset View"
          className="p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <RotateCcw className="w-4 h-4" />
        </button>
      </div>
    </div>
  );
};
