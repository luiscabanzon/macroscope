import pytest
import respx
from httpx import Response
import httpx

from app.api.micro_routes import fundamentals_service
from app.config import settings
from app.data.cik_mapping import get_seed_fundamentals
from app.db.database import upsert_companies, upsert_competitors, upsert_observations
from app.db.models import CompanyRecord, CompetitorRecord
from app.main import app
from app.providers.sec_edgar import SecEdgarProvider
from app.services.fundamentals import FundamentalsService


@pytest.mark.asyncio
async def test_sec_edgar_provider_fetch_series(load_fixture):
    """Verify SEC EDGAR XBRL facts parser."""
    fixture_content = load_fixture("sec_edgar_companyfacts.json")
    provider = SecEdgarProvider()

    assert provider.supports("revenue", "AAPL") is True
    assert provider.supports("unknown_metric", "AAPL") is False
    assert provider.supports("revenue", "NONEXISTENT") is False

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get(
            "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"
        ).mock(return_value=Response(200, text=fixture_content))

        obs = await provider.fetch_series("revenue", "AAPL")

        # 3 observations in fixture (1 10-K and 2 10-Q)
        assert len(obs) == 3
        # Annual
        assert obs[0].frequency == "A"
        assert obs[0].value == 383285000000.0
        assert obs[0].source == "SEC EDGAR"
        assert obs[0].unit == "USD"
        # Quarterly
        assert obs[1].frequency == "Q"
        assert obs[1].value == 90753000000.0
        assert obs[2].frequency == "Q"
        assert obs[2].value == 85777000000.0


@pytest.mark.asyncio
async def test_fundamentals_service_ratios(test_db, db_conn):
    """Verify ratio calculations and LTM metric aggregation."""
    # Seed company & fundamental observations
    companies = [
        CompanyRecord(ticker="NVDA", name="NVIDIA Corporation", sector="Information Technology", industry="Semiconductors")
    ]
    await upsert_companies(db_conn, companies)
    await upsert_observations(db_conn, get_seed_fundamentals())

    service = FundamentalsService(db_path=test_db)
    result = await service.get_fundamentals("NVDA")

    assert result is not None
    assert result.ticker == "NVDA"
    assert len(result.annual_series) >= 3
    assert len(result.quarterly_series) >= 3

    # Check margin calculation on latest annual
    latest_annual = result.annual_series[-1]
    assert latest_annual.operating_margin is not None
    assert latest_annual.operating_margin > 50.0  # NVIDIA op margin > 50%
    assert latest_annual.gross_margin is not None
    assert latest_annual.gross_margin > 70.0  # Gross margin > 70%

    # Check summary metrics
    summary = result.summary_metrics
    assert summary.operating_margin is not None
    assert summary.ltm_revenue is not None
    assert summary.ltm_revenue > 0


@pytest.mark.asyncio
async def test_competitor_benchmark_alignment(test_db, db_conn):
    """Verify side-by-side competitor metric alignment."""
    companies = [
        CompanyRecord(ticker="NVDA", name="Nvidia", sector="Tech", industry="Semis"),
        CompanyRecord(ticker="AMD", name="AMD", sector="Tech", industry="Semis"),
    ]
    await upsert_companies(db_conn, companies)

    competitors = [
        CompetitorRecord(company_ticker="NVDA", competitor_ticker="AMD", relationship_type="direct_competitor", weight=1.0)
    ]
    await upsert_competitors(db_conn, competitors)
    await upsert_observations(db_conn, get_seed_fundamentals())

    service = FundamentalsService(db_path=test_db)
    benchmark = await service.get_competitor_benchmark("NVDA", metric="operating_margin")

    assert benchmark is not None
    assert benchmark.target_ticker == "NVDA"
    assert "AMD" in benchmark.competitors
    assert len(benchmark.data) > 0
    # Check that points contain both NVDA and AMD where dates overlap
    has_overlap = any("NVDA" in p.values and "AMD" in p.values for p in benchmark.data)
    assert has_overlap is True


@pytest.mark.asyncio
async def test_micro_api_endpoints(test_db, db_conn, monkeypatch):
    """Verify /api/v1/companies/{ticker}/fundamentals and /benchmark endpoints."""
    monkeypatch.setattr(settings, "db_path", test_db)
    fundamentals_service.db_path = test_db
    fundamentals_service.cache_manager.db_path = test_db

    companies = [
        CompanyRecord(ticker="AAPL", name="Apple Inc.", sector="Tech", industry="Hardware"),
        CompanyRecord(ticker="MSFT", name="Microsoft Corp", sector="Tech", industry="Software"),
    ]
    await upsert_companies(db_conn, companies)
    await upsert_observations(db_conn, get_seed_fundamentals())

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Fundamentals endpoint
        res = await client.get("/api/v1/companies/AAPL/fundamentals")
        assert res.status_code == 200
        data = res.json()
        assert data["ticker"] == "AAPL"
        assert "summary_metrics" in data
        assert "annual_series" in data

        # 2. Benchmark endpoint
        res_bench = await client.get("/api/v1/companies/AAPL/benchmark?metric=operating_margin")
        assert res_bench.status_code == 200
        bench_data = res_bench.json()
        assert bench_data["target_ticker"] == "AAPL"
        assert bench_data["metric"] == "operating_margin"

        # 3. 404 for unknown company
        res_404 = await client.get("/api/v1/companies/DOESNOTEXIST/fundamentals")
        assert res_404.status_code == 404
