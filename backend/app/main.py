from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.graph_routes import router as graph_router
from app.api.micro_routes import router as micro_router
from app.api.routes import router as api_router
from app.config import settings
from app.db.database import get_connection, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager initializing SQLite database and graph seed."""
    await init_db()
    async with get_connection() as conn:
        async with conn.execute("SELECT count(*) FROM companies") as cursor:
            row = await cursor.fetchone()
            if row and row[0] == 0:
                from app.services.seed_graph import seed_graph_database
                await seed_graph_database()

        async with conn.execute("SELECT count(*) FROM news_articles") as cursor:
            row = await cursor.fetchone()
            if row and row[0] == 0:
                from app.services.seed_news import seed_news_database
                await seed_news_database()

        async with conn.execute("SELECT count(*) FROM observations WHERE source = 'SEC EDGAR'") as cursor:
            row = await cursor.fetchone()
            if row and row[0] == 0:
                from app.data.cik_mapping import get_seed_fundamentals
                from app.db.database import upsert_observations
                fundamentals = get_seed_fundamentals()
                await upsert_observations(conn, fundamentals)

        async with conn.execute("SELECT count(*) FROM company_supply_chain") as cursor:
            row = await cursor.fetchone()
            if row and row[0] == 0:
                from app.services.seed_supply_chain import seed_supply_chain_database
                await seed_supply_chain_database()
    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="MacroScope: Open Macroeconomic & Market Intelligence API (100% Keyless)",
    lifespan=lifespan,
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Attach API routes under /api/v1
app.include_router(api_router, prefix="/api/v1")
app.include_router(graph_router, prefix="/api/v1")
app.include_router(micro_router, prefix="/api/v1")


@app.get("/", tags=["Root"])
async def root():
    return {
        "message": "Welcome to MacroScope API",
        "docs_url": "/docs",
        "health_url": "/api/v1/health",
    }
