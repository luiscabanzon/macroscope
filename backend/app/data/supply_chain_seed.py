"""Curated NASDAQ 100 and S&P 500 company universe supply chain linkages."""

from app.db.models import SupplyChainRecord

# 1. High-Impact Enterprise Supply Chain Linkages
# Format: (supplier_ticker, customer_ticker, product_category, tier_or_importance, weight)
SUPPLY_CHAIN_PAIRINGS: list[tuple[str, str, str, str, float]] = [
    # --- Semiconductor & AI Hardware Value Chain ---
    ("ASML", "TSM", "EUV & DUV Photolithography Scanners", "critical", 1.0),
    ("ASML", "INTC", "High-NA & EUV Lithography Systems", "critical", 0.95),
    ("ASML", "MU", "Extreme Ultraviolet Lithography Systems", "critical", 0.9),
    ("AMAT", "TSM", "Wafer Deposition & CMP Fabrication Equipment", "critical", 0.95),
    ("AMAT", "INTC", "Wafer Fabrication Equipment & Metrology", "critical", 0.9),
    ("AMAT", "MU", "Memory Wafer Fabrication Equipment", "critical", 0.9),
    ("LRCX", "TSM", "Advanced Dielectric & Conductor Etch Systems", "critical", 0.95),
    ("LRCX", "INTC", "Semiconductor Wafer Etch Tools", "critical", 0.9),
    ("LRCX", "MU", "High-Aspect-Ratio Memory Etch Equipment", "critical", 0.95),
    ("TSM", "NVDA", "Advanced Node Wafer Foundry (CoWoS / 4N / 3nm)", "critical", 1.0),
    ("TSM", "AAPL", "A-Series & M-Series Silicon Wafer Foundry (3nm)", "critical", 1.0),
    ("TSM", "AMD", "Zen & Instinct Advanced Packaging Foundry", "critical", 1.0),
    ("TSM", "QCOM", "Snapdragon Mobile Application Processors Foundry", "critical", 0.95),
    ("TSM", "AVGO", "Custom Silicon & ASIC Fabrication (3nm/5nm)", "critical", 0.95),
    ("MU", "NVDA", "HBM3e High Bandwidth Memory for Blackwell GPUs", "critical", 0.95),
    ("MU", "AMD", "HBM3 Memory for MI300X AI Accelerators", "critical", 0.9),
    ("MU", "AAPL", "LPDDR5X Low-Power Memory for iPhone & Mac", "major", 0.85),
    ("NVDA", "MSFT", "Data Center AI GPUs (H100/H200/Blackwell) for Azure", "critical", 1.0),
    ("NVDA", "AMZN", "AWS EC2 UltraClusters (H100 GPUs & InfiniBand)", "critical", 1.0),
    ("NVDA", "META", "Grand Teton AI Training Clusters (H100/B200)", "critical", 1.0),
    ("NVDA", "GOOGL", "Google Cloud A3 High-Compute GPU Instances", "major", 0.9),
    ("NVDA", "TSLA", "Dojo & Cortex Autonomous AI Training Superclusters", "major", 0.9),
    ("AMD", "MSFT", "EPYC Server Processors & MI300X Accelerators for Azure", "major", 0.9),
    ("AMD", "AMZN", "AWS EC2 EPYC-Powered Cloud Compute Instances", "major", 0.85),
    ("AVGO", "GOOGL", "Custom TPU AI Silicon Co-Design & Optical Interconnects", "critical", 0.95),
    ("AVGO", "META", "Custom MTIA Silicon & Tomahawk Networking Switches", "critical", 0.9),
    ("AVGO", "AAPL", "5G RF Wireless & Connectivity Components", "major", 0.9),
    ("QCOM", "AAPL", "Snapdragon 5G Mobile Baseband Modems", "major", 0.85),
    ("TXN", "TSLA", "Automotive Analog Power ICs & Battery Management", "major", 0.85),
    ("TXN", "F", "Analog Microcontrollers & Body Electronics ICs", "major", 0.8),
    ("TXN", "GM", "Automotive Powertrain & Telematics Semiconductors", "major", 0.8),
    ("TXN", "BA", "Aerospace-Grade Analog & High-Reliability ICs", "standard", 0.75),
    ("TXN", "CAT", "Industrial Automation & Heavy Equipment Sensors", "standard", 0.75),

    # --- Automotive & Mobility Value Chain ---
    ("TSLA", "F", "NACS Supercharger Network Access & EV Fast-Charging", "major", 0.8),
    ("TSLA", "GM", "NACS Fast-Charging Network Interoperability", "major", 0.8),
    ("TSLA", "RIVN", "North American Charging Standard (NACS) Network Access", "major", 0.8),

    # --- Aerospace & Defense Value Chain ---
    ("GE", "BA", "Commercial Turbofan Engines (LEAP-1B for 737 MAX, GE9X)", "critical", 1.0),
    ("RTX", "BA", "Pratt & Whitney Geared Turbofans & Collins Avionics", "critical", 0.95),
    ("RTX", "LMT", "Missile Propulsion & F-35 Tactical Communications", "critical", 0.95),

    # --- Energy & Resources Upstream Value Chain ---
    ("SLB", "XOM", "Upstream Drilling Tech, MWD & Subsea Production", "critical", 0.95),
    ("SLB", "CVX", "Directional Drilling & Digital Reservoir Characterization", "critical", 0.95),
    ("SLB", "COP", "Unconventional Shale Hydraulic Fracturing Services", "major", 0.9),
    ("SLB", "EOG", "Smart Completion Technology & Horizontal Drilling", "major", 0.9),

    # --- Cloud Infrastructure & Cybersecurity Value Chain ---
    ("AMZN", "NFLX", "AWS Global Cloud Infrastructure & CDN Edge Streaming", "critical", 1.0),
    ("AMZN", "CRWD", "AWS Cloud Compute for Falcon Threat Graph Analysis", "major", 0.85),
    ("AMZN", "SNOW", "AWS Infrastructure Hosting for Snowflake Data Cloud", "critical", 0.95),
    ("AMZN", "RIVN", "AWS Automotive Cloud & Connected Vehicle Telematics", "major", 0.85),
    ("MSFT", "NOW", "Azure Cloud Infrastructure & Enterprise Copilot APIs", "major", 0.85),
    ("MSFT", "SNOW", "Azure Infrastructure & Data Cloud Integrations", "critical", 0.95),
    ("MSFT", "ADBE", "Azure Cloud for Adobe Experience & Creative Cloud", "major", 0.85),
    ("CRWD", "JPM", "Global Cyber Defense & Endpoint Threat Monitoring", "critical", 0.95),
    ("CRWD", "BAC", "Institutional Cyber Threat Mitigation & Incident Response", "critical", 0.9),
    ("CRWD", "WMT", "Retail Edge Device & Point-of-Sale Endpoint Security", "critical", 0.9),
    ("PANW", "JPM", "Enterprise Next-Gen Firewalls & Cloud Security", "critical", 0.9),
    ("PANW", "BAC", "Banking Network Security & Zero-Trust Architecture", "critical", 0.9),

    # --- Payment Rails & Retail Wholesale Distribution ---
    ("V", "AMZN", "Global Consumer Payment Card Processing Rails", "critical", 0.95),
    ("V", "WMT", "Omnichannel Card Transaction Clearing & Settlement", "critical", 0.95),
    ("V", "COST", "Exclusive In-Warehouse Credit Card Acceptance (Visa)", "critical", 1.0),
    ("MA", "AMZN", "E-Commerce Transaction Network & Mastercard Rails", "critical", 0.95),
    ("MA", "WMT", "Global Point-of-Sale Payment Card Clearing", "critical", 0.95),
    ("KO", "MCD", "Exclusive Fountain Beverage Syrups & Dispenser Systems", "critical", 1.0),
    ("KO", "WMT", "Beverage Wholesale Direct-Store-Delivery Distribution", "critical", 0.95),
    ("PEP", "WMT", "Frito-Lay Snacks & Beverage Wholesale Distribution", "critical", 0.95),
    ("KO", "COST", "Bulk Packaged Beverage Supply & Warehouse Distribution", "major", 0.9),
    ("PEP", "COST", "Snack Foods & Packaged Beverage Warehouse Supply", "major", 0.9),
]


def get_seed_supply_chain() -> list[SupplyChainRecord]:
    """Generate normalized SupplyChainRecord instances."""
    return [
        SupplyChainRecord(
            supplier_ticker=supplier,
            customer_ticker=customer,
            product_category=category,
            tier_or_importance=tier,
            weight=weight,
        )
        for supplier, customer, category, tier, weight in SUPPLY_CHAIN_PAIRINGS
    ]
