import logging
from app.providers.base import BaseDataProvider
from app.providers.fred_csv import FredCsvProvider
from app.providers.world_bank import WorldBankProvider

logger = logging.getLogger(__name__)


class ProviderRegistry:
    """Registry coordinating available data providers and resolving routing priorities."""

    def __init__(self) -> None:
        self._providers: list[BaseDataProvider] = []

    def register(self, provider: BaseDataProvider, high_priority: bool = False) -> None:
        """Register a new provider. If high_priority, insert at front of lookup chain."""
        if high_priority:
            self._providers.insert(0, provider)
        else:
            self._providers.append(provider)
        logger.info("Registered data provider: %s (id=%s)", provider.source_name, provider.provider_id)

    def get_provider(self, indicator_slug: str, country_code: str) -> BaseDataProvider | None:
        """Find the first matching provider that supports the requested entity and indicator."""
        for provider in self._providers:
            if provider.supports(indicator_slug, country_code):
                return provider
        return None

    def list_providers(self) -> list[BaseDataProvider]:
        """List all currently registered providers."""
        return list(self._providers)


def create_default_registry() -> ProviderRegistry:
    """Build the standard production provider registry."""
    registry = ProviderRegistry()
    # FRED takes precedence for high-frequency commodities and US series
    registry.register(FredCsvProvider())
    # World Bank provides broad global coverage for annual macroeconomic series
    registry.register(WorldBankProvider())
    return registry


# Global default singleton registry
default_registry = create_default_registry()
