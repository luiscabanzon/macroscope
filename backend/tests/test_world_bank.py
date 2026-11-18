import json
import pytest
import respx
from httpx import Response

from app.providers.world_bank import WorldBankProvider


@pytest.mark.asyncio
async def test_world_bank_fetch_series_success(load_fixture):
    """Test successful World Bank series extraction and normalization."""
    fixture_content = load_fixture("world_bank_gdp.json")
    provider = WorldBankProvider()

    assert provider.supports("gdp_growth", "USA") is True
    assert provider.supports("unknown_indicator", "USA") is False
    assert provider.supports("gdp_growth", "INVALID_CODE") is False

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get(
            "https://api.worldbank.org/v2/country/usa/indicator/NY.GDP.MKTP.KD.ZG"
        ).mock(return_value=Response(200, text=fixture_content))

        obs = await provider.fetch_series("gdp_growth", "USA")

        # 4 records in fixture, but one has value=null -> only 3 valid observations expected
        assert len(obs) == 3
        # Verified chronological sort
        assert obs[0].period_date == "2021-01-01"
        assert obs[0].value == 5.945
        assert obs[0].unit == "%"
        assert obs[0].frequency == "A"
        assert obs[0].source == "World Bank"
        assert obs[0].country_code == "USA"

        assert obs[1].period_date == "2022-01-01"
        assert obs[1].value == 1.942

        assert obs[2].period_date == "2023-01-01"
        assert obs[2].value == 2.536


@pytest.mark.asyncio
async def test_world_bank_empty_or_invalid_response(load_fixture):
    """Test handling of World Bank API error payload."""
    fixture_content = load_fixture("world_bank_empty.json")
    provider = WorldBankProvider()

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get(
            "https://api.worldbank.org/v2/country/usa/indicator/NY.GDP.MKTP.KD.ZG"
        ).mock(return_value=Response(200, text=fixture_content))

        obs = await provider.fetch_series("gdp_growth", "USA")
        assert obs == []


@pytest.mark.asyncio
async def test_world_bank_date_filtering(load_fixture):
    """Test that start_date and end_date correctly filter output."""
    fixture_content = load_fixture("world_bank_gdp.json")
    provider = WorldBankProvider()

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get(
            "https://api.worldbank.org/v2/country/usa/indicator/NY.GDP.MKTP.KD.ZG"
        ).mock(return_value=Response(200, text=fixture_content))

        obs = await provider.fetch_series(
            "gdp_growth", "USA", start_date="2022-01-01", end_date="2022-12-31"
        )
        assert len(obs) == 1
        assert obs[0].period_date == "2022-01-01"
