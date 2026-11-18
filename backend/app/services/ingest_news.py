import argparse
import asyncio
import logging
from app.config import settings
from app.db.database import get_connection, init_db, query_companies, upsert_news_articles
from app.providers.rss_news import RssNewsProvider

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


async def ingest_live_news(
    tickers: list[str] | None = None,
    sectors: list[str] | None = None,
    delay_seconds: float = 0.5,
    dry_run: bool = False,
    db_path: str | None = None,
) -> int:
    """Crawl and update news articles for companies and sectors from public RSS feeds."""
    target_db = db_path or settings.db_path
    await init_db(target_db)
    provider = RssNewsProvider()

    async with get_connection(target_db) as conn:
        all_companies = await query_companies(conn)

    target_tickers = tickers or [c.ticker for c in all_companies[:15]]  # Top 15 bellwethers by default
    target_sectors = sectors or list({c.sector for c in all_companies})

    total_ingested = 0
    logger.info("Starting live RSS ingestion for %d tickers and %d sectors...", len(target_tickers), len(target_sectors))

    # 1. Company news crawl
    for idx, ticker in enumerate(target_tickers, 1):
        if dry_run:
            logger.info("[%d/%d] DRY-RUN: Would crawl RSS for %s", idx, len(target_tickers), ticker)
            continue

        logger.info("[%d/%d] Crawling RSS headlines for %s...", idx, len(target_tickers), ticker)
        try:
            articles = await provider.fetch_company_news(ticker, limit=8)
            if articles:
                async with get_connection(target_db) as conn:
                    count = await upsert_news_articles(conn, articles)
                    total_ingested += count
                logger.info("Saved %d articles for %s", len(articles), ticker)
        except Exception as exc:
            logger.warning("Error fetching RSS for %s: %s", ticker, exc)

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    # 2. Sector news crawl
    for idx, sector in enumerate(target_sectors, 1):
        if dry_run:
            logger.info("[%d/%d] DRY-RUN: Would crawl sector feed for %s", idx, len(target_sectors), sector)
            continue

        logger.info("[%d/%d] Crawling sector feed for %s...", idx, len(target_sectors), sector)
        try:
            sector_articles = await provider.fetch_sector_news(sector, limit=8)
            if sector_articles:
                async with get_connection(target_db) as conn:
                    count = await upsert_news_articles(conn, sector_articles)
                    total_ingested += count
                logger.info("Saved %d sector articles for %s", len(sector_articles), sector)
        except Exception as exc:
            logger.warning("Error fetching sector RSS for %s: %s", sector, exc)

        if delay_seconds > 0:
            await asyncio.sleep(delay_seconds)

    logger.info("Ingestion finished. Total new/updated articles: %d", total_ingested)
    return total_ingested


def main() -> None:
    parser = argparse.ArgumentParser(description="Live RSS News Ingestion Pipeline")
    parser.add_argument("--tickers", type=str, default="", help="Comma-separated tickers to crawl (e.g. AAPL,NVDA,TSLA)")
    parser.add_argument("--sectors", type=str, default="", help="Comma-separated sectors to crawl")
    parser.add_argument("--delay", type=float, default=0.5, help="Politeness delay between requests (seconds)")
    parser.add_argument("--dry-run", action="store_true", help="Simulate without network calls or DB writes")

    args = parser.parse_args()
    parsed_tickers = [t.strip().upper() for t in args.tickers.split(",") if t.strip()] or None
    parsed_sectors = [s.strip() for s in args.sectors.split(",") if s.strip()] or None

    asyncio.run(
        ingest_live_news(
            tickers=parsed_tickers,
            sectors=parsed_sectors,
            delay_seconds=args.delay,
            dry_run=args.dry_run,
        )
    )


if __name__ == "__main__":
    main()
