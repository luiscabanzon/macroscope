import logging
import httpx
from typing import Any

from app.providers.base import BaseDataProvider, NormalizedObservation

logger = logging.getLogger(__name__)

WORLD_BANK_INDICATOR_MAP: dict[str, dict[str, Any]] = {
    "gdp_growth": {
        "code": "NY.GDP.MKTP.KD.ZG",
        "unit": "%",
        "frequency": "A",
        "description": "GDP growth (annual %)",
    },
    "inflation_cpi": {
        "code": "FP.CPI.TOTL.ZG",
        "unit": "%",
        "frequency": "A",
        "description": "Inflation, consumer prices (annual %)",
    },
    "unemployment_rate": {
        "code": "SL.UEM.TOTL.ZS",
        "unit": "%",
        "frequency": "A",
        "description": "Unemployment, total (% of total labor force)",
    },
    "bank_npl_ratio": {
        "code": "FB.AST.NPLS.ZS",
        "unit": "%",
        "frequency": "A",
        "description": "Bank nonperforming loans to total gross loans (%)",
    },
    "gov_debt_gdp": {
        "code": "GC.DOD.TOTL.GD.ZS",
        "unit": "%",
        "frequency": "A",
        "description": "Central government debt, total (% of GDP)",
    },
}


class WorldBankProvider(BaseDataProvider):
    """Zero-auth World Bank Open Data API v2 Adapter."""

    provider_id = "world_bank"
    source_name = "World Bank"

    def __init__(self, base_url: str = "https://api.worldbank.org/v2") -> None:
        self.base_url = base_url.rstrip("/")

    def supports(self, indicator_slug: str, country_code: str) -> bool:
        """Supports mapped indicators for all ISO-3 countries except global aggregates or tickers."""
        if indicator_slug not in WORLD_BANK_INDICATOR_MAP:
            return False
        # Do not support corporate tickers or 'WLD' for certain indicators if needed,
        # but World Bank supports WLD and 200+ ISO-3 countries
        return len(country_code) == 3 and country_code.isalpha()

    async def fetch_series(
        self,
        indicator_slug: str,
        country_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[NormalizedObservation]:
        """Fetch indicator series from World Bank API and normalize."""
        meta = WORLD_BANK_INDICATOR_MAP.get(indicator_slug)
        if not meta:
            raise ValueError(f"Indicator '{indicator_slug}' not supported by WorldBankProvider")

        wb_code = meta["code"]
        url = f"{self.base_url}/country/{country_code.lower()}/indicator/{wb_code}"
        params = {
            "format": "json",
            "per_page": 1000,
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            headers = {"User-Agent": "MacroScope/0.1.0"}
            response = await client.get(url, params=params, headers=headers)
            response.raise_for_status()
            payload = response.json()

        # World Bank API returns a 2-element list: [page_metadata, data_records]
        # On error or invalid parameter, it returns [ {"message": [...] } ]
        if not isinstance(payload, list) or len(payload) < 2:
            logger.warning(
                "World Bank returned unexpected payload for %s/%s: %s",
                country_code,
                indicator_slug,
                payload,
            )
            return []

        records = payload[1]
        if not isinstance(records, list):
            return []

        observations: list[NormalizedObservation] = []
        for item in records:
            raw_val = item.get("value")
            if raw_val is None:
                continue

            try:
                numeric_val = float(raw_val)
            except (ValueError, TypeError):
                continue

            raw_date = str(item.get("date", "")).strip()
            if not raw_date:
                continue

            # World Bank dates are typically 'YYYY' or 'YYYYQ1' or 'YYYYM01'
            if len(raw_date) == 4 and raw_date.isdigit():
                period_date = f"{raw_date}-01-01"
            elif len(raw_date) == 7 and "-" in raw_date:
                period_date = f"{raw_date}-01"
            elif len(raw_date) == 10:
                period_date = raw_date
            else:
                period_date = f"{raw_date[:4]}-01-01"

            if start_date and period_date < start_date:
                continue
            if end_date and period_date > end_date:
                continue

            # Ensure country code is standardized
            iso3 = (item.get("countryiso3code") or country_code).upper()

            observations.append(
                NormalizedObservation(
                    country_code=iso3,
                    indicator_slug=indicator_slug,
                    period_date=period_date,
                    frequency=meta["frequency"],
                    value=numeric_val,
                    unit=meta["unit"],
                    source=self.source_name,
                )
            )

        # Sort chronologically
        observations.sort(key=lambda o: o.period_date)
        return observations

    async def health_check(self) -> bool:
        """Verify World Bank API connectivity."""
        url = f"{self.base_url}/country/usa/indicator/NY.GDP.MKTP.KD.ZG?format=json&per_page=1"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers={"User-Agent": "MacroScope/0.1.0"})
                return res.status_code == 200
        except Exception:
            return False
