# MacroScope — Open Macroeconomic & Market Intelligence Dashboard

## 1. Project Vision & Scope

MacroScope is a local-first, open-source web application for exploring macroeconomic indicators, company relationships, and market intelligence using **100% keyless, unauthenticated public data endpoints**.

The platform is structured around **three interconnected views**:
1. **Macro View:** Global & country-level macroeconomic indicators (GDP growth, CPI inflation, policy rates, unemployment, loan default proxies, vehicle registrations, and global benchmark oil prices).
2. **Micro View:** Deep-dive into an individual company: company fundamentals (SEC EDGAR), financial ratios, alongside relevant country-level macro and sector trends.
3. **Graph View (Interactive Company & Sector Network):**
   - An interactive network graph of companies clustered by sector and linked by direct competitor and sector-peer relationships.
   - Clicking on a company node opens an inspection panel:
     - **Iteration 1 (Current Focus):** Aggregates contextual, real-time news headlines extracted from public RSS feeds matching the selected company, its direct competitors, and its broader sector.
     - **Iteration 2:** Seamlessly transitions into the full Micro fundamental view.

---

## 2. Architecture & Data Caching Strategy

### Hybrid Read-Through Cache (SQLite + On-Demand Fetch)
To eliminate latency, prevent rate-limiting, and run completely offline or as a zero-cost public demo:

1. **Persisted Company Graph & Sector Knowledge Base:**
   - A curated SQLite dataset of major public companies across strategic sectors (Tech, Semiconductors, Energy, Financials, Auto, Healthcare, Consumer).
   - Stored directly in `macroscope.db` (version-controlled and bundled in the repository).
2. **Historical Macroeconomic Time-Series (`TTL = 30 days`):**
   - Annual and quarterly macro series persisted in SQLite upon first request. Subsequent queries serve in <10ms.
3. **Rolling Macro & Commodity Releases (`TTL = 24 hours` / `1 hour`):**
   - Monthly unemployment and CPI prints refresh on a 24-hour TTL; daily benchmark oil prices (Brent/WTI) refresh on a 1-hour TTL.
4. **Contextual RSS News Cache (`TTL = 15 - 30 minutes`):**
   - Public company, competitor, and sector RSS feeds are fetched and cached in SQLite with a 30-minute TTL to maintain responsiveness without hammering feed providers.
5. **Public Demo Mode (`READ_ONLY_CACHE=false` by default):**
   - When set to `true`, serves cached SQLite data and suppresses external requests so public visitors cannot trigger upstream rate limits or IP bans.

---

## 3. Keyless Data Sources (Zero-Auth Adapters)

All data providers follow the pluggable `BaseDataProvider` / `MacroProvider` interface and normalize data into unified schemas.

| Domain | Primary Keyless Source | Endpoint / Mechanism | Coverage |
| :--- | :--- | :--- | :--- |
| **Company Graph & Competitor DB** | **Local Curated SQLite DB** | Bundled in repository (`macroscope.db`) | 50+ bellwether companies across 7 sectors + competitor edges |
| **Contextual Company & Sector News** | **Public Financial RSS Feeds** | Yahoo Finance RSS (`https://feeds.finance.yahoo.com/rss/2.0/headline?s={TICKER}`), Google News RSS, Reuters, CNBC RSS | Company ticker, competitor names, and sector keyword feeds |
| **Core Global Macro** | **World Bank Open Data API v2** | `https://api.worldbank.org/v2/country/{iso3}/indicator/{code}?format=json` | 200+ countries (annual) |
| **US Macro & Commodities** | **FRED Public CSV Download** | `https://fred.stlouisfed.org/graph/fredgraph.csv?id={SERIES_ID}` | Daily oil prices, monthly US CPI/Unemployment/Auto Sales |
| **Micro Financials (v2)** | **SEC EDGAR Company Facts API** | `https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json` (User-Agent auth only) | US public companies (10-K, 10-Q) |

---

## 4. Tech Stack & Directory Structure

### Stack
- **Backend:** Python 3.11+, FastAPI, SQLite (`aiosqlite`), `httpx`, `feedparser` (for RSS XML parsing).
- **Frontend:** React 19, TypeScript, Vite, Tailwind CSS, TanStack Query, Recharts, Cytoscape.js / React Flow / SVG Force Graph (for the interactive network graph), Lucide React.
- **Repository Structure:**
```text
macroscope/
├── AGENTS.md                  # Isolation rules, strict TypeScript, pytest requirements
├── ARCHITECTURE.md            # High-level architecture and specification
├── Makefile                   # make dev, make test, make seed
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint, CORS, lifespan DB init
│   │   ├── config.py          # Settings (DB path, TTLs, READ_ONLY_CACHE)
│   │   ├── db/
│   │   │   ├── database.py    # SQLite connection, queries, schema init
│   │   │   └── models.py      # SQLite records (observations, companies, competitors, news)
│   │   ├── providers/
│   │   │   ├── base.py        # BaseDataProvider abstract class
│   │   │   ├── world_bank.py  # World Bank JSON adapter
│   │   │   ├── fred_csv.py    # Keyless FRED CSV adapter
│   │   │   ├── rss_news.py    # Keyless RSS news aggregator for companies/sectors
│   │   │   └── registry.py    # Dynamic provider lookup & registration
│   │   ├── services/
│   │   │   ├── cache_manager.py # Read-through cache logic & TTL enforcement
│   │   │   ├── company_graph.py # Graph queries (nodes, edges, competitor clusters)
│   │   │   └── seed.py        # Pre-warms database with graph + macro data
│   │   ├── schemas/
│   │   │   ├── macro.py       # Pydantic schemas for macro API
│   │   │   └── graph.py       # Pydantic schemas for Graph & News API
│   │   └── api/
│   │       ├── routes.py      # Macro endpoints
│   │       └── graph_routes.py# Graph & News endpoints
│   ├── tests/                 # 100% offline mocked pytest suite
│   │   ├── fixtures/
│   │   └── test_*.py
│   ├── pytest.ini
│   └── requirements.txt
└── frontend/                  # React 19 + TypeScript SPA
```

---

## 5. SQLite Database Schema

```sql
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

-- 2. Companies & Sector Graph Dataset
CREATE TABLE IF NOT EXISTS companies (
    ticker TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    sector TEXT NOT NULL,              -- e.g. 'Technology', 'Energy', 'Automotive', 'Financials'
    industry TEXT NOT NULL,            -- e.g. 'Semiconductors', 'Oil & Gas Integrated'
    country_code TEXT NOT NULL DEFAULT 'USA',
    market_cap_tier TEXT,              -- 'Mega', 'Large', 'Mid'
    description TEXT
);

CREATE TABLE IF NOT EXISTS company_competitors (
    company_ticker TEXT NOT NULL,
    competitor_ticker TEXT NOT NULL,
    relationship_type TEXT NOT NULL DEFAULT 'direct_competitor', -- 'direct_competitor', 'sector_peer'
    weight REAL DEFAULT 1.0,
    PRIMARY KEY (company_ticker, competitor_ticker),
    FOREIGN KEY (company_ticker) REFERENCES companies(ticker),
    FOREIGN KEY (competitor_ticker) REFERENCES companies(ticker)
);

-- 3. Cached RSS News Feed
CREATE TABLE IF NOT EXISTS news_articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    guid TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    link TEXT NOT NULL,
    published_at TEXT NOT NULL,        -- ISO-8601 string
    source TEXT NOT NULL,              -- e.g. 'Yahoo Finance', 'Reuters', 'CNBC'
    summary TEXT,
    entity_ticker TEXT,                -- Target ticker if company-specific
    sector TEXT,                       -- Target sector if sector-wide
    fetched_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_news_entity 
ON news_articles(entity_ticker, published_at DESC);

CREATE INDEX IF NOT EXISTS idx_news_sector 
ON news_articles(sector, published_at DESC);
```

---

## 6. REST API Specification

### Macro Endpoints (`/api/v1/`)
- `GET /api/v1/health` — System status, DB connectivity, and cached observation counts.
- `GET /api/v1/countries` — List of supported economies, metadata, and indicator coverage.
- `GET /api/v1/dashboard/{country_code}` — KPI snapshots + historical time-series for a country.
- `GET /api/v1/compare?countries=USA,GBR,DEU&indicator=inflation_cpi` — Cross-country aligned time series.
- `POST /api/v1/refresh/{country_code}` — Forces cache invalidation and upstream refresh.

### Graph & Company News Endpoints (`/api/v1/`)
- `GET /api/v1/graph`
  - Returns the complete company network graph payload:
    - `nodes`: `[{ ticker, name, sector, industry, country_code, market_cap_tier, competitor_count }]`
    - `edges`: `[{ source, target, relationship_type, weight }]`
    - `sectors`: List of distinct sectors for frontend filtering.
- `GET /api/v1/companies`
  - List of companies with sector and competitor count metadata (supports `?sector=Technology`).
- `GET /api/v1/companies/{ticker}`
  - Returns single company details, direct competitors list, and sector peers.
- `GET /api/v1/companies/{ticker}/news`
  - Returns contextual news stream segmented into:
    - `company_news`: Headlines directly referencing `{ticker}`.
    - `competitor_news`: Headlines from its direct competitors.
    - `sector_news`: Broader sector and industry headlines.
  - Automatically fetches keyless RSS feeds on miss or TTL expiration (>30 mins).

---

## 7. Frontend User Experience (3 Core Views)

1. **Navigation Bar:**
   - Tabs: **Macro**, **Micro (v2)**, and **Company Graph**.
   - Sector / Country quick-search and data freshness status badge.

2. **Graph View (Interactive Network & Contextual News Drawer):**
   - **Canvas Area:** Force-directed network diagram:
     - Nodes colored by sector (e.g. Blue = Tech, Green = Energy, Orange = Auto, Purple = Financials).
     - Node size scaled by market cap tier or competitor degree.
     - Edges represent competitor rivalries (solid line) or sector peer linkages (dashed line).
     - Sector filter pills at the top (e.g. *All*, *Technology*, *Energy*, *Automotive*, *Financials*).
   - **Contextual Side Drawer (Triggered by Clicking a Node):**
     - Company header with Ticker, Name, Sector, and Industry badge.
     - **Direct Competitors Chip Bar:** Clickable chips linking directly to competitor nodes in the graph.
     - **Contextual News Feed (3 Tabs/Sections):**
       1. **Company News:** Latest updates and earnings releases for the selected firm.
       2. **Competitor News:** Recent developments across its rivals (e.g., if AAPL is selected, shows MSFT, GOOGL, NVDA headlines).
       3. **Sector Trends:** Macroeconomic and industry-wide news for that sector.
     - "Open Micro View" action button (prepared for v2 company fundamentals).

---

## 8. Implementation Roadmap

- [x] **Phase 1: Backend Core & Keyless Adapters** — FastAPI, SQLite database engine, `BaseDataProvider` contract, World Bank JSON adapter, keyless FRED CSV adapter, 100% offline pytest suite.
- [x] **Phase 2: Cache Manager & REST API** — Read-through caching with tiered TTLs, graceful fallback on error, seed CLI, `/api/v1/countries`, `/dashboard`, `/compare`, `/refresh`.
- [ ] **Phase 3A: Graph Dataset & RSS News Engine (Current Focus)**
  1. Populate persisted `companies` and `company_competitors` seed dataset in SQLite with 50+ key companies across Tech, Energy, Auto, Financials, Healthcare, Consumer, and Telecom.
  2. Implement zero-auth `RssNewsProvider` (Yahoo Finance RSS + Google News RSS) parsing articles via `feedparser` / XML parser.
  3. Implement `company_graph.py` service and `/api/v1/graph`, `/api/v1/companies/{ticker}`, `/api/v1/companies/{ticker}/news` endpoints with 30-minute read-through cache.
  4. Write pytest suite with mocked RSS XML fixtures verifying graph extraction and news categorization (Company vs. Competitor vs. Sector).
- [ ] **Phase 3B: Frontend Scaffold & Graph View UI**
  1. Scaffold Vite + React 19 + TypeScript + Tailwind CSS.
  2. Implement interactive Canvas graph (force-directed network with node clustering and sector filters).
  3. Implement Contextual News Drawer with tabbed company, competitor, and sector feeds.
  4. Connect Macro Dashboard tab with Recharts time-series and country comparisons.
- [ ] **Phase 4: Micro View (SEC EDGAR) & Polish**
  1. Keyless SEC EDGAR Company Facts adapter for revenue, margins, and ratios.
  2. Integrated Micro Tab.
  3. Production build, Dockerfile, and GitHub repo polish.
