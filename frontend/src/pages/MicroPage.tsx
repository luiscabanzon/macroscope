import React, { useState, useEffect } from 'react';
import { useCompanyFundamentals, useCompetitorBenchmark } from '../api/useMicro.ts';
import { useGraph } from '../api/useGraph.ts';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
  Legend,
} from 'recharts';
import {
  Building2,
  TrendingUp,
  TrendingDown,
  Layers,
  Loader2,
  DollarSign,
  Percent,
  Cpu,
  ShieldCheck,
  ChevronDown,
} from 'lucide-react';
import { SECTOR_COLORS, DEFAULT_COLOR } from '../components/graph/GraphControls.tsx';

interface MicroPageProps {
  initialTicker?: string;
}

export const MicroPage: React.FC<MicroPageProps> = ({ initialTicker = 'NVDA' }) => {
  const [selectedTicker, setSelectedTicker] = useState(initialTicker);
  const [frequency, setFrequency] = useState<'Q' | 'A'>('Q');
  const [benchmarkMetric, setBenchmarkMetric] = useState('operating_margin');

  useEffect(() => {
    if (initialTicker) {
      setSelectedTicker(initialTicker);
    }
  }, [initialTicker]);

  const { data: graphData } = useGraph();
  const { data: fundamentals, isLoading } = useCompanyFundamentals(selectedTicker);
  const { data: benchmarkData } = useCompetitorBenchmark(selectedTicker, benchmarkMetric);

  const series =
    frequency === 'Q'
      ? fundamentals?.quarterly_series ?? []
      : fundamentals?.annual_series ?? [];

  const summary = fundamentals?.summary_metrics;
  const sectorColor = fundamentals?.sector
    ? SECTOR_COLORS[fundamentals.sector] ?? DEFAULT_COLOR
    : DEFAULT_COLOR;

  const formatCurrency = (val: number | null) => {
    if (val === null || val === undefined) return 'N/A';
    if (Math.abs(val) >= 1e9) return `$${(val / 1e9).toFixed(1)}B`;
    if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(1)}M`;
    return `$${val.toLocaleString()}`;
  };

  if (isLoading && !fundamentals) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center min-h-[calc(100vh-4rem)] bg-slate-950">
        <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mb-3" />
        <p className="text-sm font-medium text-slate-400">Loading SEC EDGAR XBRL Fundamentals for {selectedTicker}...</p>
      </div>
    );
  }

  const chartSeries = series.map((s) => ({
    ...s,
    revenueBillions: s.revenue ? Number((s.revenue / 1e9).toFixed(2)) : null,
    netIncomeBillions: s.net_income ? Number((s.net_income / 1e9).toFixed(2)) : null,
    operatingIncomeBillions: s.operating_income ? Number((s.operating_income / 1e9).toFixed(2)) : null,
  }));

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Header & Company Switcher */}
      <div className="bg-slate-900/80 backdrop-blur-md p-5 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          {/* Ticker Selector */}
          <div className="relative">
            <select
              value={selectedTicker}
              onChange={(e) => setSelectedTicker(e.target.value)}
              className="appearance-none bg-slate-950 px-4 py-2 pr-9 rounded-xl border border-slate-700/80 text-sm font-bold text-white focus:outline-none focus:border-cyan-500 cursor-pointer font-mono"
            >
              {graphData?.nodes.map((n) => (
                <option key={n.ticker} value={n.ticker}>
                  {n.ticker} — {n.name}
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
          </div>

          {fundamentals && (
            <div className="flex items-center space-x-2">
              <span
                className="text-xs font-semibold px-2.5 py-1 rounded-full"
                style={{
                  backgroundColor: `${sectorColor}20`,
                  color: sectorColor,
                  border: `1px solid ${sectorColor}40`,
                }}
              >
                {fundamentals.sector}
              </span>
              <span className="text-xs text-slate-400 hidden sm:inline">•</span>
              <span className="text-xs text-slate-400 hidden sm:inline">{fundamentals.industry}</span>
              {fundamentals.cik && (
                <span className="text-[11px] font-mono text-slate-500 bg-slate-950 px-2 py-0.5 rounded border border-slate-800">
                  CIK: {fundamentals.cik}
                </span>
              )}
            </div>
          )}
        </div>

        {/* Annual / Quarterly Toggle */}
        <div className="flex items-center space-x-1 bg-slate-950/80 p-1 rounded-xl border border-slate-800">
          <button
            onClick={() => setFrequency('Q')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              frequency === 'Q'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Quarterly (10-Q)
          </button>
          <button
            onClick={() => setFrequency('A')}
            className={`px-3 py-1.5 rounded-lg text-xs font-semibold transition-all ${
              frequency === 'A'
                ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-500/30'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Annual (10-K)
          </button>
        </div>
      </div>

      {/* Financial Health KPI Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        {/* LTM Revenue */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">LTM Total Revenue</span>
            <DollarSign className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5">
            {formatCurrency(summary?.ltm_revenue ?? null)}
          </div>
          <div className="mt-2 text-[11px] text-slate-400 flex items-center space-x-1">
            {summary?.revenue_growth_yoy !== null && summary?.revenue_growth_yoy !== undefined && (
              <span
                className={`flex items-center font-semibold ${
                  summary.revenue_growth_yoy >= 0 ? 'text-emerald-400' : 'text-rose-400'
                }`}
              >
                {summary.revenue_growth_yoy >= 0 ? (
                  <TrendingUp className="w-3 h-3 mr-0.5" />
                ) : (
                  <TrendingDown className="w-3 h-3 mr-0.5" />
                )}
                {summary.revenue_growth_yoy}% YoY
              </span>
            )}
            <span className="text-slate-600">vs prior period</span>
          </div>
        </div>

        {/* Operating Margin */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">Operating Margin</span>
            <Percent className="w-4 h-4 text-cyan-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5">
            {summary?.operating_margin !== null && summary?.operating_margin !== undefined
              ? `${summary.operating_margin}%`
              : 'N/A'}
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Core operating profitability</div>
        </div>

        {/* Net Profit Margin */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">Net Profit Margin</span>
            <Building2 className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5">
            {summary?.net_margin !== null && summary?.net_margin !== undefined
              ? `${summary.net_margin}%`
              : 'N/A'}
          </div>
          <div className="mt-2 text-[11px] text-slate-500">Bottom-line net margin</div>
        </div>

        {/* R&D Intensity */}
        <div className="p-4 rounded-2xl bg-slate-900/60 border border-slate-800/80">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold">R&D Intensity</span>
            <Cpu className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1.5">
            {summary?.rnd_intensity !== null && summary?.rnd_intensity !== undefined
              ? `${summary.rnd_intensity}%`
              : 'N/A'}
          </div>
          <div className="mt-2 text-[11px] text-slate-500">R&D as % of total revenue</div>
        </div>
      </div>

      {/* Grid of Financial Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Chart 1: Revenue & Net Income Trajectory */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <DollarSign className="w-4 h-4 text-emerald-400" />
                <span>Revenue & Net Income Trajectory</span>
              </h3>
              <p className="text-xs text-slate-400">Historical $USD Billions ({frequency === 'Q' ? 'Quarterly' : 'Annual'})</p>
            </div>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartSeries}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="period_date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} unit="B" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Bar dataKey="revenueBillions" name="Revenue ($B)" fill="#38bdf8" radius={[4, 4, 0, 0]} />
                <Bar dataKey="netIncomeBillions" name="Net Income ($B)" fill="#34d399" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Chart 2: Profitability & Margin Structure */}
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-3">
          <div className="flex items-center justify-between border-b border-slate-800/60 pb-3">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center space-x-2">
                <Percent className="w-4 h-4 text-cyan-400" />
                <span>Margin Dynamics & Cost Structure</span>
              </h3>
              <p className="text-xs text-slate-400">Gross vs. Operating vs. Net Margin (%)</p>
            </div>
          </div>

          <div className="h-72 w-full pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={series}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="period_date" stroke="#64748b" tick={{ fontSize: 10 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 10 }} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                />
                <Legend wrapperStyle={{ fontSize: 11 }} />
                <Line
                  type="monotone"
                  dataKey="gross_margin"
                  name="Gross Margin %"
                  stroke="#a78bfa"
                  strokeWidth={2}
                  dot={{ r: 2 }}
                />
                <Line
                  type="monotone"
                  dataKey="operating_margin"
                  name="Operating Margin %"
                  stroke="#38bdf8"
                  strokeWidth={2.5}
                  dot={{ r: 3 }}
                />
                <Line
                  type="monotone"
                  dataKey="net_margin"
                  name="Net Margin %"
                  stroke="#34d399"
                  strokeWidth={2}
                  dot={{ r: 2 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Chart 3: Peer Competitor Benchmark */}
      <div className="p-6 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-slate-800/60 pb-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <Layers className="w-4 h-4 text-emerald-400" />
              <span>Direct Peer Competitor Benchmark</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Side-by-side quarterly comparison against graph rivals:{' '}
              <span className="font-semibold text-cyan-300">
                {benchmarkData?.competitors.join(', ') || 'No rivals mapped'}
              </span>
            </p>
          </div>

          {/* Metric Selector for Benchmark */}
          <div className="flex items-center space-x-2">
            <span className="text-xs text-slate-400 font-medium">Metric:</span>
            <select
              value={benchmarkMetric}
              onChange={(e) => setBenchmarkMetric(e.target.value)}
              className="bg-slate-950 px-3 py-1.5 rounded-lg border border-slate-700 text-xs font-semibold text-white focus:outline-none focus:border-emerald-500"
            >
              <option value="operating_margin">Operating Margin (%)</option>
              <option value="net_margin">Net Profit Margin (%)</option>
              <option value="gross_margin">Gross Margin (%)</option>
              <option value="rnd_intensity">R&D Intensity (%)</option>
              <option value="revenue_growth_yoy">YoY Revenue Growth (%)</option>
            </select>
          </div>
        </div>

        <div className="h-80 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={benchmarkData?.data ?? []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="period_date" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} unit={benchmarkData?.unit ?? '%'} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
              />
              <Legend wrapperStyle={{ fontSize: 11 }} />
              {/* Highlight target company */}
              <Line
                type="monotone"
                dataKey={`values.${selectedTicker}`}
                name={`${selectedTicker} (Target)`}
                stroke="#38bdf8"
                strokeWidth={3}
                dot={{ r: 4, fill: '#38bdf8' }}
              />
              {/* Plot rivals with distinct colors */}
              {benchmarkData?.competitors.map((peer, idx) => (
                <Line
                  key={peer}
                  type="monotone"
                  dataKey={`values.${peer}`}
                  name={peer}
                  stroke={['#34d399', '#f43f5e', '#fb923c', '#a78bfa'][idx % 4]}
                  strokeWidth={2}
                  strokeDasharray="4 4"
                  dot={{ r: 2 }}
                />
              ))}
            </LineChart>
          </ResponsiveContainer>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-500 pt-2 border-t border-slate-800/40">
          <span className="flex items-center space-x-1.5">
            <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
            <span>Extracted via keyless SEC EDGAR XBRL (10-K & 10-Q)</span>
          </span>
          <span className="text-[11px] font-mono">Frequencies aligned by Calendar Quarter</span>
        </div>
      </div>
    </div>
  );
};
