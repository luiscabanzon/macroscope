import pytest
from app.db.database import upsert_companies, upsert_competitors
from app.db.models import CompanyRecord, CompetitorRecord, NewsArticleRecord
from app.services.company_graph import CompanyGraphService


class MockNewsProvider:
    """Mock RSS news provider for offline service testing."""

    async def fetch_company_news(self, ticker: str, limit: int = 10) -> list[NewsArticleRecord]:
        return [
            NewsArticleRecord(
                guid=f"mock-{ticker}-1",
                title=f"{ticker} Reports Earnings",
                link=f"https://example.com/{ticker}",
                published_at="2026-11-18T10:00:00Z",
                source="Mock Source",
                entity_ticker=ticker,
                fetched_at="2026-11-18T10:05:00Z",
            )
        ]

    async def fetch_sector_news(self, sector: str, limit: int = 10) -> list[NewsArticleRecord]:
        return [
            NewsArticleRecord(
                guid=f"mock-sector-{sector}",
                title=f"{sector} Market Overview",
                link="https://example.com/sector",
                published_at="2026-11-18T09:00:00Z",
                source="Mock Source",
                sector=sector,
                fetched_at="2026-11-18T10:05:00Z",
            )
        ]


@pytest.mark.asyncio
async def test_contextual_news_partitioning(test_db, db_conn):
    """Test 3-way news partitioning into company, competitor, and sector buckets."""
    # Seed companies & competitor relationship
    companies = [
        CompanyRecord(ticker="AAPL", name="Apple Inc.", sector="Technology", industry="Hardware"),
        CompanyRecord(ticker="MSFT", name="Microsoft Corp", sector="Technology", industry="Software"),
    ]
    await upsert_companies(db_conn, companies)

    competitors = [
        CompetitorRecord(company_ticker="AAPL", competitor_ticker="MSFT", relationship_type="direct_competitor", weight=1.0)
    ]
    await upsert_competitors(db_conn, competitors)

    service = CompanyGraphService(news_provider=MockNewsProvider(), db_path=test_db)

    # First fetch: triggers news provider and partitions
    result = await service.get_contextual_news("AAPL")
    assert result["company"] is not None
    assert result["company"].ticker == "AAPL"
    assert result["competitor_tickers"] == ["MSFT"]

    # Verify company news
    company_news = result["company_news"]
    assert len(company_news) >= 1
    assert any(a.entity_ticker == "AAPL" for a in company_news)

    # Verify competitor news
    competitor_news = result["competitor_news"]
    assert len(competitor_news) >= 1
    assert any(a.entity_ticker == "MSFT" for a in competitor_news)

    # Verify sector news
    sector_news = result["sector_news"]
    assert len(sector_news) >= 1
    assert any(a.sector == "Technology" for a in sector_news)
