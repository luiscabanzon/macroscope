import asyncio
import logging
from app.config import settings
from app.data.cik_mapping import get_seed_fundamentals
from app.db.database import get_connection, init_db, upsert_observations

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def seed_fundamentals_database(db_path: str | None = None) -> int:
    """Seed SEC EDGAR fundamental financial observations into SQLite."""
    target_db = db_path or settings.db_path
    await init_db(target_db)

    fundamentals = get_seed_fundamentals()
    logger.info("Seeding %d SEC EDGAR fundamental observations into %s...", len(fundamentals), target_db)

    async with get_connection(target_db) as conn:
        inserted = await upsert_observations(conn, fundamentals)

    logger.info("Successfully seeded %d SEC EDGAR observations.", inserted)
    return inserted


def main() -> None:
    asyncio.run(seed_fundamentals_database())


if __name__ == "__main__":
    main()
