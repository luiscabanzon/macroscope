import React, { useState } from 'react';
import { X, RefreshCw, ExternalLink, Calendar, ArrowRight, Building, Radio, FileText } from 'lucide-react';
import { useCompany, useCompanyNews, useRefreshCompanyNews } from '../../api/useGraph.ts';
import { SECTOR_COLORS, DEFAULT_COLOR } from './GraphControls.tsx';

interface NewsDrawerProps {
  ticker: string | null;
  onClose: () => void;
  onSelectCompany: (ticker: string) => void;
  onDeepDive?: (ticker: string) => void;
}

type NewsTab = 'company' | 'competitors' | 'sector';

export const NewsDrawer: React.FC<NewsDrawerProps> = ({
  ticker,
  onClose,
  onSelectCompany,
  onDeepDive,
}) => {
  const [activeTab, setActiveTab] = useState<NewsTab>('company');
  const { data: company, isLoading: isCompanyLoading } = useCompany(ticker);
  const { data: news, isLoading: isNewsLoading, isFetching: isNewsFetching } = useCompanyNews(ticker);
  const refreshMutation = useRefreshCompanyNews();

  if (!ticker) return null;

  const sectorColor = company?.sector ? SECTOR_COLORS[company.sector] ?? DEFAULT_COLOR : DEFAULT_COLOR;

  const handleRefresh = () => {
    if (ticker) {
      refreshMutation.mutate(ticker);
    }
  };

  const currentArticles =
    activeTab === 'company'
      ? news?.company_news ?? []
      : activeTab === 'competitors'
      ? news?.competitor_news ?? []
      : news?.sector_news ?? [];

  return (
    <div className="fixed inset-y-0 right-0 w-full sm:w-[460px] lg:w-[500px] bg-slate-900/95 backdrop-blur-xl border-l border-slate-800 shadow-2xl z-50 flex flex-col transition-all duration-300 animate-in slide-in-from-right">
      {/* Header */}
      <div className="p-5 border-b border-slate-800/80 bg-slate-950/40 relative">
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-1.5 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors"
        >
          <X className="w-5 h-5" />
        </button>

        {isCompanyLoading ? (
          <div className="animate-pulse space-y-2">
            <div className="h-6 bg-slate-800 rounded w-24" />
            <div className="h-4 bg-slate-800 rounded w-48" />
          </div>
        ) : (
          <div>
            <div className="flex items-center space-x-2.5 mb-1.5">
              <span className="font-mono text-2xl font-bold text-white tracking-tight">{company?.ticker}</span>
              <span
                className="text-[11px] font-semibold px-2 py-0.5 rounded-full"
                style={{
                  backgroundColor: `${sectorColor}18`,
                  color: sectorColor,
                  border: `1px solid ${sectorColor}30`,
                }}
              >
                {company?.sector}
              </span>
              {company?.market_cap_tier && (
                <span className="text-[10px] font-semibold px-2 py-0.5 rounded-md bg-slate-800 text-slate-300 border border-slate-700/60">
                  {company.market_cap_tier} Cap
                </span>
              )}
            </div>

            <h2 className="text-sm font-semibold text-slate-200 line-clamp-1">{company?.name}</h2>
            <p className="text-xs text-slate-400 mt-0.5 flex items-center space-x-1.5">
              <Building className="w-3.5 h-3.5 text-slate-500" />
              <span>{company?.industry}</span>
            </p>

            {onDeepDive && company && (
              <button
                onClick={() => onDeepDive(company.ticker)}
                className="mt-3 w-full flex items-center justify-between py-2 px-3 rounded-lg bg-gradient-to-r from-cyan-950/60 to-blue-950/60 hover:from-cyan-900/60 hover:to-blue-900/60 border border-cyan-500/30 hover:border-cyan-400/60 text-cyan-300 hover:text-white text-xs font-semibold shadow-sm transition-all group"
              >
                <div className="flex items-center space-x-2">
                  <FileText className="w-4 h-4 text-cyan-400 group-hover:scale-110 transition-transform" />
                  <span>Deep Dive Fundamentals</span>
                </div>
                <span className="flex items-center space-x-1 text-[11px] text-cyan-400/80 group-hover:text-cyan-200">
                  <span>SEC EDGAR</span>
                  <ArrowRight className="w-3.5 h-3.5 group-hover:translate-x-0.5 transition-transform" />
                </span>
              </button>
            )}
          </div>
        )}

        {/* Competitor Chips */}
        {company?.competitors && company.competitors.length > 0 && (
          <div className="mt-3.5 pt-3 border-t border-slate-800/60">
            <div className="flex items-center justify-between mb-1.5">
              <span className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
                Direct Rivals & Peers ({company.competitors.length})
              </span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {company.competitors.map((comp) => (
                <button
                  key={comp.ticker}
                  onClick={() => onSelectCompany(comp.ticker)}
                  className="group flex items-center space-x-1.5 px-2 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/50 text-xs font-medium text-slate-200 hover:text-white transition-all shadow-sm"
                  title={`${comp.name} (${comp.relationship_type.replace('_', ' ')})`}
                >
                  <span className="font-mono font-bold text-cyan-300">{comp.ticker}</span>
                  <span className="text-[11px] text-slate-400 group-hover:text-slate-300 hidden sm:inline">
                    {comp.name.split(' ')[0]}
                  </span>
                  <ArrowRight className="w-2.5 h-2.5 opacity-40 group-hover:opacity-100 group-hover:translate-x-0.5 transition-all text-cyan-400" />
                </button>
              ))}
            </div>
          </div>
        )}
      </div>

      {/* Tabs & Controls */}
      <div className="px-5 py-2.5 border-b border-slate-800/80 bg-slate-900/60 flex items-center justify-between">
        <div className="flex items-center space-x-1 bg-slate-950/60 p-0.5 rounded-lg border border-slate-800/60">
          <button
            onClick={() => setActiveTab('company')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
              activeTab === 'company'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Company ({news?.company_news?.length ?? 0})
          </button>
          <button
            onClick={() => setActiveTab('competitors')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
              activeTab === 'competitors'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Competitors ({news?.competitor_news?.length ?? 0})
          </button>
          <button
            onClick={() => setActiveTab('sector')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
              activeTab === 'sector'
                ? 'bg-slate-800 text-white shadow-sm'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Sector ({news?.sector_news?.length ?? 0})
          </button>
        </div>

        <button
          onClick={handleRefresh}
          disabled={refreshMutation.isPending || isNewsFetching}
          className="flex items-center space-x-1 text-xs text-slate-400 hover:text-white px-2 py-1 rounded hover:bg-slate-800/80 transition-colors disabled:opacity-50"
          title="Refresh RSS Feeds"
        >
          <RefreshCw
            className={`w-3.5 h-3.5 ${
              refreshMutation.isPending || isNewsFetching ? 'animate-spin text-cyan-400' : ''
            }`}
          />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>

      {/* Articles Feed */}
      <div className="flex-1 overflow-y-auto p-5 space-y-3.5 divide-y divide-slate-800/40">
        {isNewsLoading ? (
          <div className="space-y-4 pt-2">
            {[1, 2, 3, 4].map((i) => (
              <div key={i} className="animate-pulse space-y-2 pt-2">
                <div className="h-4 bg-slate-800 rounded w-3/4" />
                <div className="h-3 bg-slate-800 rounded w-full" />
                <div className="h-3 bg-slate-800 rounded w-1/3" />
              </div>
            ))}
          </div>
        ) : currentArticles.length === 0 ? (
          <div className="py-12 text-center text-slate-500">
            <Radio className="w-8 h-8 mx-auto mb-2 opacity-40 text-slate-400 animate-pulse" />
            <p className="text-xs font-medium">No recent news headlines cached for this category.</p>
            <p className="text-[11px] text-slate-600 mt-1">Click Refresh to crawl public RSS feeds.</p>
          </div>
        ) : (
          currentArticles.map((article) => {
            const pubDate = new Date(article.published_at);
            const formattedDate = isNaN(pubDate.getTime())
              ? article.published_at
              : pubDate.toLocaleDateString('en-US', {
                  month: 'short',
                  day: 'numeric',
                  hour: '2-digit',
                  minute: '2-digit',
                });

            return (
              <article key={article.guid} className="pt-3.5 first:pt-0 group">
                <div className="flex items-center justify-between text-[11px] text-slate-400 mb-1">
                  <div className="flex items-center space-x-2">
                    <span className="font-semibold text-slate-300 bg-slate-800/80 px-1.5 py-0.5 rounded text-[10px] border border-slate-700/40">
                      {article.source}
                    </span>
                    {article.entity_ticker && (
                      <span className="font-mono font-bold text-cyan-400 text-[10px]">
                        ${article.entity_ticker}
                      </span>
                    )}
                  </div>
                  <span className="flex items-center space-x-1 text-slate-500">
                    <Calendar className="w-3 h-3" />
                    <span>{formattedDate}</span>
                  </span>
                </div>

                <a
                  href={article.link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block text-sm font-medium text-slate-100 group-hover:text-cyan-300 transition-colors leading-snug"
                >
                  {article.title}
                  <ExternalLink className="inline-block w-3 h-3 ml-1 opacity-0 group-hover:opacity-100 transition-opacity" />
                </a>

                {article.summary && (
                  <p className="text-xs text-slate-400 mt-1.5 line-clamp-2 leading-relaxed">
                    {article.summary}
                  </p>
                )}
              </article>
            );
          })
        )}
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-slate-800/80 bg-slate-950/60 text-center text-[11px] text-slate-500">
        Extracted via keyless public RSS feeds • 30m TTL cache
      </div>
    </div>
  );
};
