import React, { useState, useRef } from 'react';
import { useGraph } from '../api/useGraph.ts';
import { GraphCanvas, GraphCanvasRef } from '../components/graph/GraphCanvas.tsx';
import { GraphControls } from '../components/graph/GraphControls.tsx';
import { NewsDrawer } from '../components/graph/NewsDrawer.tsx';
import { Loader2, AlertCircle } from 'lucide-react';
import { NetworkType } from '../types/graph.ts';

interface GraphPageProps {
  onDeepDive?: (ticker: string) => void;
}

export const GraphPage: React.FC<GraphPageProps> = ({ onDeepDive }) => {
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [networkType, setNetworkType] = useState<NetworkType>('all');
  const [selectedTicker, setSelectedTicker] = useState<string | null>(null);
  const canvasRef = useRef<GraphCanvasRef>(null);

  const { data: graphData, isLoading, error } = useGraph(selectedSector, networkType);

  const handleSelectCompany = (ticker: string) => {
    setSelectedTicker(ticker);
    canvasRef.current?.focusNode(ticker);
  };

  if (isLoading) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] bg-slate-950">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mb-3" />
        <p className="text-sm font-medium text-slate-400">Loading S&P 500 & NASDAQ 100 Company Network...</p>
      </div>
    );
  }

  if (error || !graphData) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] bg-slate-950 p-6 text-center">
        <AlertCircle className="w-10 h-10 text-rose-500 mb-3" />
        <h3 className="text-base font-semibold text-white">Failed to load company network graph</h3>
        <p className="text-xs text-slate-400 mt-1 max-w-md">
          {error instanceof Error ? error.message : 'Please check that the backend server is running.'}
        </p>
      </div>
    );
  }

  return (
    <div className="relative w-full h-[calc(100vh-4rem)] overflow-hidden flex flex-col bg-slate-950">
      {/* Interactive Controls Bar */}
      <GraphControls
        sectors={graphData.sectors}
        selectedSector={selectedSector}
        onSelectSector={setSelectedSector}
        networkType={networkType}
        onSelectNetworkType={setNetworkType}
        nodes={graphData.nodes}
        onSelectCompany={handleSelectCompany}
        onZoomIn={() => canvasRef.current?.zoomIn()}
        onZoomOut={() => canvasRef.current?.zoomOut()}
        onResetZoom={() => canvasRef.current?.resetZoom()}
      />

      {/* Interactive Force-Directed Canvas */}
      <div className="flex-1 w-full h-full">
        <GraphCanvas
          ref={canvasRef}
          nodes={graphData.nodes}
          edges={graphData.edges}
          selectedTicker={selectedTicker}
          onSelectNode={handleSelectCompany}
        />
      </div>

      {/* Contextual News Drawer */}
      <NewsDrawer
        ticker={selectedTicker}
        onClose={() => setSelectedTicker(null)}
        onSelectCompany={handleSelectCompany}
        onDeepDive={onDeepDive}
      />
    </div>
  );
};
