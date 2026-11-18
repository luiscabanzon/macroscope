from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.graph import (
    CompanyDetailResponse,
    CompanyNewsResponse,
    CompetitorItem,
    GraphEdge,
    GraphNode,
    GraphResponse,
    NewsArticleItem,
)
from app.services.company_graph import CompanyGraphService

router = APIRouter(prefix="", tags=["Company Graph & News"])
graph_service = CompanyGraphService()


@router.get("/graph", response_model=GraphResponse)
async def get_company_graph(
    sector: str | None = Query(None, description="Optional sector filter e.g. 'Information Technology'"),
) -> GraphResponse:
    """Retrieve company graph nodes and competitor edges for network visualization."""
    nodes_raw, edges_raw, sectors = await graph_service.get_graph(sector=sector)

    nodes = [GraphNode(**n) for n in nodes_raw]
    edges = [GraphEdge(**e) for e in edges_raw]

    return GraphResponse(
        nodes=nodes,
        edges=edges,
        sectors=sectors,
    )


@router.get("/companies/{ticker}", response_model=CompanyDetailResponse)
async def get_company_profile(ticker: str) -> CompanyDetailResponse:
    """Retrieve company details and direct competitor breakdown."""
    company, competitor_tuples = await graph_service.get_company_profile(ticker)
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker.upper()}' not found in database",
        )

    competitors = [
        CompetitorItem(
            ticker=comp.ticker,
            name=comp.name,
            industry=comp.industry,
            relationship_type=rel_type,
            weight=weight,
        )
        for comp, rel_type, weight in competitor_tuples
    ]

    return CompanyDetailResponse(
        ticker=company.ticker,
        name=company.name,
        sector=company.sector,
        industry=company.industry,
        country_code=company.country_code,
        market_cap_tier=company.market_cap_tier,
        description=company.description,
        competitors=competitors,
    )


@router.get("/companies/{ticker}/news", response_model=CompanyNewsResponse)
async def get_company_news(
    ticker: str,
    force_refresh: bool = Query(False, description="Bypass cache and fetch fresh RSS feeds"),
) -> CompanyNewsResponse:
    """Retrieve contextual news segmented into Company, Competitor, and Sector headlines."""
    news_data = await graph_service.get_contextual_news(ticker, force_refresh=force_refresh)
    company = news_data["company"]
    if not company:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker.upper()}' not found in database",
        )

    def to_item(a) -> NewsArticleItem:
        return NewsArticleItem(
            id=a.id,
            guid=a.guid,
            title=a.title,
            link=a.link,
            published_at=a.published_at,
            source=a.source,
            summary=a.summary,
            entity_ticker=a.entity_ticker,
            sector=a.sector,
        )

    return CompanyNewsResponse(
        ticker=company.ticker,
        company_name=company.name,
        sector=company.sector,
        competitor_tickers=news_data["competitor_tickers"],
        company_news=[to_item(a) for a in news_data["company_news"]],
        competitor_news=[to_item(a) for a in news_data["competitor_news"]],
        sector_news=[to_item(a) for a in news_data["sector_news"]],
    )
