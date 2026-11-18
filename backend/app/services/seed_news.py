import asyncio
import logging
from app.config import settings
from app.data.news_seed import get_seed_news_articles
from app.db.database import get_connection, init_db, upsert_news_articles

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def seed_news_database(db_path: str | None = None) -> int:
    """Pre-populate the SQLite database with curated snapshot news articles."""
    target_db = db_path or settings.db_path
    await init_db(target_db)

    articles = get_seed_news_articles()
    logger.info("Seeding %d news articles into %s...", len(articles), target_db)

    async with get_connection(target_db) as conn:
        inserted = await upsert_news_articles(conn, articles)

    logger.info("Successfully seeded %d news articles into database.", inserted)
    return inserted


def main() -> None:
    asyncio.run(seed_news_database())


if __name__ == "__main__":
    main()
