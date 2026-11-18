from pydantic import BaseModel, Field


class CountryInfo(BaseModel):
    """Country metadata and indicator support mapping."""
    code: str = Field(description="ISO-3 Country Code (e.g. USA, GBR, DEU)")
    name: str = Field(description="Full country name")
    region: str = Field(description="Geographic or economic region")
    indicators: list[str] = Field(description="List of supported indicator slugs")


class KpiSnapshot(BaseModel):
    """High-level KPI card metrics with directional changes."""
    indicator_slug: str
    indicator_name: str
    latest_value: float
    period_date: str
    previous_value: float | None = None
    delta_yoy: float | None = None
    delta_mom: float | None = None
    unit: str
    source: str
    is_stale: bool = False


class ObservationPoint(BaseModel):
    """Single date-value pair in a time series."""
    period_date: str
    value: float


class IndicatorSeriesResponse(BaseModel):
    """Historical time-series array with metadata."""
    indicator_slug: str
    indicator_name: str
    country_code: str
    unit: str
    frequency: str
    source: str
    is_stale: bool
    last_updated: str | None = None
    data: list[ObservationPoint]


class DashboardResponse(BaseModel):
    """Full country dashboard payload."""
    country_code: str
    country_name: str
    last_updated: str | None = None
    is_stale: bool = False
    kpis: list[KpiSnapshot]
    series: dict[str, IndicatorSeriesResponse]


class ComparisonDataPoint(BaseModel):
    """Cross-country aligned observation point for comparative charting."""
    period_date: str
    values: dict[str, float] = Field(description="Map of country_code to numeric value")


class ComparisonResponse(BaseModel):
    """Multi-country aligned time-series for comparison charts."""
    indicator_slug: str
    indicator_name: str
    unit: str
    countries: list[str]
    data: list[ComparisonDataPoint]


class RefreshResponse(BaseModel):
    """Response returned after triggering a cache refresh."""
    country_code: str
    status: str
    refreshed_indicators: list[str]
