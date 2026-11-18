import aiosqlite
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncGenerator

from app.config import settings
from app.db.models import (
    CompanyRecord,
    CompetitorRecord,
    FetchLogRecord,
    NewsArticleRecord,
    ObservationRecord,
    SupplyChainRecord,
)

INIT_SQL = """
-- 1. Macro Time-Series Observations
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    country_code TEXT NOT NULL,
    indicator_slug TEXT NOT NULL,
    period_date TEXT NOT NULL,
    frequency TEXT NOT NULL,
    value REAL NOT NULL,
    unit TEXT NOT NULL,
    source TEXT NOT NULL,
    UNIQUE(country_code, indicator_slug, period_date, source)
);

CREATE INDEX IF NOT EXISTS idx_obs_lookup 
ON observations(country_code, indicator_slug, period_date);

CREATE TABLE IF NOT EXISTS fetch_log (
    country_code TEXT NOT NULL,
    indicator_slug TEXT NOT NULL,
    last_fetched_at TEXT NOT NULL,
    status TEXT NOT NULL,
    error_message TEXT,
    PRIMARY KEY (country_code, indicator_slug)
);

-- 2. Companies & Competitors Network
CREATE TABLE IF NOT EXISTS companies (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT NOT NULL,
    industry TEXT NOT NULL,
    country_code TEXT NOT NULL DEFAULT 'USA',
    market_cap_tier TEXT DEFAULT 'Large',
    description TEXT
);

CREATE INDEX IF NOT EXISTS idx_companies_sector ON companies(sector);

CREATE TABLE IF NOT EXISTS company_competitors (
    company_ticker TEXT NOT NULL,
    competitor_ticker TEXT NOT NULL,
    relationship_type TEXT NOT NULL DEFAULT 'direct_competitor',
    weight REAL DEFAULT 1.0,
    PRIMARY KEY (company_ticker, competitor_ticker),
    FOREIGN KEY (company_ticker) REFERENCES companies(ticker),
    FOREIGN KEY (competitor_ticker) REFERENCES companies(ticker)
);

CREATE INDEX IF NOT EXISTS idx_comp_lookup ON company_competitors(company_ticker);

-- 3. Company Supply Chain & Customer-Supplier Linkages
CREATE TABLE IF NOT EXISTS company_supply_chain (
    supplier_ticker TEXT NOT NULL,
    customer_ticker TEXT NOT NULL,
    product_category TEXT NOT NULL,
    tier_or_importance TEXT NOT NULL DEFAULT 'critical',
    weight REAL DEFAULT 1.0,
    PRIMARY KEY (supplier_ticker, customer_ticker),
    FOREIGN KEY (supplier_ticker) REFERENCES companies(ticker),
    FOREIGN KEY (customer_ticker) REFERENCES companies(ticker)
);

CREATE INDEX IF NOT EXISTS idx_supply_supplier ON company_supply_chain(supplier_ticker);
CREATE INDEX IF NOT EXISTS idx_supply_customer ON company_supply_chain(customer_ticker);

-- 4. Cached Public RSS News Articles
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    published_at TEXT NOT NULL,
    source TEXT NOT NULL,
    summary TEXT,
    entity_ticker TEXT,
    sector TEXT,
    fetched_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_news_entity ON news_articles(entity_ticker, published_at DESC);
CREATE INDEX IF NOT EXISTS idx_news_sector ON news_articles(sector, published_at DESC);
"""


@asynccontextmanager
async def get_connection(db_path: str | None = None) -> AsyncGenerator[aiosqlite.Connection, None]:
    """Yield an async SQLite database connection with row factory enabled."""
    target_path = db_path or settings.db_path
    async with aiosqlite.connect(target_path) as conn:
        conn.row_factory = aiosqlite.Row
        await conn.execute("PRAGMA journal_mode=WAL;")
        await conn.execute("PRAGMA synchronous=NORMAL;")
        await conn.execute("PRAGMA foreign_keys=ON;")
        yield conn


async def init_db(db_path: str | None = None) -> None:
    """Initialize SQLite tables and indexes."""
    async with get_connection(db_path) as conn:
        await conn.executescript(INIT_SQL)
        await conn.commit()


# ==========================================
# Macro Time-Series Operations
# ==========================================

async def upsert_observations(
    conn: aiosqlite.Connection,
    observations: list[ObservationRecord],
) -> int:
    """Batch upsert observations into SQLite."""
    if not observations:
        return 0

    query = """
    INSERT INTO observations (
        country_code, indicator_slug, period_date, frequency, value, unit, source
    ) VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(country_code, indicator_slug, period_date, source) DO UPDATE SET
        value = excluded.value,
        frequency = excluded.frequency,
        unit = excluded.unit;
    """
    params = [
        (
            obs.country_code,
            obs.indicator_slug,
            obs.period_date,
            obs.frequency,
            obs.value,
            obs.unit,
            obs.source,
        )
        for obs in observations
    ]
    await conn.executemany(query, params)
    await conn.commit()
    return len(params)


async def query_observations(
    conn: aiosqlite.Connection,
    country_code: str,
    indicator_slug: str,
    start_date: str | None = None,
    end_date: str | None = None,
) -> list[ObservationRecord]:
    """Query ordered observations for an entity and indicator."""
    query = """
    SELECT id, country_code, indicator_slug, period_date, frequency, value, unit, source
    FROM observations
    WHERE country_code = ? AND indicator_slug = ?
    """
    params: list[str] = [country_code, indicator_slug]

    if start_date:
        query += " AND period_date >= ?"
        params.append(start_date)
    if end_date:
        query += " AND period_date <= ?"
        params.append(end_date)

    query += " ORDER BY period_date ASC"

    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [
            ObservationRecord(
                id=row["id"],
                country_code=row["country_code"],
                indicator_slug=row["indicator_slug"],
                period_date=row["period_date"],
                frequency=row["frequency"],
                value=float(row["value"]),
                unit=row["unit"],
                source=row["source"],
            )
            for row in rows
        ]


async def query_multi_country_observations(
    conn: aiosqlite.Connection,
    country_codes: list[str],
    indicator_slug: str,
    start_date: str | None = None,
) -> list[ObservationRecord]:
    """Query observations across multiple countries for comparative analysis."""
    if not country_codes:
        return []

    placeholders = ",".join("?" for _ in country_codes)
    query = f"""
    SELECT id, country_code, indicator_slug, period_date, frequency, value, unit, source
    FROM observations
    WHERE country_code IN ({placeholders}) AND indicator_slug = ?
    """
    params = list(country_codes) + [indicator_slug]

    if start_date:
        query += " AND period_date >= ?"
        params.append(start_date)

    query += " ORDER BY period_date ASC, country_code ASC"

    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [
            ObservationRecord(
                id=row["id"],
                country_code=row["country_code"],
                indicator_slug=row["indicator_slug"],
                period_date=row["period_date"],
                frequency=row["frequency"],
                value=float(row["value"]),
                unit=row["unit"],
                source=row["source"],
            )
            for row in rows
        ]


async def get_fetch_log(
    conn: aiosqlite.Connection,
    country_code: str,
    indicator_slug: str,
) -> FetchLogRecord | None:
    """Retrieve the latest fetch log for an entity and indicator."""
    query = """
    SELECT country_code, indicator_slug, last_fetched_at, status, error_message
    FROM fetch_log
    WHERE country_code = ? AND indicator_slug = ?
    """
    async with conn.execute(query, (country_code, indicator_slug)) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return FetchLogRecord(
            country_code=row["country_code"],
            indicator_slug=row["indicator_slug"],
            last_fetched_at=row["last_fetched_at"],
            status=row["status"],
            error_message=row["error_message"],
        )


async def set_fetch_log(
    conn: aiosqlite.Connection,
    country_code: str,
    indicator_slug: str,
    status: str,
    last_fetched_at: str | None = None,
    error_message: str | None = None,
) -> None:
    """Update or insert the fetch log record."""
    fetched_at = last_fetched_at or datetime.now(timezone.utc).isoformat()
    query = """
    INSERT INTO fetch_log (country_code, indicator_slug, last_fetched_at, status, error_message)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(country_code, indicator_slug) DO UPDATE SET
        last_fetched_at = excluded.last_fetched_at,
        status = excluded.status,
        error_message = excluded.error_message;
    """
    await conn.execute(query, (country_code, indicator_slug, fetched_at, status, error_message))
    await conn.commit()


# ==========================================
# Company & Competitor Graph Operations
# ==========================================

async def upsert_companies(
    conn: aiosqlite.Connection,
    companies: list[CompanyRecord],
) -> int:
    """Batch insert or update companies."""
    if not companies:
        return 0

    query = """
    INSERT INTO companies (ticker, name, sector, industry, country_code, market_cap_tier, description)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(ticker) DO UPDATE SET
        name = excluded.name,
        sector = excluded.sector,
        industry = excluded.industry,
        country_code = excluded.country_code,
        market_cap_tier = excluded.market_cap_tier,
        description = excluded.description;
    """
    params = [
        (c.ticker, c.name, c.sector, c.industry, c.country_code, c.market_cap_tier, c.description)
        for c in companies
    ]
    await conn.executemany(query, params)
    await conn.commit()
    return len(params)


async def upsert_competitors(
    conn: aiosqlite.Connection,
    competitors: list[CompetitorRecord],
) -> int:
    """Batch insert or update competitor relationship edges."""
    if not competitors:
        return 0

    query = """
    INSERT INTO company_competitors (company_ticker, competitor_ticker, relationship_type, weight)
    VALUES (?, ?, ?, ?)
    ON CONFLICT(company_ticker, competitor_ticker) DO UPDATE SET
        relationship_type = excluded.relationship_type,
        weight = excluded.weight;
    """
    params = [
        (c.company_ticker, c.competitor_ticker, c.relationship_type, c.weight)
        for c in competitors
    ]
    await conn.executemany(query, params)
    await conn.commit()
    return len(params)


async def upsert_supply_chain(
    conn: aiosqlite.Connection,
    links: list[SupplyChainRecord],
) -> int:
    """Batch insert or update company supply chain linkages."""
    if not links:
        return 0

    query = """
    INSERT INTO company_supply_chain (supplier_ticker, customer_ticker, product_category, tier_or_importance, weight)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(supplier_ticker, customer_ticker) DO UPDATE SET
        product_category = excluded.product_category,
        tier_or_importance = excluded.tier_or_importance,
        weight = excluded.weight;
    """
    params = [
        (s.supplier_ticker, s.customer_ticker, s.product_category, s.tier_or_importance, s.weight)
        for s in links
    ]
    await conn.executemany(query, params)
    await conn.commit()
    return len(params)


async def query_companies(
    conn: aiosqlite.Connection,
    sector: str | None = None,
) -> list[CompanyRecord]:
    """Retrieve companies, optionally filtered by sector."""
    query = "SELECT ticker, name, sector, industry, country_code, market_cap_tier, description FROM companies"
    params: list[str] = []
    if sector:
        query += " WHERE sector = ?"
        params.append(sector)
    query += " ORDER BY name ASC"

    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [
            CompanyRecord(
                ticker=r["ticker"],
                name=r["name"],
                sector=r["sector"],
                industry=r["industry"],
                country_code=r["country_code"],
                market_cap_tier=r["market_cap_tier"],
                description=r["description"],
            )
            for r in rows
        ]


async def get_company_by_ticker(
    conn: aiosqlite.Connection,
    ticker: str,
) -> CompanyRecord | None:
    """Retrieve a single company by ticker."""
    query = """
    SELECT ticker, name, sector, industry, country_code, market_cap_tier, description
    FROM companies WHERE ticker = ?
    """
    async with conn.execute(query, (ticker.upper(),)) as cursor:
        row = await cursor.fetchone()
        if not row:
            return None
        return CompanyRecord(
            ticker=row["ticker"],
            name=row["name"],
            sector=row["sector"],
            industry=row["industry"],
            country_code=row["country_code"],
            market_cap_tier=row["market_cap_tier"],
            description=row["description"],
        )


async def get_company_competitors(
    conn: aiosqlite.Connection,
    ticker: str,
) -> list[tuple[CompanyRecord, str, float]]:
    """Retrieve all competitors of a company with relationship details."""
    query = """
    SELECT c.ticker, c.name, c.sector, c.industry, c.country_code, c.market_cap_tier, c.description,
           cc.relationship_type, cc.weight
    FROM company_competitors cc
    JOIN companies c ON cc.competitor_ticker = c.ticker
    WHERE cc.company_ticker = ?
    ORDER BY cc.weight DESC, c.name ASC
    """
    async with conn.execute(query, (ticker.upper(),)) as cursor:
        rows = await cursor.fetchall()
        return [
            (
                CompanyRecord(
                    ticker=r["ticker"],
                    name=r["name"],
                    sector=r["sector"],
                    industry=r["industry"],
                    country_code=r["country_code"],
                    market_cap_tier=r["market_cap_tier"],
                    description=r["description"],
                ),
                r["relationship_type"],
                float(r["weight"]),
            )
            for r in rows
        ]


async def get_company_supply_chain(
    conn: aiosqlite.Connection,
    ticker: str,
) -> dict[str, list[dict]]:
    """Retrieve all upstream suppliers and downstream customers for a company."""
    clean_ticker = ticker.upper()

    # 1. Upstream Suppliers (who supplies this company: customer_ticker = clean_ticker)
    supplier_query = """
    SELECT c.ticker, c.name, c.sector, c.industry, c.country_code, c.market_cap_tier, c.description,
           sc.product_category, sc.tier_or_importance, sc.weight
    FROM company_supply_chain sc
    JOIN companies c ON sc.supplier_ticker = c.ticker
    WHERE sc.customer_ticker = ?
    ORDER BY sc.weight DESC, c.name ASC
    """
    suppliers: list[dict] = []
    async with conn.execute(supplier_query, (clean_ticker,)) as cursor:
        rows = await cursor.fetchall()
        for r in rows:
            suppliers.append({
                "ticker": r["ticker"],
                "name": r["name"],
                "sector": r["sector"],
                "industry": r["industry"],
                "country_code": r["country_code"],
                "market_cap_tier": r["market_cap_tier"],
                "description": r["description"],
                "product_category": r["product_category"],
                "tier_or_importance": r["tier_or_importance"],
                "weight": float(r["weight"]),
                "role": "supplier",
            })

    # 2. Downstream Customers (who buys from this company: supplier_ticker = clean_ticker)
    customer_query = """
    SELECT c.ticker, c.name, c.sector, c.industry, c.country_code, c.market_cap_tier, c.description,
           sc.product_category, sc.tier_or_importance, sc.weight
    FROM company_supply_chain sc
    JOIN companies c ON sc.customer_ticker = c.ticker
    WHERE sc.supplier_ticker = ?
    ORDER BY sc.weight DESC, c.name ASC
    """
    customers: list[dict] = []
    async with conn.execute(customer_query, (clean_ticker,)) as cursor:
        rows = await cursor.fetchall()
        for r in rows:
            customers.append({
                "ticker": r["ticker"],
                "name": r["name"],
                "sector": r["sector"],
                "industry": r["industry"],
                "country_code": r["country_code"],
                "market_cap_tier": r["market_cap_tier"],
                "description": r["description"],
                "product_category": r["product_category"],
                "tier_or_importance": r["tier_or_importance"],
                "weight": float(r["weight"]),
                "role": "customer",
            })

    return {"suppliers": suppliers, "customers": customers}


async def get_graph_elements(
    conn: aiosqlite.Connection,
    sector: str | None = None,
    network_type: str = "all",
) -> tuple[list[dict], list[dict], list[str]]:
    """Retrieve graph nodes and edges with competitor and supply chain counts."""
    # 1. Fetch distinct sectors
    async with conn.execute("SELECT DISTINCT sector FROM companies ORDER BY sector ASC") as cursor:
        sector_rows = await cursor.fetchall()
        sectors = [r["sector"] for r in sector_rows]

    # 2. Fetch nodes with competitor and supply chain connection counts
    node_query = """
    SELECT c.ticker, c.name, c.sector, c.industry, c.country_code, c.market_cap_tier, c.description,
           count(DISTINCT cc.competitor_ticker) as competitor_count,
           count(DISTINCT sc_supp.supplier_ticker) as supplier_count,
           count(DISTINCT sc_cust.customer_ticker) as customer_count
    FROM companies c
    LEFT JOIN company_competitors cc ON c.ticker = cc.company_ticker
    LEFT JOIN company_supply_chain sc_supp ON c.ticker = sc_supp.customer_ticker
    LEFT JOIN company_supply_chain sc_cust ON c.ticker = sc_cust.supplier_ticker
    """
    params: list[str] = []
    if sector:
        node_query += " WHERE c.sector = ?"
        params.append(sector)

    node_query += " GROUP BY c.ticker ORDER BY c.market_cap_tier DESC, c.name ASC"

    async with conn.execute(node_query, params) as cursor:
        node_rows = await cursor.fetchall()
        nodes = [
            {
                "ticker": r["ticker"],
                "name": r["name"],
                "sector": r["sector"],
                "industry": r["industry"],
                "country_code": r["country_code"],
                "market_cap_tier": r["market_cap_tier"],
                "competitor_count": int(r["competitor_count"]),
                "supplier_count": int(r["supplier_count"]),
                "customer_count": int(r["customer_count"]),
                "description": r["description"],
            }
            for r in node_rows
        ]

    included_tickers = {n["ticker"] for n in nodes}
    edges: list[dict] = []

    # 3. Fetch competitor rivalry edges
    if network_type in ("all", "competition"):
        edge_query = """
        SELECT company_ticker, competitor_ticker, relationship_type, weight
        FROM company_competitors
        """
        async with conn.execute(edge_query) as cursor:
            edge_rows = await cursor.fetchall()
            for r in edge_rows:
                if r["company_ticker"] in included_tickers and r["competitor_ticker"] in included_tickers:
                    edges.append({
                        "source": r["company_ticker"],
                        "target": r["competitor_ticker"],
                        "relationship_type": r["relationship_type"],
                        "weight": float(r["weight"]),
                        "is_directed": False,
                        "relationship_category": "competition",
                    })

    # 4. Fetch supply chain dependency edges (supplier -> customer)
    if network_type in ("all", "supply_chain"):
        sc_query = """
        SELECT supplier_ticker, customer_ticker, product_category, tier_or_importance, weight
        FROM company_supply_chain
        """
        async with conn.execute(sc_query) as cursor:
            sc_rows = await cursor.fetchall()
            for r in sc_rows:
                if r["supplier_ticker"] in included_tickers and r["customer_ticker"] in included_tickers:
                    edges.append({
                        "source": r["supplier_ticker"],
                        "target": r["customer_ticker"],
                        "relationship_type": "supply_chain",
                        "product_category": r["product_category"],
                        "tier_or_importance": r["tier_or_importance"],
                        "weight": float(r["weight"]),
                        "is_directed": True,
                        "relationship_category": "supply_chain",
                    })

    return nodes, edges, sectors


# ==========================================
# News Cache Operations
# ==========================================

async def upsert_news_articles(
    conn: aiosqlite.Connection,
    articles: list[NewsArticleRecord],
) -> int:
    """Batch insert news articles, ignoring duplicates by GUID."""
    if not articles:
        return 0

    query = """
    INSERT INTO news_articles (guid, title, link, published_at, source, summary, entity_ticker, sector, fetched_at)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(guid) DO UPDATE SET
        title = excluded.title,
        link = excluded.link,
        summary = excluded.summary,
        entity_ticker = COALESCE(excluded.entity_ticker, news_articles.entity_ticker),
        sector = COALESCE(excluded.sector, news_articles.sector),
        fetched_at = excluded.fetched_at;
    """
    params = [
        (
            a.guid,
            a.title,
            a.link,
            a.published_at,
            a.source,
            a.summary,
            a.entity_ticker,
            a.sector,
            a.fetched_at,
        )
        for a in articles
    ]
    await conn.executemany(query, params)
    await conn.commit()
    return len(params)


async def upsert_supply_chain(
    conn: aiosqlite.Connection,
    links: list[SupplyChainRecord],
) -> int:
    """Batch insert or update company supply chain linkages."""
    if not links:
        return 0

    query = """
    INSERT INTO company_supply_chain (supplier_ticker, customer_ticker, product_category, tier_or_importance, weight)
    VALUES (?, ?, ?, ?, ?)
    ON CONFLICT(supplier_ticker, customer_ticker) DO UPDATE SET
        product_category = excluded.product_category,
        tier_or_importance = excluded.tier_or_importance,
        weight = excluded.weight;
    """
    params = [
        (s.supplier_ticker, s.customer_ticker, s.product_category, s.tier_or_importance, s.weight)
        for s in links
    ]
    await conn.executemany(query, params)
    await conn.commit()
    return len(params)


async def query_news_articles(
    conn: aiosqlite.Connection,
    entity_ticker: str | None = None,
    sector: str | None = None,
    limit: int = 20,
) -> list[NewsArticleRecord]:
    """Retrieve cached news articles by ticker or sector."""
    query = """
    SELECT id, guid, title, link, published_at, source, summary, entity_ticker, sector, fetched_at
    FROM news_articles
    """
    params: list[str | int] = []
    clauses: list[str] = []

    if entity_ticker:
        clauses.append("entity_ticker = ?")
        params.append(entity_ticker.upper())
    if sector:
        clauses.append("sector = ?")
        params.append(sector)

    if clauses:
        query += " WHERE " + " OR ".join(clauses)

    query += " ORDER BY published_at DESC LIMIT ?"
    params.append(limit)

    async with conn.execute(query, params) as cursor:
        rows = await cursor.fetchall()
        return [
            NewsArticleRecord(
                id=r["id"],
                guid=r["guid"],
                title=r["title"],
                link=r["link"],
                published_at=r["published_at"],
                source=r["source"],
                summary=r["summary"],
                entity_ticker=r["entity_ticker"],
                sector=r["sector"],
                fetched_at=r["fetched_at"],
            )
            for r in rows
        ]
