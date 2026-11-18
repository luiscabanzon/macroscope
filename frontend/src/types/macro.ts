export interface CountryInfo {
  code: string;
  name: string;
  region: string;
  indicators: string[];
}

export interface KpiSnapshot {
  indicator_slug: string;
  indicator_name: string;
  latest_value: number;
  period_date: string;
  previous_value: number | null;
  delta_yoy: number | null;
  delta_mom: number | null;
  unit: string;
  source: string;
  is_stale: boolean;
}

export interface ObservationPoint {
  period_date: string;
  value: number;
}

export interface IndicatorSeriesResponse {
  indicator_slug: string;
  indicator_name: string;
  country_code: string;
  unit: string;
  frequency: string;
  source: string;
  is_stale: boolean;
  last_updated: string | null;
  data: ObservationPoint[];
}

export interface DashboardResponse {
  country_code: string;
  country_name: string;
  last_updated: string | null;
  is_stale: boolean;
  kpis: KpiSnapshot[];
  series: Record<string, IndicatorSeriesResponse>;
}

export interface ComparisonDataPoint {
  period_date: string;
  values: Record<string, number>;
}

export interface ComparisonResponse {
  indicator_slug: string;
  indicator_name: string;
  unit: string;
  countries: string[];
  data: ComparisonDataPoint[];
}

export interface RefreshResponse {
  country_code: string;
  status: string;
  refreshed_indicators: string[];
}
