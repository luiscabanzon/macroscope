from datetime import datetime, timedelta, timezone
import httpx
import pytest
from app.config import settings
from app.db.database import get_fetch_log, upsert_observations
from app.db.models import ObservationRecord
from app.providers.base import BaseDataProvider, NormalizedObservation
from app.providers.registry import ProviderRegistry
from app.services.cache_manager import CacheManager


class DummyProvider(BaseDataProvider):
    provider_id = "dummy"
    source_name = "Dummy Source"

    def __init__(self, should_fail: bool = False) -> None:
        self.should_fail = should_fail
        self.call_count = 0

    def supports(self, indicator_slug: str, country_code: str) -> bool:
        return indicator_slug == "gdp_growth"

    async def fetch_series(
        self,
        indicator_slug: str,
        country_code: str,
        start_date: str | None = None,
        end_date: str | None = None,
    ) -> list[NormalizedObservation]:
        self.call_count += 1
        if self.should_fail:
            raise httpx.ConnectTimeout("Mocked upstream connection timeout")
        return [
            NormalizedObservation(
                country_code=country_code,
                indicator_slug=indicator_slug,
                period_date="2023-01-01",
                frequency="A",
                value=2.5,
                unit="%",
                source=self.source_name,
            )
        ]

    async def health_check(self) -> bool:
        return not self.should_fail


@pytest.mark.asyncio
async def test_cache_miss_fetches_and_persists(test_db):
    """Verify that a cache miss invokes the provider and persists observations."""
    registry = ProviderRegistry()
    dummy = DummyProvider()
    registry.register(dummy)

    manager = CacheManager(registry=registry, db_path=test_db)

    # First call: cache miss
    obs, is_stale, last_updated = await manager.get_series("USA", "gdp_growth")
    assert len(obs) == 1
    assert obs[0].value == 2.5
    assert is_stale is False
    assert dummy.call_count == 1
    assert last_updated is not None

    # Second call within TTL: cache hit, provider should not be called again
    obs2, is_stale2, _ = await manager.get_series("USA", "gdp_growth")
    assert len(obs2) == 1
    assert is_stale2 is False
    assert dummy.call_count == 1  # Unchanged!


@pytest.mark.asyncio
async def test_cache_graceful_fallback_on_failure(test_db, db_conn):
    """Verify that provider failure gracefully returns stale cached data with is_stale=True."""
    # Pre-populate database with an older observation
    initial_obs = [
        ObservationRecord(
            country_code="USA",
            indicator_slug="gdp_growth",
            period_date="2022-01-01",
            frequency="A",
            value=2.1,
            unit="%",
            source="Old Provider",
        )
    ]
    await upsert_observations(db_conn, initial_obs)

    # Setup failing provider
    registry = ProviderRegistry()
    failing_dummy = DummyProvider(should_fail=True)
    registry.register(failing_dummy)

    manager = CacheManager(registry=registry, db_path=test_db)

    # Upstream fails -> fallback to SQLite cache
    obs, is_stale, _ = await manager.get_series("USA", "gdp_growth", force_refresh=True)
    assert len(obs) == 1
    assert obs[0].value == 2.1
    assert is_stale is True


@pytest.mark.asyncio
async def test_read_only_cache_mode(test_db, monkeypatch):
    """Verify that READ_ONLY_CACHE mode disables all external fetches."""
    monkeypatch.setattr(settings, "read_only_cache", True)

    registry = ProviderRegistry()
    dummy = DummyProvider()
    registry.register(dummy)

    manager = CacheManager(registry=registry, db_path=test_db)

    obs, is_stale, _ = await manager.get_series("USA", "gdp_growth")
    assert is_stale is True
    assert dummy.call_count == 0  # Provider never touched
