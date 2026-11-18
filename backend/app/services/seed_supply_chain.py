import asyncio
import logging
from app.config import settings
from app.data.supply_chain_seed import get_seed_supply_chain
from app.db.database import get_connection, init_db, upsert_supply_chain

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def seed_supply_chain_database(db_path: str | None = None) -> int:
    """Seed supply chain links into SQLite."""
    target_db = db_path or settings.db_path
    await init_db(target_db)

    links = get_seed_supply_chain()
    logger.info("Seeding %d enterprise supply chain edges into %s...", len(links), target_db)

    async with get_connection(target_db) as conn:
        inserted = await upsert_supply_chain(conn, links)

    logger.info("Successfully seeded %d supply chain edges.", inserted)
    return inserted


def main() -> None:
    asyncio.run(seed_supply_chain_database())


if __name__ == "__main__":
    main()
