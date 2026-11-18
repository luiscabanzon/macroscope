import asyncio
from datetime import datetime, timedelta, timezone
import logging

from app.config import settings
from app.db.database import (
    get_company_by_ticker,
    get_company_competitors,
    get_connection,
    get_graph_elements,
    query_companies,
    query_news_articles,
    upsert_news_articles,
)
from app.db.models import CompanyRecord, NewsArticleRecord
from app.providers.rss_news import RssNewsProvider

logger = logging.getLogger(__name__)

NEWS_CACHE_TTL = timedelta(minutes=30)


class CompanyGraphService:
    """Manages company graph queries and contextual RSS news aggregation."""

    def __init__(
        self,
        news_provider: RssNewsProvider | None = None,
        db_path: str | None = None,
    ) -> None:
        self.news_provider = news_provider or RssNewsProvider()
        self.db_path = db_path or settings.db_path

    async def get_graph(self, sector: str | None = None) -> tuple[list[dict], list[dict], list[str]]:
        """Retrieve graph nodes, edges, and sector list."""
        async with get_connection(self.db_path) as conn:
            return await get_graph_elements(conn, sector=sector)

    async def get_company_profile(
        self, ticker: str
    ) -> tuple[CompanyRecord | None, list[tuple[CompanyRecord, str, float]]]:
        """Retrieve company metadata and its competitor pairings."""
        clean_ticker = ticker.upper()
        async with get_connection(self.db_path) as conn:
            company = await get_company_by_ticker(conn, clean_ticker)
            if not company:
                return None, []
            competitors = await get_company_competitors(conn, clean_ticker)
            return company, competitors

    async def get_contextual_news(
        self,
        ticker: str,
        force_refresh: bool = False,
    ) -> dict[str, list[NewsArticleRecord] | list[str] | CompanyRecord | None]:
        """Fetch and partition news for a company, its competitors, and its sector."""
        clean_ticker = ticker.upper()
        company, competitor_tuples = await self.get_company_profile(clean_ticker)
        if not company:
            return {
                "company": None,
                "competitor_tickers": [],
                "company_news": [],
                "competitor_news": [],
                "sector_news": [],
            }

        competitor_tickers = [c[0].ticker for c in competitor_tuples]

        async with get_connection(self.db_path) as conn:
            cached_company_news = await query_news_articles(conn, entity_ticker=clean_ticker, limit=10)
            cached_sector_news = await query_news_articles(conn, sector=company.sector, limit=10)

            # Check cache freshness
            is_company_fresh = False
            if cached_company_news:
                try:
                    fetched_at = datetime.fromisoformat(cached_company_news[0].fetched_at)
                    if datetime.now(timezone.utc) - fetched_at < NEWS_CACHE_TTL:
                        is_company_fresh = True
                except Exception:
                    is_company_fresh = False

            # Check if upstream fetch needed
            if (not is_company_fresh or force_refresh) and not settings.read_only_cache:
                new_articles: list[NewsArticleRecord] = []

                # 1. Fetch company news
                company_articles = await self.news_provider.fetch_company_news(clean_ticker, limit=10)
                new_articles.extend(company_articles)

                # 2. Fetch news for top 3 competitors
                for comp_ticker in competitor_tickers[:3]:
                    comp_articles = await self.news_provider.fetch_company_news(comp_ticker, limit=5)
                    new_articles.extend(comp_articles)

                # 3. Fetch sector news
                sector_articles = await self.news_provider.fetch_sector_news(company.sector, limit=10)
                new_articles.extend(sector_articles)

                if new_articles:
                    await upsert_news_articles(conn, new_articles)

            # Retrieve final partitioned articles from SQLite
            final_company_news = await query_news_articles(conn, entity_ticker=clean_ticker, limit=10)

            # Competitor news: query across all competitor tickers
            final_competitor_news: list[NewsArticleRecord] = []
            for comp_ticker in competitor_tickers:
                comp_records = await query_news_articles(conn, entity_ticker=comp_ticker, limit=5)
                final_competitor_news.extend(comp_records)

            # Sort competitor news chronologically descending and take top 15
            final_competitor_news.sort(key=lambda a: a.published_at, reverse=True)
            final_competitor_news = final_competitor_news[:15]

            final_sector_news = await query_news_articles(conn, sector=company.sector, limit=10)

            return {
                "company": company,
                "competitor_tickers": competitor_tickers,
                "company_news": final_company_news,
                "competitor_news": final_competitor_news,
                "sector_news": final_sector_news,
            }
