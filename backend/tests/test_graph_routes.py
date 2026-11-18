import pytest
import httpx
from app.api.graph_routes import graph_service
from app.config import settings
from app.db.database import upsert_companies, upsert_competitors
from app.db.models import CompanyRecord, CompetitorRecord
from app.main import app
from tests.test_company_graph_service import MockNewsProvider


@pytest.fixture(autouse=True)
def point_graph_service_to_test_db(test_db, monkeypatch):
    """Point graph service to the isolated test database and inject mock news provider."""
    original_db = graph_service.db_path
    original_provider = graph_service.news_provider

    monkeypatch.setattr(settings, "db_path", test_db)
    graph_service.db_path = test_db
    graph_service.news_provider = MockNewsProvider()

    yield

    graph_service.db_path = original_db
    graph_service.news_provider = original_provider


@pytest.mark.asyncio
async def test_get_graph_endpoint(db_conn):
    """Verify GET /api/v1/graph returns nodes, edges, and sectors."""
    companies = [
        CompanyRecord(ticker="TSLA", name="Tesla", sector="Consumer Discretionary", industry="Automotive"),
        CompanyRecord(ticker="F", name="Ford", sector="Consumer Discretionary", industry="Automotive"),
    ]
    await upsert_companies(db_conn, companies)

    competitors = [
        CompetitorRecord(company_ticker="TSLA", competitor_ticker="F", relationship_type="direct_competitor", weight=1.0)
    ]
    await upsert_competitors(db_conn, competitors)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/graph")
        assert response.status_code == 200
        data = response.json()

        assert "nodes" in data
        assert "edges" in data
        assert "sectors" in data
        assert len(data["nodes"]) == 2
        assert len(data["edges"]) == 1
        assert data["edges"][0]["source"] == "TSLA"
        assert data["edges"][0]["target"] == "F"


@pytest.mark.asyncio
async def test_get_company_profile_endpoint(db_conn):
    """Verify GET /api/v1/companies/{ticker}."""
    companies = [
        CompanyRecord(
            ticker="NVDA",
            name="Nvidia",
            sector="Technology",
            industry="Semiconductors",
            market_cap_tier="Mega",
        ),
        CompanyRecord(
            ticker="AMD",
            name="Advanced Micro Devices",
            sector="Technology",
            industry="Semiconductors",
        ),
    ]
    await upsert_companies(db_conn, companies)

    competitors = [
        CompetitorRecord(company_ticker="NVDA", competitor_ticker="AMD", relationship_type="direct_competitor", weight=1.0)
    ]
    await upsert_competitors(db_conn, competitors)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # Existing company
        res = await client.get("/api/v1/companies/NVDA")
        assert res.status_code == 200
        profile = res.json()
        assert profile["ticker"] == "NVDA"
        assert len(profile["competitors"]) == 1
        assert profile["competitors"][0]["ticker"] == "AMD"

        # Non-existing company
        res_404 = await client.get("/api/v1/companies/DOESNOTEXIST")
        assert res_404.status_code == 404


@pytest.mark.asyncio
async def test_get_company_news_endpoint(db_conn):
    """Verify GET /api/v1/companies/{ticker}/news partitions company, competitor, and sector news."""
    companies = [
        CompanyRecord(ticker="AAPL", name="Apple Inc.", sector="Technology", industry="Hardware"),
        CompanyRecord(ticker="MSFT", name="Microsoft Corp", sector="Technology", industry="Software"),
    ]
    await upsert_companies(db_conn, companies)

    competitors = [
        CompetitorRecord(company_ticker="AAPL", competitor_ticker="MSFT", relationship_type="direct_competitor", weight=1.0)
    ]
    await upsert_competitors(db_conn, competitors)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/companies/AAPL/news")
        assert res.status_code == 200
        news_payload = res.json()

        assert news_payload["ticker"] == "AAPL"
        assert news_payload["competitor_tickers"] == ["MSFT"]
        assert len(news_payload["company_news"]) >= 1
        assert len(news_payload["competitor_news"]) >= 1
        assert len(news_payload["sector_news"]) >= 1
