export type NetworkType = 'all' | 'competition' | 'supply_chain';

export interface GraphNode {
  ticker: string;
  name: string;
  sector: string;
  industry: string;
  country_code: string;
  market_cap_tier: string | null;
  competitor_count: number;
  supplier_count?: number;
  customer_count?: number;
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
  is_directed?: boolean;
  relationship_category?: 'competition' | 'supply_chain';
  product_category?: string | null;
  tier_or_importance?: string | null;
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

export interface SupplyChainItem {
  ticker: string;
  name: string;
  industry: string;
  product_category: string;
  tier_or_importance: string;
  weight: number;
  role: 'supplier' | 'customer';
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
  suppliers: SupplyChainItem[];
  customers: SupplyChainItem[];
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
  supply_chain_tickers: string[];
  company_news: NewsArticleItem[];
  competitor_news: NewsArticleItem[];
  sector_news: NewsArticleItem[];
  supply_chain_news: NewsArticleItem[];
}
