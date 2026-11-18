import email.utils
import hashlib
import html
import logging
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
import httpx

from app.db.models import NewsArticleRecord

logger = logging.getLogger(__name__)

# HTML tag stripping regex
TAG_RE = re.compile(r"<[^>]+>")

# Curated Keyless Public Sector RSS Feeds
SECTOR_RSS_FEEDS: dict[str, list[dict[str, str]]] = {
    "Information Technology": [
        {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=%5EIXIC", "source": "Yahoo Tech"},
        {"url": "https://news.google.com/rss/search?q=Semiconductors+AI+chips+technology+market&hl=en-US&gl=US&ceid=US:en", "source": "Google Tech"},
    ],
    "Energy": [
        {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=XLE", "source": "Yahoo Energy"},
        {"url": "https://news.google.com/rss/search?q=crude+oil+energy+natural+gas+market&hl=en-US&gl=US&ceid=US:en", "source": "Google Energy"},
    ],
    "Financials": [
        {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=XLF", "source": "Yahoo Finance"},
        {"url": "https://news.google.com/rss/search?q=Federal+Reserve+banking+financial+stocks&hl=en-US&gl=US&ceid=US:en", "source": "Google Banking"},
    ],
    "Consumer Discretionary": [
        {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=XLY", "source": "Yahoo Consumer"},
        {"url": "https://news.google.com/rss/search?q=electric+vehicles+auto+retail+consumer+spending&hl=en-US&gl=US&ceid=US:en", "source": "Google Auto/Retail"},
    ],
    "Health Care": [
        {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=XLV", "source": "Yahoo Health"},
        {"url": "https://news.google.com/rss/search?q=pharmaceuticals+biotech+healthcare+FDA+approvals&hl=en-US&gl=US&ceid=US:en", "source": "Google Pharma"},
    ],
    "Industrials": [
        {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=XLI", "source": "Yahoo Industrials"},
        {"url": "https://news.google.com/rss/search?q=aerospace+defense+industrial+manufacturing&hl=en-US&gl=US&ceid=US:en", "source": "Google Industrials"},
    ],
    "Communication Services": [
        {"url": "https://feeds.finance.yahoo.com/rss/2.0/headline?s=XLC", "source": "Yahoo Media"},
        {"url": "https://news.google.com/rss/search?q=streaming+telecom+social+media+advertising&hl=en-US&gl=US&ceid=US:en", "source": "Google Media"},
    ],
}


def clean_text(raw_html: str | None) -> str:
    """Remove HTML tags and decode HTML entities."""
    if not raw_html:
        return ""
    text = TAG_RE.sub("", raw_html)
    return html.unescape(text).strip()


def parse_rfc822_date(date_str: str | None) -> str:
    """Parse RFC-822 / RFC-2822 pubDate string into ISO-8601 string."""
    if not date_str:
        return datetime.now(timezone.utc).isoformat()
    try:
        dt = email.utils.parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


class RssNewsProvider:
    """Zero-auth public RSS news aggregator with entity cross-tagging."""

    def __init__(self) -> None:
        self.yahoo_base = "https://feeds.finance.yahoo.com/rss/2.0/headline"
        self.google_news_base = "https://news.google.com/rss/search"

    async def fetch_company_news(self, ticker: str, limit: int = 15) -> list[NewsArticleRecord]:
        """Fetch real-time RSS news articles for a specific stock ticker."""
        clean_ticker = ticker.upper()
        url = f"{self.yahoo_base}?s={clean_ticker}&region=US&lang=en-US"

        articles: list[NewsArticleRecord] = []
        now_iso = datetime.now(timezone.utc).isoformat()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    articles = self.parse_rss_xml(
                        xml_content=response.text,
                        source_label="Yahoo Finance",
                        entity_ticker=clean_ticker,
                        now_iso=now_iso,
                        limit=limit,
                    )
        except Exception as exc:
            logger.warning("Failed fetching Yahoo Finance RSS for %s: %s", clean_ticker, exc)

        # Fallback to Google News RSS if Yahoo returned no items
        if not articles:
            articles = await self.fetch_search_news(
                query=f"{clean_ticker} stock",
                entity_ticker=clean_ticker,
                limit=limit,
            )

        return articles

    async def fetch_search_news(
        self,
        query: str,
        entity_ticker: str | None = None,
        sector: str | None = None,
        limit: int = 15,
    ) -> list[NewsArticleRecord]:
        """Fetch RSS news from Google News search for a query or sector."""
        encoded_query = query.replace(" ", "+")
        url = f"{self.google_news_base}?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
        now_iso = datetime.now(timezone.utc).isoformat()

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                headers = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"}
                response = await client.get(url, headers=headers)
                if response.status_code == 200:
                    return self.parse_rss_xml(
                        xml_content=response.text,
                        source_label="Google News",
                        entity_ticker=entity_ticker,
                        sector=sector,
                        now_iso=now_iso,
                        limit=limit,
                    )
        except Exception as exc:
            logger.warning("Failed fetching Google News RSS for query '%s': %s", query, exc)

        return []

    async def fetch_sector_news(self, sector: str, limit: int = 15) -> list[NewsArticleRecord]:
        """Fetch sector news from dedicated sector feeds or keyword search."""
        feeds = SECTOR_RSS_FEEDS.get(sector, [])
        now_iso = datetime.now(timezone.utc).isoformat()
        articles: list[NewsArticleRecord] = []

        for feed_config in feeds:
            url = feed_config["url"]
            source = feed_config["source"]
            try:
                async with httpx.AsyncClient(timeout=8.0) as client:
                    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
                    response = await client.get(url, headers=headers)
                    if response.status_code == 200:
                        parsed = self.parse_rss_xml(
                            xml_content=response.text,
                            source_label=source,
                            sector=sector,
                            now_iso=now_iso,
                            limit=limit,
                        )
                        articles.extend(parsed)
                        if len(articles) >= limit:
                            break
            except Exception as exc:
                logger.warning("Failed fetching sector feed %s for %s: %s", url, sector, exc)

        if not articles:
            # Fallback search query
            query = f"{sector} industry market news"
            articles = await self.fetch_search_news(query=query, sector=sector, limit=limit)

        return articles[:limit]

    def parse_rss_xml(
        self,
        xml_content: str,
        source_label: str,
        entity_ticker: str | None = None,
        sector: str | None = None,
        now_iso: str | None = None,
        limit: int = 15,
    ) -> list[NewsArticleRecord]:
        """Parse RSS 2.0 XML string into standard NewsArticleRecord items."""
        now_ts = now_iso or datetime.now(timezone.utc).isoformat()
        articles: list[NewsArticleRecord] = []

        try:
            root = ET.fromstring(xml_content)
        except ET.ParseError as err:
            logger.warning("Failed parsing RSS XML: %s", err)
            return []

        items = root.findall(".//item")
        for item in items[:limit]:
            title_elem = item.find("title")
            link_elem = item.find("link")
            pub_date_elem = item.find("pubDate")
            guid_elem = item.find("guid")
            desc_elem = item.find("description")

            title = clean_text(title_elem.text if title_elem is not None else "")
            link = (link_elem.text if link_elem is not None else "").strip()
            if not title or not link:
                continue

            raw_guid = guid_elem.text if guid_elem is not None else None
            if raw_guid:
                guid = raw_guid.strip()
            else:
                guid = hashlib.sha256(link.encode("utf-8")).hexdigest()[:32]

            pub_date = parse_rfc822_date(pub_date_elem.text if pub_date_elem is not None else None)
            summary = clean_text(desc_elem.text if desc_elem is not None else "")

            # If Google News has <source> tag
            source = source_label
            source_elem = item.find("source")
            if source_elem is not None and source_elem.text:
                source = source_elem.text.strip()

            articles.append(
                NewsArticleRecord(
                    guid=guid,
                    title=title,
                    link=link,
                    published_at=pub_date,
                    source=source,
                    summary=summary[:300] if summary else None,
                    entity_ticker=entity_ticker,
                    sector=sector,
                    fetched_at=now_ts,
                )
            )

        return articles
