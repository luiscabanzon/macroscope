"""Curated NASDAQ 100 and S&P 500 company universe and competitor linkages."""

from app.db.models import CompanyRecord, CompetitorRecord

# 1. Company Definitions (NASDAQ 100 + S&P 500 Bellwethers)
COMPANIES_DATA: list[dict] = [
    # --- Information Technology: Big Tech, Cloud & OS ---
    {"ticker": "AAPL", "name": "Apple Inc.", "sector": "Information Technology", "industry": "Consumer Electronics & OS", "tier": "Mega", "desc": "Designs, manufactures, and markets smartphones, personal computers, tablets, wearables, and services."},
    {"ticker": "MSFT", "name": "Microsoft Corporation", "sector": "Information Technology", "industry": "Systems Software & Cloud", "tier": "Mega", "desc": "Develops and supports software, services, devices and cloud solutions including Azure, Windows, and Office."},
    {"ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Communication Services", "industry": "Interactive Media & Cloud", "tier": "Mega", "desc": "Provides search, advertising, cloud computing (Google Cloud), streaming (YouTube), and AI technology."},
    {"ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Discretionary", "industry": "E-Commerce & Cloud Infrastructure", "tier": "Mega", "desc": "Focuses on retail e-commerce, cloud computing (AWS), digital streaming, and artificial intelligence."},
    {"ticker": "META", "name": "Meta Platforms Inc.", "sector": "Communication Services", "industry": "Social Media & VR", "tier": "Mega", "desc": "Builds technologies that help people connect including Facebook, Instagram, WhatsApp, and Quest VR."},

    # --- Information Technology: Semiconductors & Hardware ---
    {"ticker": "NVDA", "name": "NVIDIA Corporation", "sector": "Information Technology", "industry": "Semiconductors & GPU", "tier": "Mega", "desc": "Pioneers GPU computing, generative AI accelerators, and data center hardware systems."},
    {"ticker": "AMD", "name": "Advanced Micro Devices Inc.", "sector": "Information Technology", "industry": "Semiconductors & CPU/GPU", "tier": "Large", "desc": "Produces microprocessors, GPUs, and adaptive SoCs for servers, PCs, and gaming."},
    {"ticker": "INTC", "name": "Intel Corporation", "sector": "Information Technology", "industry": "Semiconductors & Foundry", "tier": "Large", "desc": "Designs and manufactures microprocessors and foundry semiconductor products for cloud and client."},
    {"ticker": "AVGO", "name": "Broadcom Inc.", "sector": "Information Technology", "industry": "Semiconductors & Infrastructure Software", "tier": "Mega", "desc": "Develops enterprise storage, networking silicon, wireless semiconductors, and infrastructure software."},
    {"ticker": "QCOM", "name": "Qualcomm Inc.", "sector": "Information Technology", "industry": "Semiconductors & Wireless", "tier": "Large", "desc": "Develops wireless telecommunications products and Snapdragon mobile application processors."},
    {"ticker": "TSM", "name": "Taiwan Semiconductor Manufacturing", "sector": "Information Technology", "industry": "Semiconductor Foundry", "tier": "Mega", "desc": "World's largest dedicated contract semiconductor manufacturing foundry."},
    {"ticker": "TXN", "name": "Texas Instruments Inc.", "sector": "Information Technology", "industry": "Analog Semiconductors", "tier": "Large", "desc": "Designs and manufactures analog and embedded processing chips for industrial and auto markets."},
    {"ticker": "ASML", "name": "ASML Holding N.V.", "sector": "Information Technology", "industry": "Semiconductor Equipment", "tier": "Mega", "desc": "Manufactures advanced extreme ultraviolet (EUV) photolithography systems for chipmakers."},
    {"ticker": "AMAT", "name": "Applied Materials Inc.", "sector": "Information Technology", "industry": "Semiconductor Equipment", "tier": "Large", "desc": "Supplies equipment, software, and services for the manufacture of semiconductor chips."},
    {"ticker": "LRCX", "name": "Lam Research Corporation", "sector": "Information Technology", "industry": "Semiconductor Equipment", "tier": "Large", "desc": "Designs semiconductor processing equipment used in wafer fabrication and etch processes."},
    {"ticker": "MU", "name": "Micron Technology Inc.", "sector": "Information Technology", "industry": "Memory & Storage Silicon", "tier": "Large", "desc": "Manufactures DRAM, NAND flash memory, and high-bandwidth memory (HBM) for data centers."},

    # --- Information Technology: Enterprise Software & Cybersecurity ---
    {"ticker": "CRM", "name": "Salesforce Inc.", "sector": "Information Technology", "industry": "Enterprise Software & CRM", "tier": "Large", "desc": "Provides Customer Relationship Management cloud software, analytics, and workflow automation."},
    {"ticker": "ORCL", "name": "Oracle Corporation", "sector": "Information Technology", "industry": "Enterprise Software & Cloud DB", "tier": "Large", "desc": "Offers enterprise software, database management systems, and Oracle Cloud Infrastructure (OCI)."},
    {"ticker": "ADBE", "name": "Adobe Inc.", "sector": "Information Technology", "industry": "Application Software & Creative", "tier": "Large", "desc": "Provides digital marketing and creative software tools including Photoshop, Illustrator, and Acrobat."},
    {"ticker": "NOW", "name": "ServiceNow Inc.", "sector": "Information Technology", "industry": "Systems & Workflow Software", "tier": "Large", "desc": "Operates cloud computing platforms for digital enterprise workflows and IT service management."},
    {"ticker": "INTU", "name": "Intuit Inc.", "sector": "Information Technology", "industry": "Financial & Tax Software", "tier": "Large", "desc": "Develops TurboTax, QuickBooks, Mint, and Credit Karma financial software applications."},
    {"ticker": "CRWD", "name": "CrowdStrike Holdings Inc.", "sector": "Information Technology", "industry": "Cybersecurity", "tier": "Large", "desc": "Provides cloud-delivered endpoint security, threat intelligence, and cyberattack response."},
    {"ticker": "PANW", "name": "Palo Alto Networks Inc.", "sector": "Information Technology", "industry": "Cybersecurity & Firewalls", "tier": "Large", "desc": "Offers enterprise cybersecurity platforms, network security firewalls, and cloud security."},
    {"ticker": "SNOW", "name": "Snowflake Inc.", "sector": "Information Technology", "industry": "Cloud Data Warehousing", "tier": "Large", "desc": "Provides a cloud-based data platform for data lakes, data engineering, and data science."},

    # --- Consumer Discretionary: Automotive & EV ---
    {"ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Discretionary", "industry": "Automotive & Clean Energy", "tier": "Mega", "desc": "Designs, manufactures, and sells electric vehicles, energy storage systems, and solar panels."},
    {"ticker": "F", "name": "Ford Motor Company", "sector": "Consumer Discretionary", "industry": "Automobile Manufacturers", "tier": "Large", "desc": "Manufactures and sells trucks, commercial vehicles, SUVs, and electric vehicles globally."},
    {"ticker": "GM", "name": "General Motors Company", "sector": "Consumer Discretionary", "industry": "Automobile Manufacturers", "tier": "Large", "desc": "Designs and sells trucks, crossovers, and cars under Chevrolet, GMC, Cadillac, and Buick."},
    {"ticker": "TM", "name": "Toyota Motor Corporation", "sector": "Consumer Discretionary", "industry": "Automobile Manufacturers", "tier": "Mega", "desc": "World's largest automaker producing passenger cars, hybrid vehicles, and commercial trucks."},
    {"ticker": "RIVN", "name": "Rivian Automotive Inc.", "sector": "Consumer Discretionary", "industry": "Electric Vehicles", "tier": "Mid", "desc": "Manufactures electric adventure pickup trucks (R1T), SUVs (R1S), and commercial delivery vans."},

    # --- Consumer Discretionary: Retail, Apparel & Dining ---
    {"ticker": "HD", "name": "The Home Depot Inc.", "sector": "Consumer Discretionary", "industry": "Home Improvement Retail", "tier": "Large", "desc": "World's largest home improvement specialty retailer selling tools, construction products, and services."},
    {"ticker": "LOW", "name": "Lowe's Companies Inc.", "sector": "Consumer Discretionary", "industry": "Home Improvement Retail", "tier": "Large", "desc": "Operates home improvement and hardware retail stores across the United States."},
    {"ticker": "MCD", "name": "McDonald's Corporation", "sector": "Consumer Discretionary", "industry": "Restaurants & Fast Food", "tier": "Large", "desc": "World's largest fast-food restaurant chain operating and franchising global quick-service locations."},
    {"ticker": "SBUX", "name": "Starbucks Corporation", "sector": "Consumer Discretionary", "industry": "Restaurants & Specialty Coffee", "tier": "Large", "desc": "Roaster, marketer, and retailer of specialty coffee and food items across global retail stores."},
    {"ticker": "NKE", "name": "NIKE Inc.", "sector": "Consumer Discretionary", "industry": "Footwear & Athletic Apparel", "tier": "Large", "desc": "Designs, develops, and sells athletic footwear, apparel, equipment, and accessories."},
    {"ticker": "LULU", "name": "Lululemon Athletica Inc.", "sector": "Consumer Discretionary", "industry": "Apparel & Athleisure", "tier": "Large", "desc": "Designs and retails technical athletic apparel for yoga, running, training, and wellness."},

    # --- Consumer Staples: Retail & Packaged Goods ---
    {"ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Staples", "industry": "Hypermarkets & Supercenters", "tier": "Mega", "desc": "Operates a worldwide chain of hypermarkets, discount department stores, and grocery stores."},
    {"ticker": "COST", "name": "Costco Wholesale Corporation", "sector": "Consumer Staples", "industry": "Membership Warehouses", "tier": "Large", "desc": "Operates membership warehouse clubs offering branded and private-label merchandise in bulk."},
    {"ticker": "TGT", "name": "Target Corporation", "sector": "Consumer Staples", "industry": "General Merchandise Stores", "tier": "Large", "desc": "Operates general merchandise discount retail stores and e-commerce across the US."},
    {"ticker": "PG", "name": "The Procter & Gamble Company", "sector": "Consumer Staples", "industry": "Household & Personal Care", "tier": "Mega", "desc": "Produces consumer packaged goods in beauty, grooming, healthcare, fabric, and home care."},
    {"ticker": "KO", "name": "The Coca-Cola Company", "sector": "Consumer Staples", "industry": "Non-Alcoholic Beverages", "tier": "Large", "desc": "Manufactures, markets, and sells non-alcoholic beverage concentrates, syrups, and finished drinks."},
    {"ticker": "PEP", "name": "PepsiCo Inc.", "sector": "Consumer Staples", "industry": "Snacks & Beverages", "tier": "Large", "desc": "Manufactures beverages and convenient foods under Pepsi, Frito-Lay, Gatorade, and Quaker."},

    # --- Financials: Mega Banks & Investment Firms ---
    {"ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financials", "industry": "Diversified Banking", "tier": "Mega", "desc": "Largest US financial services firm providing investment banking, consumer banking, and asset management."},
    {"ticker": "BAC", "name": "Bank of America Corporation", "sector": "Financials", "industry": "Diversified Banking", "tier": "Large", "desc": "Provides consumer banking, corporate banking, Merrill wealth management, and capital markets."},
    {"ticker": "WFC", "name": "Wells Fargo & Company", "sector": "Financials", "industry": "Diversified Banking", "tier": "Large", "desc": "Provides retail, commercial, and mortgage banking services to individuals and businesses."},
    {"ticker": "C", "name": "Citigroup Inc.", "sector": "Financials", "industry": "Diversified Banking", "tier": "Large", "desc": "Global bank connecting consumers, corporations, and governments in 160 countries."},
    {"ticker": "GS", "name": "The Goldman Sachs Group Inc.", "sector": "Financials", "industry": "Investment Banking & Capital Markets", "tier": "Large", "desc": "Provides investment banking, securities dealing, prime brokerage, and asset management."},
    {"ticker": "MS", "name": "Morgan Stanley", "sector": "Financials", "industry": "Investment Banking & Wealth Management", "tier": "Large", "desc": "Provides institutional securities, wealth management (E*TRADE), and investment management services."},
    {"ticker": "BRK.B", "name": "Berkshire Hathaway Inc.", "sector": "Financials", "industry": "Multi-Sector Holdings & Insurance", "tier": "Mega", "desc": "Holding company owning GEICO, BNSF Railway, utility assets, and extensive equity holdings."},
    {"ticker": "V", "name": "Visa Inc.", "sector": "Financials", "industry": "Payment Transaction Processing", "tier": "Mega", "desc": "Facilitates global digital payments between consumers, merchants, financial institutions, and governments."},
    {"ticker": "MA", "name": "Mastercard Incorporated", "sector": "Financials", "industry": "Payment Transaction Processing", "tier": "Large", "desc": "Connects consumers, financial institutions, and merchants for digital electronic payments worldwide."},

    # --- Energy: Oil, Gas & Consumable Fuels ---
    {"ticker": "XOM", "name": "Exxon Mobil Corporation", "sector": "Energy", "industry": "Integrated Oil & Gas", "tier": "Mega", "desc": "Explores, produces, and refines crude oil, natural gas, petrochemicals, and petroleum products."},
    {"ticker": "CVX", "name": "Chevron Corporation", "sector": "Energy", "industry": "Integrated Oil & Gas", "tier": "Large", "desc": "Engages in integrated energy operations including upstream exploration, downstream refining, and chemicals."},
    {"ticker": "COP", "name": "ConocoPhillips", "sector": "Energy", "industry": "Oil & Gas Exploration & Production", "tier": "Large", "desc": "Independent exploration and production company with assets in Alaska, Permian, and LNG terminals."},
    {"ticker": "SLB", "name": "Schlumberger Limited (SLB)", "sector": "Energy", "industry": "Oilfield Services & Equipment", "tier": "Large", "desc": "Provides oilfield technology, reservoir characterization, drilling, and production software."},
    {"ticker": "EOG", "name": "EOG Resources Inc.", "sector": "Energy", "industry": "Oil & Gas Exploration & Production", "tier": "Large", "desc": "Crude oil and natural gas exploration and production company focused on US shale basins."},

    # --- Health Care: Pharmaceuticals & Biotechnology ---
    {"ticker": "LLY", "name": "Eli Lilly and Company", "sector": "Health Care", "industry": "Pharmaceuticals", "tier": "Mega", "desc": "Develops medicines in diabetes, oncology, immunology, and neurodegeneration including Mounjaro and Zepbound."},
    {"ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Health Care", "industry": "Pharmaceuticals & MedTech", "tier": "Mega", "desc": "Researches, develops, and manufactures innovative pharmaceuticals and medical technology devices."},
    {"ticker": "PFE", "name": "Pfizer Inc.", "sector": "Health Care", "industry": "Biopharmaceuticals", "tier": "Large", "desc": "Discovers, develops, and manufactures vaccines, oncology treatments, and biopharmaceuticals."},
    {"ticker": "MRK", "name": "Merck & Co. Inc.", "sector": "Health Care", "industry": "Pharmaceuticals & Oncology", "tier": "Large", "desc": "Develops prescription medicines, vaccines, and animal health products, including Keytruda."},
    {"ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Health Care", "industry": "Biopharmaceuticals", "tier": "Large", "desc": "Researches and markets pharmaceuticals in immunology, oncology, neuroscience, and aesthetics."},
    {"ticker": "ISRG", "name": "Intuitive Surgical Inc.", "sector": "Health Care", "industry": "Robotic Medical Equipment", "tier": "Large", "desc": "Develops and manufactures the da Vinci surgical system for minimally invasive robotic surgery."},
    {"ticker": "ABT", "name": "Abbott Laboratories", "sector": "Health Care", "industry": "Medical Devices & Diagnostics", "tier": "Large", "desc": "Produces cardiovascular medical devices, diagnostic systems, branded generics, and nutritional products."},

    # --- Industrials: Aerospace, Defense & Machinery ---
    {"ticker": "BA", "name": "The Boeing Company", "sector": "Industrials", "industry": "Aerospace & Commercial Aircraft", "tier": "Large", "desc": "Designs, manufactures, and sells commercial jetliners, defense aircraft, satellites, and space systems."},
    {"ticker": "LMT", "name": "Lockheed Martin Corporation", "sector": "Industrials", "industry": "Aerospace & Defense Systems", "tier": "Large", "desc": "Specializes in aeronautics, tactical missiles, radar, and space defense systems including F-35."},
    {"ticker": "RTX", "name": "RTX Corporation", "sector": "Industrials", "industry": "Aerospace & Defense Systems", "tier": "Large", "desc": "Produces commercial aircraft engines (Pratt & Whitney), avionics (Collins), and defense electronics (Raytheon)."},
    {"ticker": "CAT", "name": "Caterpillar Inc.", "sector": "Industrials", "industry": "Construction & Mining Machinery", "tier": "Large", "desc": "World's leading manufacturer of construction and mining equipment, diesel and natural gas engines."},
    {"ticker": "DE", "name": "Deere & Company", "sector": "Industrials", "industry": "Agricultural Machinery", "tier": "Large", "desc": "Manufactures agricultural machinery, construction equipment, and precision farming technology."},
    {"ticker": "GE", "name": "GE Aerospace", "sector": "Industrials", "industry": "Commercial & Defense Aviation Engines", "tier": "Large", "desc": "Provides commercial and military aircraft engines, components, and integrated systems."},

    # --- Communication Services: Streaming & Telecom ---
    {"ticker": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services", "industry": "Subscription Streaming Entertainment", "tier": "Large", "desc": "Operates a global entertainment subscription service providing TV series, films, and mobile games."},
    {"ticker": "DIS", "name": "The Walt Disney Company", "sector": "Communication Services", "industry": "Entertainment & Theme Parks", "tier": "Large", "desc": "Diversified media and entertainment enterprise operating theme parks, studios, and streaming (Disney+)."},
    {"ticker": "CMCSA", "name": "Comcast Corporation", "sector": "Communication Services", "industry": "Broadband, Cable & Media", "tier": "Large", "desc": "Operates Xfinity broadband connectivity, NBCUniversal media/theme parks, and Sky telecommunications."},
    {"ticker": "TMUS", "name": "T-Mobile US Inc.", "sector": "Communication Services", "industry": "Wireless Telecommunications", "tier": "Large", "desc": "Provides 5G mobile communications, wireless voice and data services, and broadband."},
    {"ticker": "VZ", "name": "Verizon Communications Inc.", "sector": "Communication Services", "industry": "Wireless Telecommunications", "tier": "Large", "desc": "Provides wireless communications, broadband wireline, and business connectivity services."},
    {"ticker": "T", "name": "AT&T Inc.", "sector": "Communication Services", "industry": "Telecommunications & Fiber", "tier": "Large", "desc": "Provides wireless 5G mobile connectivity, fiber broadband, and business telecommunication networks."},
]

# 2. Curated Competitor Pairings (Cluster & Rivalry Graph Edges)
# Format: (Company A, Company B, relationship_type, weight)
COMPETITOR_PAIRINGS: list[tuple[str, str, str, float]] = [
    # Big Tech / Cloud / OS Ecosystems
    ("AAPL", "MSFT", "direct_competitor", 1.0),
    ("AAPL", "GOOGL", "direct_competitor", 1.0),
    ("MSFT", "GOOGL", "direct_competitor", 1.0),
    ("MSFT", "AMZN", "direct_competitor", 1.0),  # Cloud AWS vs Azure
    ("GOOGL", "AMZN", "direct_competitor", 0.9),  # Cloud GCP vs AWS & Ad Search
    ("META", "GOOGL", "direct_competitor", 1.0),  # Digital Advertising
    ("META", "AAPL", "direct_competitor", 0.8),  # Hardware / Privacy / Ecosystem

    # AI Compute & Semiconductors
    ("NVDA", "AMD", "direct_competitor", 1.0),
    ("NVDA", "INTC", "direct_competitor", 0.9),
    ("AMD", "INTC", "direct_competitor", 1.0),
    ("QCOM", "AVGO", "direct_competitor", 0.8),
    ("QCOM", "AAPL", "sector_peer", 0.7),
    ("AVGO", "NVDA", "sector_peer", 0.8),
    ("AMAT", "LRCX", "direct_competitor", 1.0),
    ("AMAT", "ASML", "sector_peer", 0.8),
    ("LRCX", "ASML", "sector_peer", 0.8),
    ("MU", "TSM", "sector_peer", 0.7),
    ("INTC", "TSM", "direct_competitor", 0.8),  # Foundry competition

    # Enterprise Software & Cyber
    ("CRM", "MSFT", "direct_competitor", 0.9),
    ("CRM", "ORCL", "direct_competitor", 1.0),
    ("ORCL", "MSFT", "direct_competitor", 0.8),
    ("ADBE", "CRM", "sector_peer", 0.7),
    ("NOW", "CRM", "sector_peer", 0.8),
    ("NOW", "MSFT", "sector_peer", 0.7),
    ("CRWD", "PANW", "direct_competitor", 1.0),
    ("PANW", "MSFT", "direct_competitor", 0.8),
    ("SNOW", "ORCL", "direct_competitor", 0.8),
    ("SNOW", "GOOGL", "sector_peer", 0.7),

    # Automotive & EV
    ("TSLA", "F", "direct_competitor", 0.9),
    ("TSLA", "GM", "direct_competitor", 0.9),
    ("TSLA", "TM", "direct_competitor", 0.9),
    ("TSLA", "RIVN", "direct_competitor", 1.0),
    ("F", "GM", "direct_competitor", 1.0),
    ("F", "TM", "direct_competitor", 0.9),
    ("GM", "TM", "direct_competitor", 0.9),
    ("RIVN", "F", "direct_competitor", 0.8),

    # Retail & Consumer Goods
    ("AMZN", "WMT", "direct_competitor", 1.0),
    ("WMT", "TGT", "direct_competitor", 1.0),
    ("WMT", "COST", "direct_competitor", 0.9),
    ("TGT", "COST", "direct_competitor", 0.8),
    ("HD", "LOW", "direct_competitor", 1.0),
    ("NKE", "LULU", "direct_competitor", 0.9),
    ("MCD", "SBUX", "sector_peer", 0.7),
    ("KO", "PEP", "direct_competitor", 1.0),
    ("PG", "KO", "sector_peer", 0.6),

    # Mega Banks & Payments
    ("JPM", "BAC", "direct_competitor", 1.0),
    ("JPM", "WFC", "direct_competitor", 0.9),
    ("JPM", "C", "direct_competitor", 0.9),
    ("JPM", "GS", "direct_competitor", 0.9),
    ("JPM", "MS", "direct_competitor", 0.9),
    ("BAC", "WFC", "direct_competitor", 1.0),
    ("BAC", "C", "direct_competitor", 0.9),
    ("GS", "MS", "direct_competitor", 1.0),
    ("V", "MA", "direct_competitor", 1.0),
    ("BRK.B", "JPM", "sector_peer", 0.7),

    # Energy: Oil & Gas Majors
    ("XOM", "CVX", "direct_competitor", 1.0),
    ("XOM", "COP", "direct_competitor", 0.8),
    ("CVX", "COP", "direct_competitor", 0.8),
    ("COP", "EOG", "direct_competitor", 0.9),
    ("SLB", "XOM", "sector_peer", 0.7),

    # Health Care: Pharma & Medical Devices
    ("LLY", "JNJ", "direct_competitor", 0.9),
    ("LLY", "PFE", "direct_competitor", 0.9),
    ("LLY", "MRK", "direct_competitor", 0.9),
    ("JNJ", "PFE", "direct_competitor", 1.0),
    ("JNJ", "ABBV", "direct_competitor", 0.9),
    ("PFE", "MRK", "direct_competitor", 1.0),
    ("MRK", "ABBV", "direct_competitor", 0.9),
    ("ABT", "ISRG", "sector_peer", 0.7),
    ("JNJ", "ABT", "direct_competitor", 0.8),

    # Aerospace & Defense & Machinery
    ("BA", "LMT", "direct_competitor", 0.8),
    ("BA", "RTX", "direct_competitor", 0.8),
    ("LMT", "RTX", "direct_competitor", 1.0),
    ("GE", "RTX", "direct_competitor", 0.9),
    ("CAT", "DE", "direct_competitor", 0.9),

    # Streaming & Telecom
    ("NFLX", "DIS", "direct_competitor", 1.0),
    ("NFLX", "AMZN", "direct_competitor", 0.8),
    ("DIS", "CMCSA", "direct_competitor", 0.9),
    ("TMUS", "VZ", "direct_competitor", 1.0),
    ("TMUS", "T", "direct_competitor", 1.0),
    ("VZ", "T", "direct_competitor", 1.0),
]


def get_seed_companies() -> list[CompanyRecord]:
    """Generate normalized CompanyRecord instances."""
    return [
        CompanyRecord(
            ticker=c["ticker"],
            name=c["name"],
            sector=c["sector"],
            industry=c["industry"],
            country_code="USA",
            market_cap_tier=c["tier"],
            description=c["desc"],
        )
        for c in COMPANIES_DATA
    ]


def get_seed_competitors() -> list[CompetitorRecord]:
    """Generate bidirectional competitor links."""
    records: list[CompetitorRecord] = []
    seen: set[tuple[str, str]] = set()

    for a, b, rel, weight in COMPETITOR_PAIRINGS:
        # A -> B
        if (a, b) not in seen:
            records.append(
                CompetitorRecord(company_ticker=a, competitor_ticker=b, relationship_type=rel, weight=weight)
            )
            seen.add((a, b))
        # B -> A (Bidirectional rivalry)
        if (b, a) not in seen:
            records.append(
                CompetitorRecord(company_ticker=b, competitor_ticker=a, relationship_type=rel, weight=weight)
            )
            seen.add((b, a))

    return records
