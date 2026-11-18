import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.db.database import (
    get_company_supply_chain,
    get_connection,
    get_graph_elements,
    init_db,
    upsert_companies,
    upsert_competitors,
    upsert_news_articles,
    upsert_supply_chain,
)
from app.db.models import CompanyRecord, CompetitorRecord, NewsArticleRecord, SupplyChainRecord
from app.main import app
from app.services.company_graph import CompanyGraphService


@pytest_asyncio.fixture
async def temp_supply_chain_db(tmp_path):
    """Set up an isolated SQLite database populated with sample companies and supply chain edges."""
    db_file = str(tmp_path / "test_supply_chain.db")
    await init_db(db_file)

    async with get_connection(db_file) as conn:
        # 1. Insert sample companies
        companies = [
            CompanyRecord(
                ticker="ASML",
                name="ASML Holding N.V.",
                sector="Information Technology",
                industry="Semiconductor Equipment",
                market_cap_tier="Mega",
            ),
            CompanyRecord(
                ticker="TSM",
                name="Taiwan Semiconductor Manufacturing",
                sector="Information Technology",
                industry="Semiconductor Foundry",
                market_cap_tier="Mega",
            ),
            CompanyRecord(
                ticker="NVDA",
                name="NVIDIA Corporation",
                sector="Information Technology",
                industry="Semiconductors & GPU",
                market_cap_tier="Mega",
            ),
            CompanyRecord(
                ticker="AMD",
                name="Advanced Micro Devices Inc.",
                sector="Information Technology",
                industry="Semiconductors & CPU/GPU",
                market_cap_tier="Large",
            ),
            CompanyRecord(
                ticker="MSFT",
                name="Microsoft Corporation",
                sector="Information Technology",
                industry="Systems Software & Cloud",
                market_cap_tier="Mega",
            ),
        ]
        await upsert_companies(conn, companies)

        # 2. Insert competitor pairings: NVDA <-> AMD
        competitors = [
            CompetitorRecord(company_ticker="NVDA", competitor_ticker="AMD", relationship_type="direct_competitor", weight=1.0),
            CompetitorRecord(company_ticker="AMD", competitor_ticker="NVDA", relationship_type="direct_competitor", weight=1.0),
        ]
        await upsert_competitors(conn, competitors)

        # 3. Insert supply chain value chain:
        # ASML -> TSM -> NVDA -> MSFT
        supply_chain = [
            SupplyChainRecord(
                supplier_ticker="ASML",
                customer_ticker="TSM",
                product_category="EUV Lithography Scanners",
                tier_or_importance="critical",
                weight=1.0,
            ),
            SupplyChainRecord(
                supplier_ticker="TSM",
                customer_ticker="NVDA",
                product_category="Advanced 4N Wafer Foundry",
                tier_or_importance="critical",
                weight=1.0,
            ),
            SupplyChainRecord(
                supplier_ticker="NVDA",
                customer_ticker="MSFT",
                product_category="Blackwell AI GPUs for Azure",
                tier_or_importance="critical",
                weight=1.0,
            ),
        ]
        await upsert_supply_chain(conn, supply_chain)

    return db_file


@pytest.mark.asyncio
async def test_supply_chain_database_operations(temp_supply_chain_db):
    """Verify supply chain database upserts, queries, and conflict handling."""
    async with get_connection(temp_supply_chain_db) as conn:
        # Query supply chain for NVDA
        nvda_sc = await get_company_supply_chain(conn, "NVDA")
        assert "suppliers" in nvda_sc
        assert "customers" in nvda_sc

        # NVDA has TSM as supplier
        assert len(nvda_sc["suppliers"]) == 1
        assert nvda_sc["suppliers"][0]["ticker"] == "TSM"
        assert nvda_sc["suppliers"][0]["product_category"] == "Advanced 4N Wafer Foundry"
        assert nvda_sc["suppliers"][0]["role"] == "supplier"

        # NVDA has MSFT as customer
        assert len(nvda_sc["customers"]) == 1
        assert nvda_sc["customers"][0]["ticker"] == "MSFT"
        assert nvda_sc["customers"][0]["product_category"] == "Blackwell AI GPUs for Azure"
        assert nvda_sc["customers"][0]["role"] == "customer"

        # TSM has ASML as supplier and NVDA as customer
        tsm_sc = await get_company_supply_chain(conn, "TSM")
        assert len(tsm_sc["suppliers"]) == 1
        assert tsm_sc["suppliers"][0]["ticker"] == "ASML"
        assert len(tsm_sc["customers"]) == 1
        assert tsm_sc["customers"][0]["ticker"] == "NVDA"

        # Test conflict update on existing link
        updated_link = [
            SupplyChainRecord(
                supplier_ticker="TSM",
                customer_ticker="NVDA",
                product_category="3nm GAA Wafer Foundry",
                tier_or_importance="critical",
                weight=0.99,
            )
        ]
        inserted = await upsert_supply_chain(conn, updated_link)
        assert inserted == 1

        nvda_sc_updated = await get_company_supply_chain(conn, "NVDA")
        assert nvda_sc_updated["suppliers"][0]["product_category"] == "3nm GAA Wafer Foundry"
        assert nvda_sc_updated["suppliers"][0]["weight"] == 0.99


@pytest.mark.asyncio
async def test_graph_elements_network_filtering(temp_supply_chain_db):
    """Verify get_graph_elements correctly isolates competition, supply_chain, and all networks."""
    async with get_connection(temp_supply_chain_db) as conn:
        # 1. Competition only
        nodes_comp, edges_comp, _ = await get_graph_elements(conn, network_type="competition")
        assert len(nodes_comp) == 5
        assert len(edges_comp) == 2  # NVDA-AMD and AMD-NVDA
        assert all(e["relationship_category"] == "competition" for e in edges_comp)
        assert all(e["is_directed"] is False for e in edges_comp)

        # 2. Supply chain only
        nodes_sc, edges_sc, _ = await get_graph_elements(conn, network_type="supply_chain")
        assert len(nodes_sc) == 5
        assert len(edges_sc) == 3  # ASML->TSM, TSM->NVDA, NVDA->MSFT
        assert all(e["relationship_category"] == "supply_chain" for e in edges_sc)
        assert all(e["is_directed"] is True for e in edges_sc)
        assert all(e["product_category"] is not None for e in edges_sc)

        # 3. All networks
        nodes_all, edges_all, _ = await get_graph_elements(conn, network_type="all")
        assert len(edges_all) == 5  # 2 competition + 3 supply chain


@pytest.mark.asyncio
async def test_supply_chain_api_routes(temp_supply_chain_db, monkeypatch):
    """Verify FastAPI routes for company profile with supply chain and graph filtering."""
    from app.api.graph_routes import graph_service
    from app.config import settings

    original_db = graph_service.db_path
    graph_service.db_path = temp_supply_chain_db
    monkeypatch.setattr(settings, "db_path", temp_supply_chain_db)
    transport = ASGITransport(app=app)

    try:
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            # 1. Company profile endpoint: /api/v1/companies/NVDA
            profile_res = await client.get("/api/v1/companies/NVDA")
            assert profile_res.status_code == 200
            data = profile_res.json()
            assert data["ticker"] == "NVDA"
            assert len(data["competitors"]) == 1
            assert data["competitors"][0]["ticker"] == "AMD"

            assert len(data["suppliers"]) == 1
            assert data["suppliers"][0]["ticker"] == "TSM"
            assert data["suppliers"][0]["product_category"] == "Advanced 4N Wafer Foundry"
            assert data["suppliers"][0]["role"] == "supplier"

            assert len(data["customers"]) == 1
            assert data["customers"][0]["ticker"] == "MSFT"
            assert data["customers"][0]["product_category"] == "Blackwell AI GPUs for Azure"
            assert data["customers"][0]["role"] == "customer"

            # 2. Graph endpoint with network_type=supply_chain
            graph_res = await client.get("/api/v1/graph?network_type=supply_chain")
            assert graph_res.status_code == 200
            gdata = graph_res.json()
            assert len(gdata["edges"]) == 3
            assert all(e["relationship_category"] == "supply_chain" for e in gdata["edges"])
    finally:
        graph_service.db_path = original_db


@pytest.mark.asyncio
async def test_contextual_supply_chain_news_partitioning(temp_supply_chain_db):
    """Verify contextual news service aggregates and partitions supply chain partner headlines."""
    async with get_connection(temp_supply_chain_db) as conn:
        articles = [
            NewsArticleRecord(
                guid="nvda-news-1",
                title="Nvidia Announces Record AI Accelerator Shipments",
                link="https://news.example.com/nvda",
                published_at="2026-03-10T12:00:00Z",
                source="Yahoo Finance",
                summary="Nvidia reports surging enterprise compute demand.",
                entity_ticker="NVDA",
                sector="Information Technology",
                fetched_at="2026-03-10T12:00:00Z",
            ),
            NewsArticleRecord(
                guid="amd-news-1",
                title="AMD Launches New Instinct MI325X AI Chips",
                link="https://news.example.com/amd",
                published_at="2026-03-10T11:00:00Z",
                source="Reuters",
                summary="AMD expands competition in enterprise data center silicon.",
                entity_ticker="AMD",
                sector="Information Technology",
                fetched_at="2026-03-10T12:00:00Z",
            ),
            NewsArticleRecord(
                guid="tsm-news-1",
                title="TSMC Expands 3nm Wafer Fab Capacity for AI Customers",
                link="https://news.example.com/tsm",
                published_at="2026-03-10T10:00:00Z",
                source="Bloomberg",
                summary="TSMC foundry ramps up CoWoS packaging volume.",
                entity_ticker="TSM",
                sector="Information Technology",
                fetched_at="2026-03-10T12:00:00Z",
            ),
        ]
        await upsert_news_articles(conn, articles)

    service = CompanyGraphService(db_path=temp_supply_chain_db)
    result = await service.get_contextual_news("NVDA")

    assert result["company"] is not None
    assert "TSM" in result["supply_chain_tickers"]
    assert "AMD" in result["competitor_tickers"]

    # Verify company news
    assert len(result["company_news"]) == 1
    assert result["company_news"][0].guid == "nvda-news-1"

    # Verify competitor news
    assert len(result["competitor_news"]) == 1
    assert result["competitor_news"][0].guid == "amd-news-1"

    # Verify supply chain news contains TSM headline
    assert len(result["supply_chain_news"]) == 1
    assert result["supply_chain_news"][0].guid == "tsm-news-1"
    assert result["supply_chain_news"][0].entity_ticker == "TSM"
