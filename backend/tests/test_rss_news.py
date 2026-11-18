import pytest
import respx
from httpx import Response

from app.providers.rss_news import RssNewsProvider, clean_text, parse_rfc822_date


def test_clean_text_and_html_stripping():
    """Verify HTML cleanup and entity decoding."""
    raw = "<p>Apple &amp; Microsoft announced &quot;major&quot; updates &lt;today&gt;</p>"
    cleaned = clean_text(raw)
    assert cleaned == 'Apple & Microsoft announced "major" updates <today>'


def test_parse_rfc822_date():
    """Verify RFC 822 date to ISO conversion."""
    rfc_date = "Wed, 18 Nov 2026 09:30:00 +0000"
    iso_date = parse_rfc822_date(rfc_date)
    assert iso_date.startswith("2026-11-18T09:30:00")


@pytest.mark.asyncio
async def test_yahoo_finance_rss_parsing(load_fixture):
    """Verify parsing real Yahoo Finance RSS XML."""
    xml_content = load_fixture("yahoo_finance_rss.xml")
    provider = RssNewsProvider()

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get(
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            params={"s": "AAPL", "region": "US", "lang": "en-US"},
        ).mock(return_value=Response(200, text=xml_content))

        articles = await provider.fetch_company_news("AAPL")
        assert len(articles) == 2
        assert articles[0].entity_ticker == "AAPL"
        assert articles[0].guid == "yf-aapl-1001"
        assert "Apple Expands Enterprise AI Partnerships" in articles[0].title
        assert articles[0].source == "Yahoo Finance"
        assert "<p>" not in (articles[0].summary or "")


@pytest.mark.asyncio
async def test_google_news_rss_parsing(load_fixture):
    """Verify parsing Google News sector search XML."""
    xml_content = load_fixture("google_news_rss.xml")
    provider = RssNewsProvider()

    with respx.mock(assert_all_called=True) as respx_mock:
        respx_mock.get("https://news.google.com/rss/search").mock(return_value=Response(200, text=xml_content))

        articles = await provider.fetch_sector_news("Technology")
        assert len(articles) == 1
        assert articles[0].source == "Reuters"
        assert articles[0].sector == "Technology"
        assert "Semiconductor Fab Investments Accelerate" in articles[0].title
