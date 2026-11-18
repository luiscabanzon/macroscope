import pytest
import respx
from httpx import Response

from app.providers.fred_csv import FredCsvProvider


@pytest.mark.asyncio
async def test_fred_csv_brent_oil(load_fixture):
    """Test parsing FRED CSV for Brent Oil with '.' missing data points."""
    csv_content = load_fixture("fred_brent_oil.csv")
    provider = FredCsvProvider()

    assert provider.supports("oil_brent", "USA") is True
    assert provider.supports("oil_brent", "WLD") is True
    assert provider.supports("auto_sales", "DEU") is False
    assert provider.supports("auto_sales", "USA") is True

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv",
            params={"id": "DCOILBRENTEU"},
        ).mock(return_value=Response(200, text=csv_content))

        obs = await provider.fetch_series("oil_brent", "WLD")

        # 4 rows in CSV: 1 header, 1 missing '.', 3 valid numeric values
        assert len(obs) == 3
        assert obs[0].period_date == "2024-01-02"
        assert obs[0].value == 77.04
        assert obs[0].unit == "USD/bbl"
        assert obs[0].frequency == "D"
        assert obs[0].source == "FRED"
        assert obs[0].country_code == "WLD"

        assert obs[1].period_date == "2024-01-03"
        assert obs[1].value == 78.25

        assert obs[2].period_date == "2024-01-04"
        assert obs[2].value == 77.61


@pytest.mark.asyncio
async def test_fred_csv_auto_sales(load_fixture):
    """Test parsing FRED monthly auto sales series."""
    csv_content = load_fixture("fred_auto_sales.csv")
    provider = FredCsvProvider()

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get(
            "https://fred.stlouisfed.org/graph/fredgraph.csv",
            params={"id": "TOTALSA"},
        ).mock(return_value=Response(200, text=csv_content))

        obs = await provider.fetch_series("auto_sales", "USA")
        assert len(obs) == 3
        assert obs[0].period_date == "2023-11-01"
        assert obs[0].value == 15.652
        assert obs[0].unit == "Millions"
        assert obs[0].frequency == "M"
        assert obs[0].country_code == "USA"
