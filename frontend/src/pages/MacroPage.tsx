import React, { useState } from 'react';
import { useCountries, useDashboard, useRefreshDashboard, useComparison } from '../api/useMacro.ts';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from 'recharts';
import {
  TrendingUp,
  TrendingDown,
  RefreshCw,
  Clock,
  ShieldCheck,
  ChevronDown,
  Layers,
} from 'lucide-react';

export const MacroPage: React.FC = () => {
  const [selectedCountry, setSelectedCountry] = useState('USA');
  const [selectedIndicator, setSelectedIndicator] = useState('gdp_growth');
  const [compareMode, setCompareMode] = useState(false);
  const [comparedCountries] = useState<string[]>(['USA', 'GBR', 'DEU']);

  const { data: countries } = useCountries();
  const { data: dashboard, isLoading: isDashboardLoading } = useDashboard(selectedCountry);
  const refreshMutation = useRefreshDashboard();

  const { data: comparisonData } = useComparison(
    compareMode ? comparedCountries : [],
    selectedIndicator
  );

  const handleRefresh = () => {
    refreshMutation.mutate(selectedCountry);
  };

  const activeSeries = dashboard?.series[selectedIndicator];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
      {/* Top Command Bar */}
      <div className="bg-slate-900/80 backdrop-blur-md p-4 rounded-2xl border border-slate-800 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-3">
          {/* Country Selector */}
          <div className="relative">
            <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="appearance-none bg-slate-950 px-4 py-2 pr-9 rounded-xl border border-slate-700/80 text-sm font-semibold text-white focus:outline-none focus:border-emerald-500 cursor-pointer"
            >
              {countries?.map((c) => (
                <option key={c.code} value={c.code}>
                  {c.name} ({c.code})
                </option>
              ))}
            </select>
            <ChevronDown className="w-4 h-4 text-slate-400 absolute right-3 top-3 pointer-events-none" />
          </div>

          {/* Compare Toggle */}
          <button
            onClick={() => setCompareMode(!compareMode)}
            className={`flex items-center space-x-1.5 px-3 py-2 rounded-xl text-xs font-semibold border transition-all ${
              compareMode
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            <Layers className="w-3.5 h-3.5" />
            <span>Compare G7 Economies</span>
          </button>
        </div>

        {/* Cache Freshness & Refresh Button */}
        <div className="flex items-center space-x-3 text-xs text-slate-400">
          <div className="flex items-center space-x-1.5 bg-slate-950/60 px-3 py-1.5 rounded-lg border border-slate-800/80">
            <Clock className="w-3.5 h-3.5 text-slate-500" />
            <span>
              {dashboard?.is_stale ? (
                <span className="text-amber-400">Stale Cache Fallback</span>
              ) : (
                <span className="text-emerald-400">Cached Read-Through</span>
              )}
            </span>
          </div>

          <button
            onClick={handleRefresh}
            disabled={refreshMutation.isPending}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-medium transition-colors disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${refreshMutation.isPending ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* KPI Ribbon */}
      <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
        {isDashboardLoading ? (
          Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="h-28 bg-slate-900/60 border border-slate-800 rounded-2xl animate-pulse" />
          ))
        ) : (
          dashboard?.kpis.map((kpi) => {
            const isSelected = selectedIndicator === kpi.indicator_slug;
            const delta = kpi.delta_yoy ?? kpi.delta_mom;
            const isPositive = delta !== null && delta > 0;

            return (
              <button
                key={kpi.indicator_slug}
                onClick={() => setSelectedIndicator(kpi.indicator_slug)}
                className={`text-left p-4 rounded-2xl border transition-all ${
                  isSelected
                    ? 'bg-slate-800/90 border-emerald-500/60 shadow-lg shadow-emerald-500/10'
                    : 'bg-slate-900/60 border-slate-800/80 hover:bg-slate-800/40'
                }`}
              >
                <div className="text-[11px] font-semibold text-slate-400 line-clamp-1">{kpi.indicator_name}</div>
                <div className="text-xl font-bold font-mono text-white mt-1">
                  {kpi.latest_value}
                  <span className="text-xs text-slate-400 font-sans ml-1 font-normal">{kpi.unit}</span>
                </div>

                <div className="flex items-center justify-between mt-2 pt-2 border-t border-slate-800/60 text-[10px]">
                  <span className="text-slate-500 font-mono">{kpi.period_date.slice(0, 4)}</span>
                  {delta !== null && (
                    <span
                      className={`flex items-center space-x-0.5 font-semibold ${
                        isPositive ? 'text-emerald-400' : 'text-rose-400'
                      }`}
                    >
                      {isPositive ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                      <span>{Math.abs(delta)}</span>
                    </span>
                  )}
                </div>
              </button>
            );
          })
        )}
      </div>

      {/* Primary Chart Area */}
      <div className="bg-slate-900/80 backdrop-blur-md p-6 rounded-2xl border border-slate-800 space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-slate-800/80 pb-4">
          <div>
            <h3 className="text-base font-bold text-white flex items-center space-x-2">
              <span>{activeSeries?.indicator_name ?? selectedIndicator}</span>
              <span className="text-xs font-normal text-slate-400">({activeSeries?.unit ?? '%'})</span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">
              Historical time-series trend • Frequency: {activeSeries?.frequency ?? 'Annual'}
            </p>
          </div>

          <div className="flex items-center space-x-2 text-xs text-slate-400">
            <ShieldCheck className="w-4 h-4 text-emerald-400" />
            <span>Source: {activeSeries?.source ?? 'World Bank / FRED'}</span>
          </div>
        </div>

        <div className="h-80 w-full pt-4">
          <ResponsiveContainer width="100%" height="100%">
            {compareMode && comparisonData ? (
              <LineChart data={comparisonData.data}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="period_date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                />
                {comparisonData.countries.map((c, idx) => (
                  <Line
                    key={c}
                    type="monotone"
                    dataKey={`values.${c}`}
                    name={c}
                    stroke={['#38bdf8', '#34d399', '#f43f5e', '#fb923c'][idx % 4]}
                    strokeWidth={2}
                    dot={false}
                  />
                ))}
              </LineChart>
            ) : (
              <LineChart data={activeSeries?.data ?? []}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="period_date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem' }}
                />
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke="#34d399"
                  strokeWidth={2.5}
                  dot={{ r: 3, fill: '#34d399' }}
                  activeDot={{ r: 6 }}
                />
              </LineChart>
            )}
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};
