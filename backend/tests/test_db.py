import pytest
from app.db.database import (
    get_fetch_log,
    query_multi_country_observations,
    query_observations,
    set_fetch_log,
    upsert_observations,
)
from app.db.models import ObservationRecord


@pytest.mark.asyncio
async def test_upsert_and_query_observations(db_conn):
    """Verify inserting observations and retrieving them in order."""
    observations = [
        ObservationRecord(
            country_code="USA",
            indicator_slug="gdp_growth",
            period_date="2021-01-01",
            frequency="A",
            value=5.9,
            unit="%",
            source="World Bank",
        ),
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
    ]

    inserted = await upsert_observations(db_conn, observations)
    assert inserted == 3

    # Query all
    records = await query_observations(db_conn, "USA", "gdp_growth")
    assert len(records) == 3
    assert [r.period_date for r in records] == ["2021-01-01", "2022-01-01", "2023-01-01"]
    assert records[0].value == 5.9

    # Query with start_date filter
    filtered = await query_observations(db_conn, "USA", "gdp_growth", start_date="2022-01-01")
    assert len(filtered) == 2
    assert [r.period_date for r in filtered] == ["2022-01-01", "2023-01-01"]


@pytest.mark.asyncio
async def test_upsert_conflict_replaces_value(db_conn):
    """Verify unique constraint update (idempotence) on compound key."""
    initial = [
        ObservationRecord(
            country_code="USA",
            indicator_slug="oil_brent",
            period_date="2024-01-02",
            frequency="D",
            value=75.0,
            unit="USD/bbl",
            source="FRED",
        )
    ]
    await upsert_observations(db_conn, initial)

    records = await query_observations(db_conn, "USA", "oil_brent")
    assert len(records) == 1
    assert records[0].value == 75.0

    # Upsert updated revised print
    revised = [
        ObservationRecord(
            country_code="USA",
            indicator_slug="oil_brent",
            period_date="2024-01-02",
            frequency="D",
            value=77.04,
            unit="USD/bbl",
            source="FRED",
        )
    ]
    await upsert_observations(db_conn, revised)

    records = await query_observations(db_conn, "USA", "oil_brent")
    assert len(records) == 1
    assert records[0].value == 77.04


@pytest.mark.asyncio
async def test_multi_country_query(db_conn):
    """Verify multi-country side-by-side time series extraction."""
    obs = [
        ObservationRecord(
            country_code="USA",
            indicator_slug="inflation_cpi",
            period_date="2022-01-01",
            frequency="A",
            value=8.0,
            unit="%",
            source="World Bank",
        ),
        ObservationRecord(
            country_code="DEU",
            indicator_slug="inflation_cpi",
            period_date="2022-01-01",
            frequency="A",
            value=6.9,
            unit="%",
            source="World Bank",
        ),
        ObservationRecord(
            country_code="GBR",
            indicator_slug="inflation_cpi",
            period_date="2022-01-01",
            frequency="A",
            value=7.9,
            unit="%",
            source="World Bank",
        ),
    ]
    await upsert_observations(db_conn, obs)

    results = await query_multi_country_observations(db_conn, ["USA", "DEU"], "inflation_cpi")
    assert len(results) == 2
    codes = {r.country_code for r in results}
    assert codes == {"USA", "DEU"}


@pytest.mark.asyncio
async def test_fetch_log_operations(db_conn):
    """Verify fetch log insert, retrieval, and update on conflict."""
    # Check non-existent
    log = await get_fetch_log(db_conn, "USA", "gdp_growth")
    assert log is None

    # Insert SUCCESS
    await set_fetch_log(db_conn, "USA", "gdp_growth", status="SUCCESS")
    log = await get_fetch_log(db_conn, "USA", "gdp_growth")
    assert log is not None
    assert log.status == "SUCCESS"
    assert log.error_message is None

    # Update with ERROR
    await set_fetch_log(
        db_conn,
        "USA",
        "gdp_growth",
        status="ERROR",
        error_message="Upstream timeout",
    )
    log = await get_fetch_log(db_conn, "USA", "gdp_growth")
    assert log is not None
    assert log.status == "ERROR"
    assert log.error_message == "Upstream timeout"
