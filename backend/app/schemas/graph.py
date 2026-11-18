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
    supplier_count: int = Field(default=0, description="Number of upstream suppliers")
    customer_count: int = Field(default=0, description="Number of downstream customers")
    description: str | None = None


class GraphEdge(BaseModel):
    """Network edge representing a rivalry, peer, or supply chain relationship."""
    source: str = Field(description="Origin company ticker")
    target: str = Field(description="Target company ticker")
    relationship_type: str = Field(default="direct_competitor")
    weight: float = Field(default=1.0)
    is_directed: bool = Field(default=False, description="True for directed supply chain edges")
    relationship_category: str = Field(default="competition", description="competition or supply_chain")
    product_category: str | None = Field(default=None, description="Supplied component or service")
    tier_or_importance: str | None = Field(default=None, description="critical, major, standard")


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


class SupplyChainItem(BaseModel):
    """Customer or supplier relationship details."""
    ticker: str
    name: str
    industry: str
    product_category: str
    tier_or_importance: str
    weight: float
    role: str  # 'supplier' (upstream) or 'customer' (downstream)


class CompanyDetailResponse(BaseModel):
    """Company profile with competitor and supply chain breakdown."""
    ticker: str
    name: str
    sector: str
    industry: str
    country_code: str
    market_cap_tier: str | None = None
    description: str | None = None
    competitors: list[CompetitorItem]
    suppliers: list[SupplyChainItem] = Field(default_factory=list, description="Upstream component/service providers")
    customers: list[SupplyChainItem] = Field(default_factory=list, description="Downstream enterprise customers")


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
    """Contextual 4-way partitioned news stream."""
    ticker: str
    company_name: str
    sector: str
    competitor_tickers: list[str]
    supply_chain_tickers: list[str] = Field(default_factory=list, description="Connected suppliers and customers")
    company_news: list[NewsArticleItem]
    competitor_news: list[NewsArticleItem]
    sector_news: list[NewsArticleItem]
    supply_chain_news: list[NewsArticleItem] = Field(default_factory=list, description="Headlines for suppliers and customers")
