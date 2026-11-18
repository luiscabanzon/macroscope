from pydantic import BaseModel, Field


class ObservationRecord(BaseModel):
    """Database record representation of a single time-series observation."""
    id: int | None = None
    country_code: str = Field(description="ISO-3 country code or entity ticker (e.g. USA, WLD, AAPL)")
    indicator_slug: str = Field(description="Unified indicator identifier (e.g. gdp_growth, oil_brent)")
    period_date: str = Field(description="ISO-8601 period date string: YYYY-MM-DD")
    frequency: str = Field(description="Frequency code: 'A', 'Q', 'M', 'D'")
    value: float = Field(description="Numeric value of the observation")
    unit: str = Field(description="Unit label (e.g. %, USD/bbl, Millions)")
    source: str = Field(description="Originating source name (e.g. World Bank, FRED)")


class FetchLogRecord(BaseModel):
    """Database record tracking upstream fetch timestamps and status."""
    country_code: str
    indicator_slug: str
    last_fetched_at: str  # ISO-8601 timestamp
    status: str           # 'SUCCESS', 'ERROR', 'EMPTY'
    error_message: str | None = None


class CompanyRecord(BaseModel):
    """Database record representing a public company."""
    ticker: str = Field(description="Stock ticker symbol (e.g. AAPL, MSFT, NVDA)")
    name: str = Field(description="Full legal or commercial company name")
    sector: str = Field(description="GICS sector (e.g. Information Technology, Energy)")
    industry: str = Field(description="GICS industry group / sub-industry")
    country_code: str = Field(default="USA", description="Headquarters country code")
    market_cap_tier: str | None = Field(default="Large", description="Mega, Large, Mid, Small")
    description: str | None = None


class CompetitorRecord(BaseModel):
    """Database record representing a competitor relationship between two companies."""
    company_ticker: str
    competitor_ticker: str
    relationship_type: str = Field(default="direct_competitor", description="direct_competitor, sector_peer")
    weight: float = Field(default=1.0, description="Relationship affinity or competition weight")


class NewsArticleRecord(BaseModel):
    """Database record representing a cached public RSS news article."""
    id: int | None = None
    guid: str = Field(description="Unique article identifier (RSS GUID or link hash)")
    title: str
    link: str
    published_at: str  # ISO-8601 string
    source: str        # e.g. Yahoo Finance, Google News, Reuters
    summary: str | None = None
    entity_ticker: str | None = None  # Associated company ticker
    sector: str | None = None         # Associated sector
    fetched_at: str                   # ISO-8601 fetch timestamp
