import React, { useEffect, useRef, useState, useCallback, useImperativeHandle, forwardRef } from 'react';
import * as d3Force from 'd3-force';
import * as d3Zoom from 'd3-zoom';
import * as d3Selection from 'd3-selection';
import { GraphEdge, GraphNode } from '../../types/graph.ts';
import { SECTOR_COLORS, DEFAULT_COLOR } from './GraphControls.tsx';

interface SimulationNode extends GraphNode {
  radius: number;
}

interface SimulationEdge extends GraphEdge {
  source: SimulationNode;
  target: SimulationNode;
}

export interface GraphCanvasRef {
  zoomIn: () => void;
  zoomOut: () => void;
  resetZoom: () => void;
  focusNode: (ticker: string) => void;
}

interface GraphCanvasProps {
  nodes: GraphNode[];
  edges: GraphEdge[];
  selectedTicker: string | null;
  onSelectNode: (ticker: string) => void;
}

function getNodeRadius(tier: string | null): number {
  if (tier === 'Mega') return 22;
  if (tier === 'Large') return 16;
  return 12;
}

export const GraphCanvas = forwardRef<GraphCanvasRef, GraphCanvasProps>(
  ({ nodes, edges, selectedTicker, onSelectNode }, ref) => {
    const containerRef = useRef<HTMLDivElement>(null);
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [hoveredNode, setHoveredNode] = useState<SimulationNode | null>(null);

    const simulationRef = useRef<d3Force.Simulation<SimulationNode, SimulationEdge> | null>(null);
    const zoomBehaviorRef = useRef<d3Zoom.ZoomBehavior<HTMLCanvasElement, unknown> | null>(null);
    const transformRef = useRef<d3Zoom.ZoomTransform>(d3Zoom.zoomIdentity);
    const simNodesRef = useRef<SimulationNode[]>([]);
    const simEdgesRef = useRef<SimulationEdge[]>([]);

    // Expose zoom and focus controls to parent
    useImperativeHandle(ref, () => ({
      zoomIn: () => {
        if (!canvasRef.current || !zoomBehaviorRef.current) return;
        zoomBehaviorRef.current.scaleBy(d3Selection.select(canvasRef.current), 1.3);
      },
      zoomOut: () => {
        if (!canvasRef.current || !zoomBehaviorRef.current) return;
        zoomBehaviorRef.current.scaleBy(d3Selection.select(canvasRef.current), 0.7);
      },
      resetZoom: () => {
        if (!canvasRef.current || !zoomBehaviorRef.current) return;
        zoomBehaviorRef.current.transform(d3Selection.select(canvasRef.current), d3Zoom.zoomIdentity);
      },
      focusNode: (ticker: string) => {
        const target = simNodesRef.current.find((n) => n.ticker === ticker);
        if (!target || target.x === undefined || target.y === undefined || !canvasRef.current || !zoomBehaviorRef.current) return;
        const width = canvasRef.current.width / (window.devicePixelRatio || 1);
        const height = canvasRef.current.height / (window.devicePixelRatio || 1);
        const transform = d3Zoom.zoomIdentity.translate(width / 2 - target.x * 1.5, height / 2 - target.y * 1.5).scale(1.5);
        zoomBehaviorRef.current.transform(d3Selection.select(canvasRef.current), transform);
      },
    }));

    // Setup and run simulation
    useEffect(() => {
      if (!canvasRef.current || !containerRef.current) return;

      const container = containerRef.current;
      const width = container.clientWidth;
      const height = container.clientHeight;
      const dpr = window.devicePixelRatio || 1;

      const canvas = canvasRef.current;
      canvas.width = width * dpr;
      canvas.height = height * dpr;

      // Prepare simulation nodes
      const simNodes: SimulationNode[] = nodes.map((n) => ({
        ...n,
        radius: getNodeRadius(n.market_cap_tier),
        x: n.x ?? width / 2 + (Math.random() - 0.5) * 400,
        y: n.y ?? height / 2 + (Math.random() - 0.5) * 400,
      }));

      const nodeMap = new Map<string, SimulationNode>(simNodes.map((n) => [n.ticker, n]));

      // Prepare simulation edges
      const simEdges: SimulationEdge[] = [];
      for (const e of edges) {
        const srcId = typeof e.source === 'string' ? e.source : e.source.ticker;
        const tgtId = typeof e.target === 'string' ? e.target : e.target.ticker;
        const sourceNode = nodeMap.get(srcId);
        const targetNode = nodeMap.get(tgtId);
        if (sourceNode && targetNode) {
          simEdges.push({
            ...e,
            source: sourceNode,
            target: targetNode,
          });
        }
      }

      simNodesRef.current = simNodes;
      simEdgesRef.current = simEdges;

      // D3 Force Simulation
      const simulation = d3Force
        .forceSimulation<SimulationNode>(simNodes)
        .force(
          'link',
          d3Force
            .forceLink<SimulationNode, SimulationEdge>(simEdges)
            .id((d) => d.ticker)
            .distance((d) => (d.relationship_type === 'direct_competitor' ? 80 : 130))
            .strength(0.4)
        )
        .force('charge', d3Force.forceManyBody().strength(-240))
        .force('center', d3Force.forceCenter(width / 2, height / 2).strength(0.08))
        .force('collide', d3Force.forceCollide<SimulationNode>().radius((d) => d.radius + 14).strength(0.8));

      simulationRef.current = simulation;

      // Render loop
      const render = () => {
        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        ctx.save();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.scale(dpr, dpr);

        const transform = transformRef.current;
        ctx.translate(transform.x, transform.y);
        ctx.scale(transform.k, transform.k);

        const activeTicker = selectedTicker;

        // Draw Edges
        for (const edge of simEdges) {
          const isDirect = edge.relationship_type === 'direct_competitor';
          const isConnectedToSelected =
            activeTicker &&
            (edge.source.ticker === activeTicker || edge.target.ticker === activeTicker);

          ctx.beginPath();
          ctx.moveTo(edge.source.x!, edge.source.y!);
          ctx.lineTo(edge.target.x!, edge.target.y!);

          if (isConnectedToSelected) {
            ctx.strokeStyle = '#38bdf8'; // Cyan glow
            ctx.lineWidth = 2.5;
            ctx.globalAlpha = 0.95;
            ctx.setLineDash([]);
          } else if (activeTicker) {
            // Fade out unrelated edges
            ctx.strokeStyle = '#334155';
            ctx.lineWidth = 0.8;
            ctx.globalAlpha = 0.15;
            ctx.setLineDash(isDirect ? [] : [4, 4]);
          } else {
            ctx.strokeStyle = isDirect ? '#475569' : '#334155';
            ctx.lineWidth = isDirect ? 1.2 : 0.8;
            ctx.globalAlpha = isDirect ? 0.45 : 0.25;
            ctx.setLineDash(isDirect ? [] : [4, 4]);
          }

          ctx.stroke();
        }

        // Draw Nodes
        for (const node of simNodes) {
          if (node.x === undefined || node.y === undefined) continue;

          const isSelected = node.ticker === activeTicker;
          const isHovered = hoveredNode?.ticker === node.ticker;
          const color = SECTOR_COLORS[node.sector] ?? DEFAULT_COLOR;
          const radius = node.radius;

          // Outer selection glow
          if (isSelected || isHovered) {
            ctx.beginPath();
            ctx.arc(node.x, node.y, radius + 7, 0, Math.PI * 2);
            ctx.fillStyle = `${color}35`;
            ctx.fill();

            ctx.beginPath();
            ctx.arc(node.x, node.y, radius + 3, 0, Math.PI * 2);
            ctx.strokeStyle = isSelected ? '#ffffff' : color;
            ctx.lineWidth = 2;
            ctx.stroke();
          }

          // Main node circle
          ctx.beginPath();
          ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
          ctx.fillStyle = isSelected ? '#0f172a' : '#1e293b';
          ctx.fill();
          ctx.strokeStyle = color;
          ctx.lineWidth = isSelected ? 3 : 2;
          ctx.stroke();

          // Node Ticker Label
          ctx.font = `600 ${Math.max(9, Math.round(radius * 0.65))}px "JetBrains Mono", monospace`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillStyle = isSelected ? '#38bdf8' : '#f8fafc';
          ctx.fillText(node.ticker, node.x, node.y);

          // Competitor degree badge (small circle on top-right)
          if (node.competitor_count > 0 && !isSelected) {
            const badgeX = node.x + radius * 0.7;
            const badgeY = node.y - radius * 0.7;
            ctx.beginPath();
            ctx.arc(badgeX, badgeY, 5, 0, Math.PI * 2);
            ctx.fillStyle = color;
            ctx.fill();
          }
        }

        ctx.restore();
      };

      simulation.on('tick', render);

      // Setup D3 Zoom
      const zoom = d3Zoom
        .zoom<HTMLCanvasElement, unknown>()
        .scaleExtent([0.3, 4.0])
        .on('zoom', (event) => {
          transformRef.current = event.transform;
          render();
        });

      zoomBehaviorRef.current = zoom;
      d3Selection.select(canvas).call(zoom);

      return () => {
        simulation.stop();
      };
    }, [nodes, edges, selectedTicker]);

    // Handle mouse move for hover detection
    const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const rect = canvas.getBoundingClientRect();
      const clientX = e.clientX - rect.left;
      const clientY = e.clientY - rect.top;

      // Invert zoom transform to find canvas coordinates
      const transform = transformRef.current;
      const x = (clientX - transform.x) / transform.k;
      const y = (clientY - transform.y) / transform.k;

      let found: SimulationNode | null = null;
      for (const node of simNodesRef.current) {
        if (node.x === undefined || node.y === undefined) continue;
        const dx = x - node.x;
        const dy = y - node.y;
        if (dx * dx + dy * dy <= (node.radius + 6) * (node.radius + 6)) {
          found = node;
          break;
        }
      }

      setHoveredNode(found);
      canvas.style.cursor = found ? 'pointer' : 'default';
    }, []);

    // Handle canvas click to select node
    const handleClick = useCallback(() => {
      if (hoveredNode) {
        onSelectNode(hoveredNode.ticker);
      }
    }, [hoveredNode, onSelectNode]);

    return (
      <div ref={containerRef} className="relative w-full h-full overflow-hidden bg-slate-950 select-none">
        <canvas
          ref={canvasRef}
          onMouseMove={handleMouseMove}
          onClick={handleClick}
          className="w-full h-full block"
        />

        {/* Hover Tooltip */}
        {hoveredNode && (
          <div
            className="absolute pointer-events-none z-30 px-3 py-2 rounded-xl bg-slate-900/95 backdrop-blur-md border border-slate-700/80 shadow-2xl text-xs"
            style={{
              left: `${Math.min(window.innerWidth - 240, (hoveredNode.x ?? 0) * transformRef.current.k + transformRef.current.x + 20)}px`,
              top: `${Math.max(20, (hoveredNode.y ?? 0) * transformRef.current.k + transformRef.current.y - 40)}px`,
            }}
          >
            <div className="flex items-center space-x-2">
              <span className="font-mono font-bold text-white text-sm">{hoveredNode.ticker}</span>
              <span
                className="text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
                style={{
                  backgroundColor: `${SECTOR_COLORS[hoveredNode.sector] ?? DEFAULT_COLOR}20`,
                  color: SECTOR_COLORS[hoveredNode.sector] ?? DEFAULT_COLOR,
                }}
              >
                {hoveredNode.sector}
              </span>
            </div>
            <p className="text-slate-300 font-medium text-xs mt-0.5">{hoveredNode.name}</p>
            <div className="flex items-center space-x-3 mt-1.5 text-[10px] text-slate-400">
              <span>{hoveredNode.industry}</span>
              <span>•</span>
              <span className="text-cyan-400 font-semibold">{hoveredNode.competitor_count} Competitor Links</span>
            </div>
          </div>
        )}
      </div>
    );
  }
);
