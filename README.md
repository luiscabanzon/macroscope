# MacroScope — Open Macro & Market Intelligence

MacroScope is an open-source, local-first web application for exploring macroeconomic time series, company competitor networks, and market intelligence using **100% keyless, unauthenticated public data endpoints**.

Runs out-of-the-box locally with zero API keys or `.env` secrets required.

---

## Three Core Views

1. **Company Competitor Graph:** Interactive force-directed network diagram clustering 74 S&P 500 and NASDAQ 100 bellwethers across all 11 GICS sectors, interconnected by 160 competitor relationship edges. Clicking any company opens a drawer with direct rival shortcuts and a 3-way partitioned contextual RSS news stream (**Company News**, **Competitor News**, and **Sector Trends**).
2. **Macro Dashboard:** Country-level macroeconomic indicators (GDP growth, CPI inflation, policy rates, unemployment, loan default proxies, vehicle sales demand proxies, and Brent crude oil benchmark) with interactive Recharts time series and side-by-side G7 comparison charts.
3. **Micro View (v2 Preview):** Company fundamentals deep-dive matching SEC EDGAR financial statements with sector and macro trends.

---

## Tech Stack & Architecture

- **Backend:** Python 3.11+, FastAPI, SQLite (`aiosqlite`) read-through cache with tiered TTLs (30d historical, 24h monthly, 1h commodity, 30m news), pluggable `BaseDataProvider` interface.
- **Frontend:** React 19, TypeScript (strict mode, zero `any`), Vite, Tailwind CSS, TanStack Query v5, Recharts, `d3-force`.
- **Testing:** 100% offline, deterministic Pytest suite mock-intercepting all outbound HTTP/XML/JSON requests via `respx`.

---

## Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ and `npm`

### Installation & Test

```bash
# 1. Install dependencies
make install

# 2. Run backend & frontend tests (100% offline)
make test
```

### Running Locally

```bash
# Terminal 1: Start FastAPI backend (http://127.0.0.1:8000)
make dev

# Terminal 2: Start Vite frontend (http://127.0.0.1:5173)
make dev-frontend
```

Open **[http://localhost:5173](http://localhost:5173)** in your browser.
Open **[http://localhost:8000/docs](http://localhost:8000/docs)** to explore interactive OpenAPI docs.

---

## Repository Structure

```text
macroscope/
├── AGENTS.md                  # Development boundaries & strict guardrails
├── ARCHITECTURE.md            # System architecture & execution spec
├── README.md                  # Project overview & quickstart
├── Makefile                   # make dev, make dev-frontend, make test, make seed
├── backend/
│   ├── app/
│   │   ├── main.py            # FastAPI entrypoint & auto-seeding lifespan
│   │   ├── config.py          # Settings & TTL configuration
│   │   ├── data/              # Embedded seed datasets (NASDAQ 100/S&P 500 & News)
│   │   ├── db/                # SQLite async engine & schema models
│   │   ├── providers/         # Zero-auth adapters (World Bank, FRED CSV, RSS)
│   │   ├── services/          # CacheManager & CompanyGraphService
│   │   ├── schemas/           # Pydantic API response models
│   │   └── api/               # Macro & Graph REST endpoints
│   ├── tests/                 # 100% offline Pytest suite with realistic fixtures
│   ├── requirements.txt
│   └── pytest.ini
└── frontend/
    ├── src/
    │   ├── api/               # Typed client & TanStack Query hooks
    │   ├── components/        # GraphCanvas, GraphControls, NewsDrawer, Navigation
    │   ├── pages/             # GraphPage, MacroPage, MicroPage
    │   └── types/             # Strict TypeScript contracts
    ├── package.json
    └── vite.config.ts
```
