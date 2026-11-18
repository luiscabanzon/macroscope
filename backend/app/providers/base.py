from abc import ABC, abstractmethod
from pydantic import BaseModel, Field


class NormalizedObservation(BaseModel):
    """Unified normalized time-series data point contract."""
    country_code: str = Field(description="ISO-3 code (e.g. USA, DEU, WLD) or entity ticker in v2 (e.g. AAPL)")
    indicator_slug: str = Field(description="Unified indicator slug (e.g. gdp_growth, oil_brent, revenue)")
    period_date: str = Field(description="ISO-8601 date string: YYYY-MM-DD")
    frequency: str = Field(description="Frequency code: 'A' (Annual), 'Q' (Quarterly), 'M' (Monthly), 'D' (Daily)")
    value: float = Field(description="Normalized floating point value")
    unit: str = Field(description="Standardized unit label (e.g. %, USD/bbl, Millions)")
    source: str = Field(description="Human-readable provider name (e.g. World Bank, FRED, SEC EDGAR)")


class BaseDataProvider(ABC):
    """Abstract base class for all keyless macroeconomic and microeconomic data providers."""

    provider_id: str
    source_name: str

    @abstractmethod
    def supports(self, indicator_slug: str, country_code: str) -> bool:
        """Return True if this provider can fulfill the requested indicator and entity."""
        pass

    @abstractmethod
    async def fetch_series(
        self,
        indicator_slug: str,
        country_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[NormalizedObservation]:
        """Fetch raw data from upstream, parse, and normalize into standardized observations."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check availability and connectivity of the upstream provider endpoint."""
        pass
