# AGENTS.md — Development Guidelines & Agent Guardrails

Welcome to **MacroScope**. This document defines architectural boundaries, coding standards, testing requirements, and agent instructions. All autonomous agents and human contributors must strictly follow these rules.

---

## 1. Architectural Boundaries & Isolation

The repository is strictly partitioned into two decoupled halves: `backend/` and `frontend/`.

```text
macroscope/
├── backend/      # Python 3.11+ FastAPI service, SQLite cache, data adapters, pytest suite
├── frontend/     # React 19 + TypeScript + Vite SPA, Tailwind CSS, TanStack Query, Recharts
├── AGENTS.md     # This rulebook
├── ARCHITECTURE.md
└── Makefile
```

### Backend (`backend/`)
- **Single Responsibility:** Data extraction from keyless public providers, normalization into unified time-series formats, SQLite read-through caching with TTL enforcement, and serving typed JSON REST endpoints under `/api/v1/`.
- **Isolation Constraint:** Never import, execute, or reference frontend files, packages, or node modules. Backend must be fully operable, runnable, and testable via standard Python tooling (`uv`, `pip`, `pytest`) without `node` or `npm`.
- **Zero-Secret Philosophy:** Must run 100% keyless out-of-the-box. Never require API keys or secrets in `.env` for core functionality.

### Frontend (`frontend/`)
- **Single Responsibility:** Visual presentation, interactive charting (Recharts), country comparisons, and client-side caching/state (TanStack Query).
- **Isolation Constraint:** Frontend interacts with the backend **strictly via HTTP/JSON REST API**. Never import Python scripts, database models, or backend code.
- **Contract Enforcement:** All API response shapes must be explicitly typed in `frontend/src/types/macro.ts`, keeping an exact 1:1 mapping with FastAPI Pydantic response models.

---

## 2. Strict TypeScript Rules

To maintain high code quality and prevent runtime errors:

1. **Strict Compiler Options:**
   - `strict: true` must be enabled in `tsconfig.json`.
   - `noImplicitAny: true`, `strictNullChecks: true`, and `noUncheckedIndexedAccess: true`.
2. **Forbidden Patterns:**
   - **No `any`:** The use of `any` is strictly prohibited. Use `unknown` with runtime type narrowing or define explicit interfaces/unions.
   - **No Type Assertions Without Validation:** Avoid `as Type` assertions unless interfacing with third-party libraries that lack definitions. Prefer schema parsing or type guard predicates.
   - **No Untyped API Calls:** All API calls via `fetch` / `axios` / TanStack Query must have an explicit response type argument (e.g., `useQuery<DashboardResponse>`).
3. **Data Contracts:**
   - All shared API schemas must be defined in `frontend/src/types/macro.ts`.
   - Property names must match FastAPI camelCase / snake_case conventions (documented in `macro.ts`).
   - Dates must be represented as ISO-8601 strings (`YYYY-MM-DD` or full ISO).

---

## 3. Pytest & Backend Testing Requirements

High-confidence, reproducible testing is non-negotiable.

### 1. 100% Offline & Mocked Tests
- **Zero Real Network Calls:** Tests must never hit external endpoints (World Bank, FRED, ECB, RSS feeds). All outbound HTTP calls must be intercepted using `respx`, `pytest-mock`, or `unittest.mock`.
- **Fixtures Directory (`backend/tests/fixtures/`):** Store realistic sample payloads (World Bank JSON responses, FRED CSV extracts) to test parsers against real-world schema quirks (e.g. missing periods, empty values, irregular date formats).

### 2. Mandatory Test Coverage
Every phase and component must include dedicated pytest suites:
- **Provider Adapters:** Verify normalization of raw data into standard schema:
  - Proper date formatting (`YYYY-MM-DD` or year string normalization).
  - Accurate unit mapping (`%`, `USD/bbl`, etc.).
  - Resilient handling of `None`, empty strings, NaN, or malformed data points.
- **Database & Cache Layer:**
  - Verify SQLite schema initialization, table creation, and indexes.
  - Verify unique compound constraints (`country_code`, `indicator_slug`, `period_date`, `source`).
  - Read-through cache behavior:
    - Cache miss: queries provider, writes to SQLite, updates `fetch_log`.
    - Cache hit: serves directly from SQLite in <10ms without calling provider.
    - TTL expiration: re-fetches when stale.
- **Graceful Fallback & Resilience:**
  - If an upstream provider returns 5xx, 429, or times out, the cache manager must serve stale data from SQLite with a `stale: true` flag rather than throwing a 500 error.
- **REST Endpoints:** Test FastAPI status codes, error models, and payload validation.

### 3. Pytest Command
Run tests from the `backend/` directory or root Makefile:
```bash
pytest backend/tests/ -v --durations=10
```

---

## 4. Extensibility & Provider Interface (v1 Macro & v2 Micro Data)

To ensure seamless extensibility for v2 (e.g. SEC EDGAR company fundamentals, financial ratios, stock benchmarks), all data ingestion must adhere to the abstract provider contract:

1. **Provider Abstraction (`backend/app/providers/base.py`):**
   - Inherit from `BaseDataProvider` / `MacroProvider`.
   - Implement `async def fetch_series(self, indicator_slug: str, country_code: str, **kwargs) -> list[NormalizedObservation]`.
   - Implement `async def health_check(self) -> bool`.
2. **Unified Normalized Observation Model:**
   ```python
   class NormalizedObservation(BaseModel):
       country_code: str          # ISO-3 (e.g., 'USA', 'DEU') or 'WLD' / Ticker symbol in v2
       indicator_slug: str        # e.g., 'gdp_growth', 'inflation_cpi', 'oil_brent'
       period_date: str           # 'YYYY-MM-DD'
       frequency: str             # 'A' (Annual), 'Q' (Quarterly), 'M' (Monthly), 'D' (Daily)
       value: float
       unit: str                  # '%', 'USD/bbl', 'USD', etc.
       source: str                # 'World Bank', 'FRED', 'SEC EDGAR'
   ```
3. **Registry Pattern:** Adapters register their supported indicator slugs and country/entity capabilities. The `cache_manager` routes requests dynamically through the provider registry without hardcoding provider logic in route handlers.

---

## 5. Development Workflow & Change Approval

1. **Plan First:** Whenever introducing significant architectural changes, phases, or migrations, generate an implementation plan artifact and await user review.
2. **Incremental Execution:** Build and verify step-by-step. Run tests after implementing each layer.
3. **Clean Code & Linting:** Code should adhere to PEP 8 (Python) and ESLint/Prettier (TypeScript).
