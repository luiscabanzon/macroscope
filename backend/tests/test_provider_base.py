import pytest
from app.providers.base import BaseDataProvider, NormalizedObservation
from app.providers.registry import ProviderRegistry, default_registry


class MockSecEdgarProvider(BaseDataProvider):
    """Simulated v2 Micro Provider demonstrating plug-and-play capability."""

    provider_id = "sec_edgar"
    source_name = "SEC EDGAR"

    def supports(self, indicator_slug: str, country_code: str) -> bool:
        # Micro data: country_code is a company ticker (e.g. AAPL, MSFT)
        return indicator_slug in {"revenue", "net_income"} and country_code.isalpha()

    async def fetch_series(
        self,
        indicator_slug: str,
        country_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[NormalizedObservation]:
        return [
            NormalizedObservation(
                country_code=country_code.upper(),
                indicator_slug=indicator_slug,
                period_date="2023-12-31",
                frequency="A",
                value=383285000000.0,
                unit="USD",
                source=self.source_name,
            )
        ]

    async def health_check(self) -> bool:
        return True


@pytest.mark.asyncio
async def test_provider_registry_and_v2_extensibility():
    """Verify that a new v2 micro-data provider registers and resolves cleanly."""
    registry = ProviderRegistry()

    # Initially empty
    assert registry.get_provider("revenue", "AAPL") is None

    # Register mock SEC EDGAR provider
    edgar_provider = MockSecEdgarProvider()
    registry.register(edgar_provider)

    resolved = registry.get_provider("revenue", "AAPL")
    assert resolved is not None
    assert resolved.source_name == "SEC EDGAR"

    data = await resolved.fetch_series("revenue", "AAPL")
    assert len(data) == 1
    assert data[0].country_code == "AAPL"
    assert data[0].indicator_slug == "revenue"
    assert data[0].value == 383285000000.0
    assert data[0].source == "SEC EDGAR"


def test_default_registry_resolution():
    """Test resolution order of standard providers."""
    # Commodity should resolve to FRED
    oil_provider = default_registry.get_provider("oil_brent", "USA")
    assert oil_provider is not None
    assert oil_provider.provider_id == "fred_csv"

    # Multi-country annual GDP should resolve to World Bank
    gdp_provider = default_registry.get_provider("gdp_growth", "DEU")
    assert gdp_provider is not None
    assert gdp_provider.provider_id == "world_bank"
