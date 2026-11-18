import logging
from datetime import datetime, timedelta, timezone
from typing import Any
import aiosqlite

from app.config import settings
from app.db.database import (
    get_connection,
    get_fetch_log,
    query_observations,
    set_fetch_log,
    upsert_observations,
)
from app.db.models import ObservationRecord
from app.providers.registry import ProviderRegistry, default_registry

logger = logging.getLogger(__name__)

# Indicator Metadata & Default TTL categorizations
INDICATOR_METADATA: dict[str, dict[str, Any]] = {
    "gdp_growth": {
        "name": "Real GDP Growth",
        "category": "macro_annual",
        "default_unit": "%",
        "default_source": "World Bank",
    },
    "inflation_cpi": {
        "name": "Inflation (CPI)",
        "category": "macro_monthly",
        "default_unit": "%",
        "default_source": "World Bank / FRED",
    },
    "unemployment_rate": {
        "name": "Unemployment Rate",
        "category": "macro_monthly",
        "default_unit": "%",
        "default_source": "World Bank / FRED",
    },
    "interest_rate": {
        "name": "Central Bank Policy Rate",
        "category": "macro_monthly",
        "default_unit": "%",
        "default_source": "FRED",
    },
    "bank_npl_ratio": {
        "name": "Bank Non-Performing Loans",
        "category": "macro_annual",
        "default_unit": "%",
        "default_source": "World Bank",
    },
    "auto_sales": {
        "name": "Vehicle Sales / Registrations",
        "category": "macro_monthly",
        "default_unit": "Millions",
        "default_source": "FRED",
    },
    "gov_debt_gdp": {
        "name": "Government Debt (% of GDP)",
        "category": "macro_annual",
        "default_unit": "%",
        "default_source": "World Bank",
    },
    "oil_brent": {
        "name": "Brent Crude Oil",
        "category": "commodity_daily",
        "default_unit": "USD/bbl",
        "default_source": "FRED",
    },
    "oil_wti": {
        "name": "WTI Crude Oil",
        "category": "commodity_daily",
        "default_unit": "USD/bbl",
        "default_source": "FRED",
    },
}


class CacheManager:
    """Manages read-through caching, tiered TTL freshness, and resilient fallback to SQLite."""

    def __init__(
        self,
        registry: ProviderRegistry | None = None,
        db_path: str | None = None,
    ) -> None:
        self.registry = registry or default_registry
        self.db_path = db_path or settings.db_path

    def get_ttl(self, indicator_slug: str) -> timedelta:
        """Resolve TTL duration based on indicator frequency and volatility category."""
        meta = INDICATOR_METADATA.get(indicator_slug, {})
        category = meta.get("category", "macro_annual")

        if category == "commodity_daily":
            return timedelta(hours=settings.ttl_high_freq_hours)
        elif category == "macro_monthly":
            return timedelta(hours=settings.ttl_recent_hours)
        else:
            return timedelta(days=settings.ttl_historical_days)

    async def get_series(
        self,
        country_code: str,
        indicator_slug: str,
        start_date: str | None = None,
        end_date: str | None = None,
        force_refresh: bool = False,
    ) -> tuple[list[ObservationRecord], bool, str | None]:
        """Read-through getter for time-series observations.

        Returns:
            tuple of (observations, is_stale, last_updated_iso)
        """
        entity = country_code.upper()
        ttl = self.get_ttl(indicator_slug)

        async with get_connection(self.db_path) as conn:
            fetch_log = await get_fetch_log(conn, entity, indicator_slug)

            is_fresh = False
            last_fetched: datetime | None = None

            if fetch_log and fetch_log.status == "SUCCESS":
                try:
                    last_fetched = datetime.fromisoformat(fetch_log.last_fetched_at)
                    if datetime.now(timezone.utc) - last_fetched < ttl:
                        is_fresh = True
                except (ValueError, TypeError):
                    is_fresh = False

            # Cache hit: fresh data available
            if is_fresh and not force_refresh:
                records = await query_observations(
                    conn, entity, indicator_slug, start_date=start_date, end_date=end_date
                )
                if records:
                    return records, False, fetch_log.last_fetched_at  # type: ignore

            # Public demo / read-only cache guard
            if settings.read_only_cache:
                logger.info("READ_ONLY_CACHE is active: skipping upstream fetch for %s/%s", entity, indicator_slug)
                records = await query_observations(
                    conn, entity, indicator_slug, start_date=start_date, end_date=end_date
                )
                last_updated = fetch_log.last_fetched_at if fetch_log else None
                return records, True, last_updated

            # Cache miss or stale: resolve provider
            provider = self.registry.get_provider(indicator_slug, entity)
            if not provider:
                logger.warning("No registered provider supports %s for %s", indicator_slug, entity)
                records = await query_observations(
                    conn, entity, indicator_slug, start_date=start_date, end_date=end_date
                )
                last_updated = fetch_log.last_fetched_at if fetch_log else None
                return records, True, last_updated

            # Attempt live upstream fetch
            now_iso = datetime.now(timezone.utc).isoformat()
            try:
                raw_obs = await provider.fetch_series(indicator_slug, entity)
                records_to_insert = [
                    ObservationRecord(
                        country_code=obs.country_code,
                        indicator_slug=obs.indicator_slug,
                        period_date=obs.period_date,
                        frequency=obs.frequency,
                        value=obs.value,
                        unit=obs.unit,
                        source=obs.source,
                    )
                    for obs in raw_obs
                ]

                if records_to_insert:
                    await upsert_observations(conn, records_to_insert)
                    await set_fetch_log(conn, entity, indicator_slug, status="SUCCESS", last_fetched_at=now_iso)
                else:
                    await set_fetch_log(conn, entity, indicator_slug, status="EMPTY", last_fetched_at=now_iso)

                observations = await query_observations(
                    conn, entity, indicator_slug, start_date=start_date, end_date=end_date
                )
                return observations, False, now_iso

            except Exception as exc:
                # Upstream error: log failure and gracefully serve stale records if available
                logger.error(
                    "Upstream provider failure (%s) for %s/%s: %s. Falling back to cached data.",
                    provider.source_name,
                    entity,
                    indicator_slug,
                    exc,
                )
                await set_fetch_log(
                    conn,
                    entity,
                    indicator_slug,
                    status="ERROR",
                    last_fetched_at=now_iso,
                    error_message=str(exc),
                )
                stale_records = await query_observations(
                    conn, entity, indicator_slug, start_date=start_date, end_date=end_date
                )
                last_updated = fetch_log.last_fetched_at if fetch_log else now_iso
                return stale_records, True, last_updated
