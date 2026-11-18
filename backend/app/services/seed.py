import argparse
import asyncio
import logging
from app.config import settings
from app.db.database import init_db
from app.services.cache_manager import CacheManager, INDICATOR_METADATA

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

DEFAULT_SEED_COUNTRIES = [
    "USA", "GBR", "DEU", "FRA", "JPN", "CAN", "ITA", "CHN", "IND"
]

DEFAULT_SEED_INDICATORS = [
    "gdp_growth",
    "inflation_cpi",
    "unemployment_rate",
    "bank_npl_ratio",
    "gov_debt_gdp",
    "oil_brent",
    "auto_sales",
]


async def seed_database(
    countries: list[str],
    indicators: list[str],
    dry_run: bool = False,
    delay_seconds: float = 0.25,
) -> dict[str, int]:
    """Pre-warm the SQLite database with macro and commodity series."""
    await init_db()
    cache_mgr = CacheManager()
    summary: dict[str, int] = {}

    total_tasks = len(countries) * len(indicators)
    current = 0

    logger.info("Starting database seed for %d economies across %d indicators...", len(countries), len(indicators))

    for country in countries:
        for indicator in indicators:
            current += 1
            provider = cache_mgr.registry.get_provider(indicator, country)
            if not provider:
                continue

            if dry_run:
                logger.info(
                    "[%d/%d] DRY-RUN: Would fetch %s for %s via %s",
                    current,
                    total_tasks,
                    indicator,
                    country,
                    provider.source_name,
                )
                summary[f"{country}_{indicator}"] = 0
                continue

            logger.info(
                "[%d/%d] Seeding %s for %s via %s...",
                current,
                total_tasks,
                indicator,
                country,
                provider.source_name,
            )

            try:
                obs, is_stale, _ = await cache_mgr.get_series(
                    country_code=country,
                    indicator_slug=indicator,
                    force_refresh=True,
                )
                summary[f"{country}_{indicator}"] = len(obs)
                logger.info(
                    "Successfully seeded %s for %s: %d observations (stale=%s)",
                    indicator,
                    country,
                    len(obs),
                    is_stale,
                )
            except Exception as e:
                logger.error("Failed seeding %s for %s: %s", indicator, country, e)
                summary[f"{country}_{indicator}"] = -1

            if delay_seconds > 0:
                await asyncio.sleep(delay_seconds)

    logger.info("Seed complete. Processed %d series combinations.", len(summary))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="MacroScope Database Pre-Warm Seed CLI")
    parser.add_argument(
        "--countries",
        type=str,
        default=",".join(DEFAULT_SEED_COUNTRIES),
        help="Comma-separated ISO-3 country codes to pre-warm",
    )
    parser.add_argument(
        "--indicators",
        type=str,
        default=",".join(DEFAULT_SEED_INDICATORS),
        help="Comma-separated indicator slugs to pre-warm",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate execution without making network calls or database writes",
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=0.25,
        help="Politeness delay in seconds between external provider requests",
    )

    args = parser.parse_args()
    target_countries = [c.strip().upper() for c in args.countries.split(",") if c.strip()]
    target_indicators = [i.strip() for i in args.indicators.split(",") if i.strip()]

    asyncio.run(
        seed_database(
            countries=target_countries,
            indicators=target_indicators,
            dry_run=args.dry_run,
            delay_seconds=args.delay,
        )
    )


if __name__ == "__main__":
    main()
