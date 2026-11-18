import pytest
import httpx
from app.config import settings
from app.db.database import upsert_observations
from app.db.models import ObservationRecord
from app.main import app
from app.api.routes import cache_manager


@pytest.fixture(autouse=True)
def point_cache_manager_to_test_db(test_db, monkeypatch):
    """Ensure route handlers use the temporary test database."""
    monkeypatch.setattr(settings, "db_path", test_db)
    original_db = cache_manager.db_path
    cache_manager.db_path = test_db
    yield
    cache_manager.db_path = original_db


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Verify GET /api/v1/health."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        payload = response.json()
        assert payload["status"] == "healthy"
        assert "cached_observations" in payload


@pytest.mark.asyncio
async def test_get_countries_endpoint():
    """Verify GET /api/v1/countries returns supported economy metadata."""
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/countries")
        assert response.status_code == 200
        countries = response.json()
        assert len(countries) >= 10
        codes = [c["code"] for c in countries]
        assert "USA" in codes
        assert "GBR" in codes
        assert "DEU" in codes


@pytest.mark.asyncio
async def test_dashboard_endpoint_with_seeded_data(db_conn):
    """Verify GET /api/v1/dashboard/{country_code} returns correct schema and KPI ribbons."""
    # Seed sample observations into test DB
    obs = [
        ObservationRecord(
            country_code="USA",
            indicator_slug="gdp_growth",
            period_date="2022-01-01",
            frequency="A",
            value=1.9,
            unit="%",
            source="World Bank",
        ),
        ObservationRecord(
            country_code="USA",
            indicator_slug="gdp_growth",
            period_date="2023-01-01",
            frequency="A",
            value=2.5,
            unit="%",
            source="World Bank",
        ),
        ObservationRecord(
            country_code="USA",
            indicator_slug="oil_brent",
            period_date="2024-01-02",
            frequency="D",
            value=77.0,
            unit="USD/bbl",
            source="FRED",
        ),
    ]
    await upsert_observations(db_conn, obs)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/dashboard/USA")
        assert response.status_code == 200
        data = response.json()
        assert data["country_code"] == "USA"
        assert data["country_name"] == "United States"

        # Check KPI snapshots
        kpi_map = {k["indicator_slug"]: k for k in data["kpis"]}
        assert "gdp_growth" in kpi_map
        gdp_kpi = kpi_map["gdp_growth"]
        assert gdp_kpi["latest_value"] == 2.5
        assert gdp_kpi["previous_value"] == 1.9
        assert gdp_kpi["delta_yoy"] == 0.6  # 2.5 - 1.9

        # Check Series dictionary
        assert "gdp_growth" in data["series"]
        gdp_series = data["series"]["gdp_growth"]
        assert len(gdp_series["data"]) == 2


@pytest.mark.asyncio
async def test_compare_endpoint(db_conn):
    """Verify GET /api/v1/compare aligns dates across multiple countries."""
    obs = [
        ObservationRecord(
            country_code="USA",
            indicator_slug="inflation_cpi",
            period_date="2023-01-01",
            frequency="A",
            value=4.1,
            unit="%",
            source="World Bank",
        ),
        ObservationRecord(
            country_code="DEU",
            indicator_slug="inflation_cpi",
            period_date="2023-01-01",
            frequency="A",
            value=5.9,
            unit="%",
            source="World Bank",
        ),
    ]
    await upsert_observations(db_conn, obs)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/compare?countries=USA,DEU&indicator=inflation_cpi")
        assert response.status_code == 200
        data = response.json()
        assert data["indicator_slug"] == "inflation_cpi"
        assert set(data["countries"]) == {"USA", "DEU"}
        assert len(data["data"]) == 1
        assert data["data"][0]["period_date"] == "2023-01-01"
        assert data["data"][0]["values"]["USA"] == 4.1
        assert data["data"][0]["values"]["DEU"] == 5.9


@pytest.mark.asyncio
async def test_refresh_blocked_in_read_only_mode(monkeypatch):
    """Verify POST /api/v1/refresh/{country_code} returns 403 when READ_ONLY_CACHE is True."""
    monkeypatch.setattr(settings, "read_only_cache", True)

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/api/v1/refresh/USA")
        assert response.status_code == 403
        assert "READ_ONLY_CACHE" in response.json()["detail"]
