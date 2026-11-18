export interface GraphNode {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  country_code: string;
  market_cap_tier: string | null;
  competitor_count: number;
  description: string | null;
  // D3 simulation coordinates
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
}

export interface GraphEdge {
  source: string | GraphNode;
  target: string | GraphNode;
  relationship_type: string;
  weight: number;
}

export interface GraphResponse {
  nodes: GraphNode[];
  edges: GraphEdge[];
  sectors: string[];
}

export interface CompetitorItem {
  ticker: string;
  name: string;
  industry: string;
  relationship_type: string;
  weight: number;
}

export interface CompanyDetailResponse {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  country_code: string;
  market_cap_tier: string | null;
  description: string | null;
  competitors: CompetitorItem[];
}

export interface NewsArticleItem {
  id: number | null;
  guid: string;
  title: string;
  link: string;
  published_at: string;
  source: string;
  summary: string | null;
  entity_ticker: string | null;
  sector: string | null;
}

export interface CompanyNewsResponse {
  ticker: string;
  company_name: string;
  sector: string;
  competitor_tickers: string[];
  company_news: NewsArticleItem[];
  competitor_news: NewsArticleItem[];
  sector_news: NewsArticleItem[];
}
