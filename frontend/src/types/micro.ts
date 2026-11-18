export interface SummaryMetrics {
  ltm_revenue: number | null;
  revenue_growth_yoy: number | null;
  operating_margin: number | null;
  net_margin: number | null;
  gross_margin: number | null;
  rnd_intensity: number | null;
}

export interface FinancialPeriodPoint {
  period_date: string;
  frequency: 'A' | 'Q';
  revenue: number | null;
  net_income: number | null;
  operating_income: number | null;
  gross_profit: number | null;
  rnd_expense: number | null;
  gross_margin: number | null;
  operating_margin: number | null;
  net_margin: number | null;
  rnd_intensity: number | null;
  revenue_growth_yoy: number | null;
}

export interface CompanyFundamentalsResponse {
  ticker: string;
  company_name: string;
  sector: string;
  industry: string;
  cik: string | null;
  summary_metrics: SummaryMetrics;
  annual_series: FinancialPeriodPoint[];
  quarterly_series: FinancialPeriodPoint[];
}

export interface BenchmarkPoint {
  period_date: string;
  values: Record<string, number>;
}

export interface CompetitorBenchmarkResponse {
  target_ticker: string;
  metric: string;
  metric_name: string;
  unit: string;
  competitors: string[];
  data: BenchmarkPoint[];
}
