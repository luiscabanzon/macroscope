import pytest
import respx
from httpx import Response
from app.config import settings
from app.db.database import get_connection
from app.services.seed import seed_database


@pytest.mark.asyncio
async def test_seed_dry_run(test_db, monkeypatch):
    """Verify seed execution with dry_run=True."""
    monkeypatch.setattr(settings, "db_path", test_db)

    summary = await seed_database(
        countries=["USA", "DEU"],
        indicators=["gdp_growth"],
        dry_run=True,
        delay_seconds=0.0,
    )

    assert "USA_gdp_growth" in summary
    assert "DEU_gdp_growth" in summary
    assert summary["USA_gdp_growth"] == 0


@pytest.mark.asyncio
async def test_seed_with_mocked_provider(test_db, load_fixture, monkeypatch):
    """Verify seed execution persists observations into the database."""
    monkeypatch.setattr(settings, "db_path", test_db)
    fixture_content = load_fixture("world_bank_gdp.json")

    with respx.mock(assert_all_called=False) as respx_mock:
        respx_mock.get(
            "https://api.worldbank.org/v2/country/usa/indicator/NY.GDP.MKTP.KD.ZG"
        ).mock(return_value=Response(200, text=fixture_content))

        summary = await seed_database(
            countries=["USA"],
            indicators=["gdp_growth"],
            dry_run=False,
            delay_seconds=0.0,
        )

        assert summary["USA_gdp_growth"] == 3

        async with get_connection(test_db) as conn:
            async with conn.execute("SELECT count(*) FROM observations WHERE country_code = 'USA'") as cursor:
                row = await cursor.fetchone()
                assert row is not None
                assert row[0] == 3
