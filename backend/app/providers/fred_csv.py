import csv
import io
import logging
import httpx
from typing import Any

from app.providers.base import BaseDataProvider, NormalizedObservation

logger = logging.getLogger(__name__)

FRED_SERIES_MAP: dict[str, dict[str, Any]] = {
    "oil_brent": {
        "series_id": "DCOILBRENTEU",
        "unit": "USD/bbl",
        "frequency": "D",
        "supported_countries": None,  # Global commodity, available for any country query or 'WLD'
        "description": "Crude Oil Prices: Brent - Europe",
    },
    "oil_wti": {
        "series_id": "DCOILWTICO",
        "unit": "USD/bbl",
        "frequency": "D",
        "supported_countries": None,  # Global commodity
        "description": "Crude Oil Prices: West Texas Intermediate (WTI)",
    },
    "auto_sales": {
        "series_id": "TOTALSA",
        "unit": "Millions",
        "frequency": "M",
        "supported_countries": {"USA"},
        "description": "Total Vehicle Sales (Seasonally Adjusted Annual Rate)",
    },
    "interest_rate": {
        "series_id": "FEDFUNDS",
        "unit": "%",
        "frequency": "M",
        "supported_countries": {"USA"},
        "description": "Federal Funds Effective Rate",
    },
    "unemployment_rate": {
        "series_id": "UNRATE",
        "unit": "%",
        "frequency": "M",
        "supported_countries": {"USA"},
        "description": "Civilian Unemployment Rate (Monthly)",
    },
    "inflation_cpi": {
        "series_id": "CPIAUCSL",
        "unit": "Index",
        "frequency": "M",
        "supported_countries": {"USA"},
        "description": "Consumer Price Index for All Urban Consumers",
    },
}


class FredCsvProvider(BaseDataProvider):
    """Zero-auth St. Louis Fed (FRED) Public CSV Stream Adapter."""

    provider_id = "fred_csv"
    source_name = "FRED"

    def __init__(self, base_url: str = "https://fred.stlouisfed.org/graph/fredgraph.csv") -> None:
        self.base_url = base_url

    def supports(self, indicator_slug: str, country_code: str) -> bool:
        """Check if FRED CSV maps this indicator for the target country/entity."""
        meta = FRED_SERIES_MAP.get(indicator_slug)
        if not meta:
            return False
        supported_countries = meta["supported_countries"]
        if supported_countries is None:
            # Global commodities supported for any country query
            return True
        return country_code.upper() in supported_countries

    async def fetch_series(
        self,
        indicator_slug: str,
        country_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[NormalizedObservation]:
        """Download public CSV directly from FRED and parse into normalized observations."""
        meta = FRED_SERIES_MAP.get(indicator_slug)
        if not meta:
            raise ValueError(f"Indicator '{indicator_slug}' not supported by FredCsvProvider")

        series_id = meta["series_id"]
        params = {"id": series_id}

        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"User-Agent": "MacroScope/0.1.0"}
            response = await client.get(self.base_url, params=params, headers=headers)
            response.raise_for_status()
            csv_text = response.text

        reader = csv.reader(io.StringIO(csv_text))
        try:
            header = next(reader)
        except StopIteration:
            return []

        # Header check: expected ["DATE", series_id]
        if not header or len(header) < 2 or header[0].strip().upper() != "DATE":
            logger.warning("Unrecognized CSV header from FRED for series %s: %s", series_id, header)
            return []

        observations: list[NormalizedObservation] = []
        entity_code = country_code.upper()

        for row in reader:
            if len(row) < 2:
                continue

            raw_date = row[0].strip()
            raw_val = row[1].strip()

            # FRED represents missing/holiday values with "."
            if not raw_val or raw_val == ".":
                continue

            try:
                numeric_val = float(raw_val)
            except ValueError:
                continue

            # Standardize date format YYYY-MM-DD
            if len(raw_date) == 7 and "-" in raw_date:
                period_date = f"{raw_date}-01"
            elif len(raw_date) == 10:
                period_date = raw_date
            else:
                continue

            if start_date and period_date < start_date:
                continue
            if end_date and period_date > end_date:
                continue

            observations.append(
                NormalizedObservation(
                    country_code=entity_code,
                    indicator_slug=indicator_slug,
                    period_date=period_date,
                    frequency=meta["frequency"],
                    value=numeric_val,
                    unit=meta["unit"],
                    source=self.source_name,
                )
            )

        observations.sort(key=lambda o: o.period_date)
        return observations

    async def health_check(self) -> bool:
        """Verify connectivity to FRED public CSV server."""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(
                    self.base_url,
                    params={"id": "DCOILBRENTEU"},
                    headers={"User-Agent": "MacroScope/0.1.0"},
                )
                return res.status_code == 200
        except Exception:
            return False
