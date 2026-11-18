import pytest
from app.db.database import (
    get_company_by_ticker,
    get_company_competitors,
    get_graph_elements,
    query_companies,
    query_news_articles,
    upsert_companies,
    upsert_competitors,
    upsert_news_articles,
)
from app.db.models import CompanyRecord, CompetitorRecord, NewsArticleRecord


@pytest.mark.asyncio
async def test_upsert_and_query_companies(db_conn):
    """Test company inserts and retrieval by sector."""
    companies = [
        CompanyRecord(
            ticker="AAPL",
            name="Apple Inc.",
            sector="Information Technology",
            industry="Consumer Electronics",
            country_code="USA",
            market_cap_tier="Mega",
        ),
        CompanyRecord(
            ticker="MSFT",
            name="Microsoft Corp",
            sector="Information Technology",
            industry="Systems Software",
            country_code="USA",
            market_cap_tier="Mega",
        ),
        CompanyRecord(
            ticker="XOM",
            name="Exxon Mobil",
            sector="Energy",
            industry="Oil & Gas",
            country_code="USA",
            market_cap_tier="Large",
        ),
    ]

    inserted = await upsert_companies(db_conn, companies)
    assert inserted == 3

    # Query all
    all_companies = await query_companies(db_conn)
    assert len(all_companies) == 3

    # Query by sector
    tech_companies = await query_companies(db_conn, sector="Information Technology")
    assert len(tech_companies) == 2
    assert {c.ticker for c in tech_companies} == {"AAPL", "MSFT"}


@pytest.mark.asyncio
async def test_competitors_and_graph_elements(db_conn):
    """Test competitor relationships and full graph network extraction."""
    companies = [
        CompanyRecord(ticker="NVDA", name="Nvidia", sector="Tech", industry="Semis"),
        CompanyRecord(ticker="AMD", name="AMD", sector="Tech", industry="Semis"),
        CompanyRecord(ticker="INTC", name="Intel", sector="Tech", industry="Semis"),
    ]
    await upsert_companies(db_conn, companies)

    competitors = [
        CompetitorRecord(company_ticker="NVDA", competitor_ticker="AMD", relationship_type="direct_competitor", weight=1.0),
        CompetitorRecord(company_ticker="NVDA", competitor_ticker="INTC", relationship_type="direct_competitor", weight=0.9),
        CompetitorRecord(company_ticker="AMD", competitor_ticker="NVDA", relationship_type="direct_competitor", weight=1.0),
    ]
    await upsert_competitors(db_conn, competitors)

    # Test single company competitor lookup
    nvda_competitors = await get_company_competitors(db_conn, "NVDA")
    assert len(nvda_competitors) == 2
    rival_tickers = [c[0].ticker for c in nvda_competitors]
    assert "AMD" in rival_tickers
    assert "INTC" in rival_tickers

    # Test graph elements
    nodes, edges, sectors = await get_graph_elements(db_conn)
    assert len(nodes) == 3
    assert len(edges) == 3
    assert "Tech" in sectors

    # Verify node degree (competitor count)
    nvda_node = next(n for n in nodes if n["ticker"] == "NVDA")
    assert nvda_node["competitor_count"] == 2


@pytest.mark.asyncio
async def test_news_articles_upsert_and_deduplication(db_conn):
    """Test caching news articles and unique constraint on GUID."""
    articles = [
        NewsArticleRecord(
            guid="guid-101",
            title="Tech Rally Continues",
            link="https://example.com/101",
            published_at="2026-11-18T10:00:00Z",
            source="Reuters",
            entity_ticker="AAPL",
            fetched_at="2026-11-18T10:05:00Z",
        )
    ]
    inserted = await upsert_news_articles(db_conn, articles)
    assert inserted == 1

    # Second insert with same GUID updates existing row
    updated_articles = [
        NewsArticleRecord(
            guid="guid-101",
            title="Tech Rally Continues - Updated",
            link="https://example.com/101",
            published_at="2026-11-18T10:00:00Z",
            source="Reuters",
            entity_ticker="AAPL",
            fetched_at="2026-11-18T10:10:00Z",
        )
    ]
    await upsert_news_articles(db_conn, updated_articles)

    results = await query_news_articles(db_conn, entity_ticker="AAPL")
    assert len(results) == 1
    assert results[0].title == "Tech Rally Continues - Updated"
