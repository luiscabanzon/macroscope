from pydantic import BaseModel, Field


class SummaryMetrics(BaseModel):
    """Latest LTM financial health and profitability metrics."""
    ltm_revenue: float | None = Field(None, description="Last Twelve Months Total Revenue (USD)")
    revenue_growth_yoy: float | None = Field(None, description="YoY Revenue Growth Rate (%)")
    operating_margin: float | None = Field(None, description="Operating Margin (%)")
    net_margin: float | None = Field(None, description="Net Profit Margin (%)")
    gross_margin: float | None = Field(None, description="Gross Margin (%)")
    rnd_intensity: float | None = Field(None, description="R&D Expense as % of Revenue")


class FinancialPeriodPoint(BaseModel):
    """Historical annual or quarterly fundamental metrics with calculated margins."""
    period_date: str
    frequency: str  # 'A' (10-K) or 'Q' (10-Q)
    revenue: float | None = None
    net_income: float | None = None
    operating_income: float | None = None
    gross_profit: float | None = None
    rnd_expense: float | None = None
    gross_margin: float | None = None
    operating_margin: float | None = None
    net_margin: float | None = None
    rnd_intensity: float | None = None
    revenue_growth_yoy: float | None = None


class CompanyFundamentalsResponse(BaseModel):
    """Complete company fundamental financial statements and ratios."""
    ticker: str
    company_name: str
    sector: str
    industry: str
    cik: str | None = None
    summary_metrics: SummaryMetrics
    annual_series: list[FinancialPeriodPoint]
    quarterly_series: list[FinancialPeriodPoint]


class BenchmarkPoint(BaseModel):
    """Aligned date point comparing metric values across peer companies."""
    period_date: str
    values: dict[str, float] = Field(description="Map of ticker to metric value")


class CompetitorBenchmarkResponse(BaseModel):
    """Peer competitor comparison series across a selected metric."""
    target_ticker: str
    metric: str
    metric_name: str
    unit: str
    competitors: list[str]
    data: list[BenchmarkPoint]
