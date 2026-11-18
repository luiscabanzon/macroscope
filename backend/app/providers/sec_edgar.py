import logging
import httpx
from typing import Any

from app.data.cik_mapping import get_cik_for_ticker
from app.providers.base import BaseDataProvider, NormalizedObservation

logger = logging.getLogger(__name__)

SEC_CONCEPT_MAPPINGS: dict[str, list[str]] = {
    "revenue": [
        "Revenues",
        "SalesRevenueNet",
        "RevenueFromContractWithCustomerExcludingAssessedTax",
    ],
    "net_income": [
        "NetIncomeLoss",
        "ProfitLoss",
    ],
    "operating_income": [
        "OperatingIncomeLoss",
    ],
    "gross_profit": [
        "GrossProfit",
    ],
    "rnd_expense": [
        "ResearchAndDevelopmentExpense",
    ],
}


class SecEdgarProvider(BaseDataProvider):
    """Zero-auth SEC EDGAR Company Facts XBRL API Adapter."""

    provider_id = "sec_edgar"
    source_name = "SEC EDGAR"

    def __init__(self, base_url: str = "https://data.sec.gov/api/xbrl/companyfacts") -> None:
        self.base_url = base_url.rstrip("/")

    def supports(self, indicator_slug: str, country_code: str) -> bool:
        """Check if indicator is a micro fundamental and ticker is in CIK mapping."""
        if indicator_slug not in SEC_CONCEPT_MAPPINGS:
            return False
        return get_cik_for_ticker(country_code) is not None

    async def fetch_series(
        self,
        indicator_slug: str,
        country_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[NormalizedObservation]:
        """Fetch unauthenticated XBRL facts from SEC EDGAR and extract normalized observations."""
        ticker = country_code.upper()
        cik = get_cik_for_ticker(ticker)
        if not cik:
            logger.warning("No CIK mapping for ticker '%s'", ticker)
            return []

        url = f"{self.base_url}/CIK{cik}.json"
        headers = {
            "User-Agent": "MacroScope Intelligence contact@macroscope.local",
            "Accept-Encoding": "gzip, deflate",
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                payload = response.json()
        except Exception as exc:
            logger.warning("SEC EDGAR request failed for %s (CIK %s): %s", ticker, cik, exc)
            return []

        gaap_facts = payload.get("facts", {}).get("us-gaap", {})
        if not gaap_facts:
            return []

        concept_candidates = SEC_CONCEPT_MAPPINGS.get(indicator_slug, [])
        target_units: list[dict[str, Any]] | None = None

        for concept in concept_candidates:
            if concept in gaap_facts and "USD" in gaap_facts[concept].get("units", {}):
                target_units = gaap_facts[concept]["units"]["USD"]
                break

        if not target_units:
            return []

        # Deduplicate entries by (frequency, end_date), preferring latest filed
        dedup_map: dict[tuple[str, str], dict[str, Any]] = {}
        for entry in target_units:
            form = entry.get("form")
            if form not in {"10-K", "10-Q"}:
                continue

            end_dt = entry.get("end")
            val = entry.get("val")
            if not end_dt or val is None:
                continue

            freq = "A" if form == "10-K" else "Q"
            key = (freq, end_dt)

            existing = dedup_map.get(key)
            if not existing or str(entry.get("filed", "")) > str(existing.get("filed", "")):
                dedup_map[key] = entry

        observations: list[NormalizedObservation] = []
        for (freq, end_dt), entry in dedup_map.items():
            if start_date and end_dt < start_date:
                continue
            if end_date and end_dt > end_date:
                continue

            try:
                numeric_val = float(entry["val"])
            except (ValueError, TypeError):
                continue

            observations.append(
                NormalizedObservation(
                    country_code=ticker,
                    indicator_slug=indicator_slug,
                    period_date=end_dt,
                    frequency=freq,
                    value=numeric_val,
                    unit="USD",
                    source=self.source_name,
                )
            )

        observations.sort(key=lambda o: o.period_date)
        return observations

    async def health_check(self) -> bool:
        """Check SEC EDGAR API responsiveness."""
        url = f"{self.base_url}/CIK0000320193.json"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url, headers={"User-Agent": "MacroScope Intelligence contact@macroscope.local"})
                return res.status_code == 200
        except Exception:
            return False
