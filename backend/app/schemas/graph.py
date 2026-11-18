from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Network node representing a public company."""
    ticker: str = Field(description="Ticker symbol")
    name: str = Field(description="Company name")
    sector: str = Field(description="GICS sector")
    industry: str = Field(description="Industry group")
    country_code: str = Field(default="USA")
    market_cap_tier: str | None = Field(default="Large")
    competitor_count: int = Field(default=0, description="Degree of competitor links")
    description: str | None = None


class GraphEdge(BaseModel):
    """Network edge representing a rivalry or peer relationship."""
    source: str = Field(description="Origin company ticker")
    target: str = Field(description="Target competitor ticker")
    relationship_type: str = Field(default="direct_competitor")
    weight: float = Field(default=1.0)


class GraphResponse(BaseModel):
    """Complete graph visualization payload."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
    sectors: list[str]


class CompetitorItem(BaseModel):
    """Competitor information linked to a company."""
    ticker: str
    name: str
    industry: str
    relationship_type: str
    weight: float


class CompanyDetailResponse(BaseModel):
    """Company profile with direct competitor breakdown."""
    ticker: str
    name: str
    sector: str
    industry: str
    country_code: str
    market_cap_tier: str | None = None
    description: str | None = None
    competitors: list[CompetitorItem]


class NewsArticleItem(BaseModel):
    """Clean news article representation."""
    id: int | None = None
    guid: str
    title: str
    link: str
    published_at: str
    source: str
    summary: str | None = None
    entity_ticker: str | None = None
    sector: str | None = None


class CompanyNewsResponse(BaseModel):
    """Contextual 3-way partitioned news stream."""
    ticker: str
    company_name: str
    sector: str
    competitor_tickers: list[str]
    company_news: list[NewsArticleItem]
    competitor_news: list[NewsArticleItem]
    sector_news: list[NewsArticleItem]
