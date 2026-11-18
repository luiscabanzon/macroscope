"""Curated pre-seeded snapshot of recent company, competitor, and sector financial news."""

from datetime import datetime, timedelta, timezone
from app.db.models import NewsArticleRecord

NOW = datetime.now(timezone.utc)

def hours_ago(h: int) -> str:
    return (NOW - timedelta(hours=h)).isoformat()

CURATED_NEWS_DATA: list[dict] = [
    # --- Apple (AAPL) & Ecosystem ---
    {
        "guid": "aapl-news-101",
        "entity_ticker": "AAPL",
        "sector": "Information Technology",
        "title": "Apple Previews Next-Gen M4 Pro Silicon and On-Device Intelligence Suite",
        "link": "https://finance.yahoo.com/news/apple-m4-pro-announcement-120000.html",
        "source": "Bloomberg",
        "summary": "Apple unveiled its latest Mac lineup powered by M4 and M4 Pro processors, touting significant improvements in machine learning inference efficiency and battery longevity.",
        "hours_ago": 2,
    },
    {
        "guid": "aapl-news-102",
        "entity_ticker": "AAPL",
        "sector": "Information Technology",
        "title": "Services Revenue Drives Strong Margin Resilience for Apple in Latest Quarter",
        "link": "https://www.reuters.com/technology/apple-services-growth-margins-2026-11-18/",
        "source": "Reuters",
        "summary": "Apple's Services segment continues to outpace hardware sales growth, surpassing expectations driven by App Store transactions, iCloud storage, and Apple Music subscriptions.",
        "hours_ago": 8,
    },

    # --- Microsoft (MSFT) ---
    {
        "guid": "msft-news-201",
        "entity_ticker": "MSFT",
        "sector": "Information Technology",
        "title": "Microsoft Expands Azure AI Enterprise Infrastructure with Custom Silicon Deployments",
        "link": "https://www.cnbc.com/2026/11/17/microsoft-azure-ai-infrastructure-expansion.html",
        "source": "CNBC",
        "summary": "Microsoft Corporation announced the broad availability of Azure Cobalt 100 processors and Maia accelerators across primary data center hubs, reducing cost per compute token.",
        "hours_ago": 5,
    },
    {
        "guid": "msft-news-202",
        "entity_ticker": "MSFT",
        "sector": "Information Technology",
        "title": "Microsoft Copilot Adoption Accelerates Among Fortune 500 Enterprise Workforces",
        "link": "https://www.wsj.com/articles/microsoft-copilot-enterprise-rollout-11678900",
        "source": "Wall Street Journal",
        "summary": "Commercial seat commitments for Microsoft 365 Copilot grew 60% year-over-year, cementing Microsoft's monetization runway across corporate productivity workflows.",
        "hours_ago": 16,
    },

    # --- Alphabet / Google (GOOGL) ---
    {
        "guid": "googl-news-301",
        "entity_ticker": "GOOGL",
        "sector": "Communication Services",
        "title": "Alphabet Unveils Gemini 2.5 Flash Architecture with Multi-Modal Real-Time Tool Use",
        "link": "https://finance.yahoo.com/news/alphabet-gemini-multimodal-update-150000.html",
        "source": "Yahoo Finance",
        "summary": "Google's AI research lab released its next generation model family, demonstrating latency reductions and agentic orchestration capabilities across search and workspace.",
        "hours_ago": 3,
    },
    {
        "guid": "googl-news-302",
        "entity_ticker": "GOOGL",
        "sector": "Communication Services",
        "title": "Google Cloud Profitability Surges on Cloud TPU Customer Backlog",
        "link": "https://www.bloomberg.com/news/articles/2026-11-17/google-cloud-tpu-demand-surges",
        "source": "Bloomberg",
        "summary": "Google Cloud reported accelerated operating margin expansion as demand for v5p and v6e TPUs outpaces supply from AI startup and enterprise clients.",
        "hours_ago": 12,
    },

    # --- Nvidia (NVDA) ---
    {
        "guid": "nvda-news-401",
        "entity_ticker": "NVDA",
        "sector": "Information Technology",
        "title": "NVIDIA Blackwell B200 Systems Enter High-Volume Shipment to Tier-1 Hyperscalers",
        "link": "https://www.reuters.com/technology/nvidia-blackwell-shipments-ramp-2026-11-18/",
        "source": "Reuters",
        "summary": "Nvidia CEO Jensen Huang confirmed full-scale rack delivery of NVL72 liquid-cooled superclusters to Microsoft, Amazon, Google, and Meta data centers.",
        "hours_ago": 1,
    },
    {
        "guid": "nvda-news-402",
        "entity_ticker": "NVDA",
        "sector": "Information Technology",
        "title": "NVIDIA Partners with European Industrial Consortium for Sovereign Factory AI",
        "link": "https://www.cnbc.com/2026/11/17/nvidia-european-industrial-ai-factory.html",
        "source": "CNBC",
        "summary": "Nvidia announced partnerships with Siemens and ASML to build industrial digital twins using Omniverse and specialized enterprise robotics models.",
        "hours_ago": 9,
    },

    # --- AMD & Intel ---
    {
        "guid": "amd-news-501",
        "entity_ticker": "AMD",
        "sector": "Information Technology",
        "title": "AMD Instinct MI325X Accelerators Gain Traction Across Enterprise Private Clouds",
        "link": "https://finance.yahoo.com/news/amd-instinct-mi325x-adoption-140000.html",
        "source": "Yahoo Finance",
        "summary": "Advanced Micro Devices is capturing market share in enterprise inference workloads with its ROCm 6.2 software ecosystem and 256GB HBM3E memory configurations.",
        "hours_ago": 6,
    },
    {
        "guid": "intc-news-502",
        "entity_ticker": "INTC",
        "sector": "Information Technology",
        "title": "Intel Foundry Secures Major Government and Defense Packaging Commitments",
        "link": "https://www.bloomberg.com/news/articles/2026-11-17/intel-foundry-packaging-awards",
        "source": "Bloomberg",
        "summary": "Intel Corporation announced key customer validations for its 18A node and advanced Foveros 3D packaging technologies as domestic manufacturing initiatives advance.",
        "hours_ago": 14,
    },

    # --- Tesla (TSLA) & Auto Rivals ---
    {
        "guid": "tsla-news-601",
        "entity_ticker": "TSLA",
        "sector": "Consumer Discretionary",
        "title": "Tesla Cybercab Unsupervised Full Self-Driving Testing Expands to Multi-City Pilot",
        "link": "https://www.reuters.com/business/autos-transportation/tesla-fsd-robotaxi-pilot-2026-11-18/",
        "source": "Reuters",
        "summary": "Tesla Inc. initiated ride-hail pilot testing for employees in Texas and California utilizing its vision-only end-to-end neural network architecture.",
        "hours_ago": 4,
    },
    {
        "guid": "f-news-602",
        "entity_ticker": "F",
        "sector": "Consumer Discretionary",
        "title": "Ford Pro Commercial Fleet Division Posts Record Margins on Connected Telematics",
        "link": "https://www.cnbc.com/2026/11/17/ford-pro-commercial-fleet-earnings.html",
        "source": "CNBC",
        "summary": "Ford Motor Company highlighted double-digit revenue growth in commercial software and fleet maintenance subscriptions, balancing consumer EV investments.",
        "hours_ago": 10,
    },
    {
        "guid": "gm-news-603",
        "entity_ticker": "GM",
        "sector": "Consumer Discretionary",
        "title": "General Motors Boosts Shareholder Return Program Following Robust Truck Cash Flows",
        "link": "https://finance.yahoo.com/news/general-motors-truck-cash-flows-110000.html",
        "source": "Yahoo Finance",
        "summary": "GM authorized an accelerated share repurchase program, citing steady demand and stable pricing power for full-size pickup trucks and hybrid SUV models.",
        "hours_ago": 18,
    },

    # --- Energy: ExxonMobil (XOM) & Chevron (CVX) ---
    {
        "guid": "xom-news-701",
        "entity_ticker": "XOM",
        "sector": "Energy",
        "title": "ExxonMobil Delivers Record Permian and Guyana Production Volumes at Low Breakevens",
        "link": "https://www.wsj.com/articles/exxon-permian-production-record-11678912",
        "source": "Wall Street Journal",
        "summary": "Exxon Mobil announced that integrated operations in the Delaware basin and offshore Guyana generated breakeven cash generation below $35 per barrel.",
        "hours_ago": 5,
    },
    {
        "guid": "cvx-news-702",
        "entity_ticker": "CVX",
        "sector": "Energy",
        "title": "Chevron Advances Gulf of Mexico Deepwater Anchor Project Ahead of Schedule",
        "link": "https://www.reuters.com/business/energy/chevron-deepwater-anchor-production-2026-11-17/",
        "source": "Reuters",
        "summary": "Chevron Corporation achieved initial production from its 20,000-psi high-pressure deepwater platform, adding high-margin barrel capacity to its portfolio.",
        "hours_ago": 11,
    },

    # --- Financials: JPMorgan (JPM) & Mega Banks ---
    {
        "guid": "jpm-news-801",
        "entity_ticker": "JPM",
        "sector": "Financials",
        "title": "JPMorgan Chase Reports Strong Net Interest Income and Robust M&A Underwriting",
        "link": "https://www.bloomberg.com/news/articles/2026-11-18/jpmorgan-q3-results-net-interest-income",
        "source": "Bloomberg",
        "summary": "JPMorgan CEO Jamie Dimon noted strong corporate liquidity and expanding advisory pipelines despite global macro uncertainty, reaffirming firm-wide guidance.",
        "hours_ago": 2,
    },
    {
        "guid": "gs-news-802",
        "entity_ticker": "GS",
        "sector": "Financials",
        "title": "Goldman Sachs Capital Markets Revenues Rebound Driven by Equity and Debt Origination",
        "link": "https://www.cnbc.com/2026/11/17/goldman-sachs-capital-markets-rebound.html",
        "source": "CNBC",
        "summary": "Goldman Sachs posted a 25% increase in investment banking fees as private equity sponsors re-enter the market for recapitalizations and cross-border M&A.",
        "hours_ago": 7,
    },

    # --- Health Care: Eli Lilly (LLY) & Pharma ---
    {
        "guid": "lly-news-901",
        "entity_ticker": "LLY",
        "sector": "Health Care",
        "title": "Eli Lilly Expands Global Incretin Manufacturing Footprint to Meet Global Demand",
        "link": "https://www.reuters.com/business/healthcare-pharmaceuticals/eli-lilly-manufacturing-expansion-2026-11-18/",
        "source": "Reuters",
        "summary": "Eli Lilly committed $4.5 billion to greenfield manufacturing sites for GLP-1 and GIP dual-agonist therapies, targeting supply bottlenecks in North America and Europe.",
        "hours_ago": 4,
    },
    {
        "guid": "jnj-news-902",
        "entity_ticker": "JNJ",
        "sector": "Health Care",
        "title": "Johnson & Johnson MedTech Division Sees Accelerated Uptake in Robotic Surgery Platforms",
        "link": "https://finance.yahoo.com/news/jnj-medtech-robotic-surgery-growth-130000.html",
        "source": "Yahoo Finance",
        "summary": "JNJ's orthopedic and cardiovascular medical device segments reported resilient procedure volumes, offsetting patent expiration headwinds in oncology pharmaceuticals.",
        "hours_ago": 15,
    },

    # --- Sector Trends: Industry-Wide Updates ---
    {
        "guid": "sector-tech-01",
        "entity_ticker": None,
        "sector": "Information Technology",
        "title": "Global Semiconductor Equipment Bookings Surge 18% as Advanced Packaging Bottlenecks Ease",
        "link": "https://www.bloomberg.com/news/articles/2026-11-18/semiconductor-equipment-global-bookings",
        "source": "Bloomberg",
        "summary": "Industry association reports indicate worldwide billings for wafer processing equipment reached new quarterly highs driven by hyperscaler AI capex commitments.",
        "hours_ago": 3,
    },
    {
        "guid": "sector-energy-02",
        "entity_ticker": None,
        "sector": "Energy",
        "title": "Crude Oil Consolidates Around $78 as OPEC+ Maintains Quota Discipline Amid Refinery Demand",
        "link": "https://www.reuters.com/business/energy/crude-oil-brent-opec-discipline-2026-11-18/",
        "source": "Reuters",
        "summary": "Brent crude oil traded in a tight channel as market participants weighed stable Middle East production against seasonal winter fuel demand in the Northern Hemisphere.",
        "hours_ago": 6,
    },
    {
        "guid": "sector-finance-03",
        "entity_ticker": None,
        "sector": "Financials",
        "title": "Central Bank Policy Trajectories Diverge as Credit Spreads Remain Historically Tight",
        "link": "https://www.wsj.com/articles/central-bank-policy-credit-spreads-11678955",
        "source": "Wall Street Journal",
        "summary": "Corporate bond issuance reached brisk volumes while bank loan loss provisions remained well within historical tolerances, signaling continued corporate balance sheet strength.",
        "hours_ago": 12,
    },
    {
        "guid": "sector-auto-04",
        "entity_ticker": None,
        "sector": "Consumer Discretionary",
        "title": "Hybrid Powertrain Registrations Outpace Pure Battery Electrics in US and European Markets",
        "link": "https://www.cnbc.com/2026/11/17/hybrid-vehicle-sales-surge-automotive.html",
        "source": "CNBC",
        "summary": "Consumer preferences for extended-range plug-in hybrids and conventional hybrids drove vehicle sales gains for traditional OEMs adjusting capital expenditure schedules.",
        "hours_ago": 17,
    },
]


def get_seed_news_articles() -> list[NewsArticleRecord]:
    """Generate normalized NewsArticleRecord instances for pre-seeding."""
    now_ts = NOW.isoformat()
    return [
        NewsArticleRecord(
            guid=item["guid"],
            title=item["title"],
            link=item["link"],
            published_at=hours_ago(item["hours_ago"]),
            source=item["source"],
            summary=item["summary"],
            entity_ticker=item["entity_ticker"],
            sector=item["sector"],
            fetched_at=now_ts,
        )
        for item in CURATED_NEWS_DATA
    ]
