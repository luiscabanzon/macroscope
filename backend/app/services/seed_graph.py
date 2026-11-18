import asyncio
import logging
from app.config import settings
from app.data.companies_seed import get_seed_companies, get_seed_competitors
from app.db.database import get_connection, init_db, upsert_companies, upsert_competitors

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def seed_graph_database(db_path: str | None = None) -> tuple[int, int]:
    """Seed companies and competitor relationships into SQLite."""
    target_db = db_path or settings.db_path
    await init_db(target_db)

    companies = get_seed_companies()
    competitors = get_seed_competitors()

    logger.info("Seeding %d companies and %d competitor edges into %s...", len(companies), len(competitors), target_db)

    async with get_connection(target_db) as conn:
        inserted_companies = await upsert_companies(conn, companies)
        inserted_competitors = await upsert_competitors(conn, competitors)

    logger.info("Successfully seeded %d companies and %d competitor edges.", inserted_companies, inserted_competitors)
    return inserted_companies, inserted_competitors


def main() -> None:
    asyncio.run(seed_graph_database())


if __name__ == "__main__":
    main()
