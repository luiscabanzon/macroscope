from collections import defaultdict
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, status

from app.config import settings
from app.db.database import get_connection
from app.schemas.macro import (
    ComparisonDataPoint,
    ComparisonResponse,
    CountryInfo,
    DashboardResponse,
    IndicatorSeriesResponse,
    KpiSnapshot,
    ObservationPoint,
    RefreshResponse,
)
from app.services.cache_manager import CacheManager, INDICATOR_METADATA

router = APIRouter()
cache_manager = CacheManager()

# Curated Country Registry
SUPPORTED_COUNTRIES: list[CountryInfo] = [
    CountryInfo(code="USA", name="United States", region="North America", indicators=list(INDICATOR_METADATA.keys())),
    CountryInfo(code="GBR", name="United Kingdom", region="Europe", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="DEU", name="Germany", region="Europe", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="FRA", name="France", region="Europe", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="JPN", name="Japan", region="Asia", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="CAN", name="Canada", region="North America", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="ITA", name="Italy", region="Europe", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="CHN", name="China", region="Asia", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="IND", name="India", region="Asia", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="BRA", name="Brazil", region="South America", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="AUS", name="Australia", region="Oceania", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="KOR", name="South Korea", region="Asia", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="ESP", name="Spain", region="Europe", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="MEX", name="Mexico", region="North America", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
    CountryInfo(code="ZAF", name="South Africa", region="Africa", indicators=["gdp_growth", "inflation_cpi", "unemployment_rate", "bank_npl_ratio", "gov_debt_gdp", "oil_brent"]),
]

COUNTRY_MAP: dict[str, CountryInfo] = {c.code: c for c in SUPPORTED_COUNTRIES}

DASHBOARD_INDICATORS = [
    "gdp_growth",
    "inflation_cpi",
    "unemployment_rate",
    "interest_rate",
    "bank_npl_ratio",
    "auto_sales",
    "oil_brent",
]


@router.get("/health", tags=["System"])
async def health_check() -> dict[str, str]:
    """Check API readiness and database health."""
    try:
        async with get_connection(cache_manager.db_path) as conn:
            async with conn.execute("SELECT count(*) FROM observations") as cursor:
                row = await cursor.fetchone()
                obs_count = row[0] if row else 0
        return {
            "status": "healthy",
            "app": settings.app_name,
            "version": settings.app_version,
            "read_only_cache": str(settings.read_only_cache),
            "cached_observations": str(obs_count),
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connectivity check failed: {exc}",
        )


@router.get("/countries", response_model=list[CountryInfo], tags=["Metadata"])
async def get_countries() -> list[CountryInfo]:
    """Retrieve all supported countries and their indicator mappings."""
    return SUPPORTED_COUNTRIES


@router.get("/dashboard/{country_code}", response_model=DashboardResponse, tags=["Dashboard"])
async def get_dashboard(country_code: str) -> DashboardResponse:
    """Retrieve full dashboard data for a country including KPI ribbons and time-series."""
    iso3 = country_code.upper()
    country_info = COUNTRY_MAP.get(iso3)
    country_name = country_info.name if country_info else iso3

    kpis: list[KpiSnapshot] = []
    series_dict: dict[str, IndicatorSeriesResponse] = {}
    is_any_stale = False
    latest_update_ts: str | None = None

    for indicator_slug in DASHBOARD_INDICATORS:
        records, is_stale, last_updated = await cache_manager.get_series(
            country_code=iso3,
            indicator_slug=indicator_slug,
        )

        if is_stale:
            is_any_stale = True
        if last_updated and (latest_update_ts is None or last_updated > latest_update_ts):
            latest_update_ts = last_updated

        meta = INDICATOR_METADATA.get(indicator_slug, {})
        ind_name = meta.get("name", indicator_slug)
        default_unit = meta.get("default_unit", "")
        default_src = meta.get("default_source", "")

        if not records:
            continue

        unit = records[-1].unit if records else default_unit
        source = records[-1].source if records else default_src
        frequency = records[-1].frequency if records else "A"

        # Calculate KPI snapshot
        latest_obs = records[-1]
        latest_val = latest_obs.value
        prev_obs = records[-2] if len(records) > 1 else None
        prev_val = prev_obs.value if prev_obs else None

        delta_mom: float | None = None
        delta_yoy: float | None = None

        if frequency in {"M", "D"}:
            if prev_val is not None:
                delta_mom = round(latest_val - prev_val, 3)
            # Find point from ~12 months prior for YoY
            if len(records) >= 13:
                delta_yoy = round(latest_val - records[-13].value, 3)
            elif prev_val is not None:
                delta_yoy = round(latest_val - prev_val, 3)
        else:
            # Annual
            if prev_val is not None:
                delta_yoy = round(latest_val - prev_val, 3)

        kpis.append(
            KpiSnapshot(
                indicator_slug=indicator_slug,
                indicator_name=ind_name,
                latest_value=latest_val,
                period_date=latest_obs.period_date,
                previous_value=prev_val,
                delta_yoy=delta_yoy,
                delta_mom=delta_mom,
                unit=unit,
                source=source,
                is_stale=is_stale,
            )
        )

        series_dict[indicator_slug] = IndicatorSeriesResponse(
            indicator_slug=indicator_slug,
            indicator_name=ind_name,
            country_code=iso3,
            unit=unit,
            frequency=frequency,
            source=source,
            is_stale=is_stale,
            last_updated=last_updated,
            data=[ObservationPoint(period_date=r.period_date, value=r.value) for r in records],
        )

    return DashboardResponse(
        country_code=iso3,
        country_name=country_name,
        last_updated=latest_update_ts,
        is_stale=is_any_stale,
        kpis=kpis,
        series=series_dict,
    )


@router.get("/compare", response_model=ComparisonResponse, tags=["Comparison"])
async def compare_countries(
    countries: str = Query(..., description="Comma-separated ISO-3 codes e.g. USA,GBR,DEU"),
    indicator: str = Query("inflation_cpi", description="Indicator slug to compare"),
    start_year: str | None = Query(None, description="Starting year filter e.g. 2015"),
) -> ComparisonResponse:
    """Retrieve side-by-side aligned time-series for multi-country charting."""
    country_list = [c.strip().upper() for c in countries.split(",") if c.strip()]
    if not country_list:
        raise HTTPException(status_code=400, detail="At least one country must be specified")

    start_date = f"{start_year}-01-01" if start_year else None
    meta = INDICATOR_METADATA.get(indicator, {})
    ind_name = meta.get("name", indicator)
    unit = meta.get("default_unit", "%")

    # Map of period_date -> {country_code: value}
    points_by_date: dict[str, dict[str, float]] = defaultdict(dict)

    for country in country_list:
        records, _, _ = await cache_manager.get_series(
            country_code=country,
            indicator_slug=indicator,
            start_date=start_date,
        )
        for r in records:
            points_by_date[r.period_date][country] = r.value
            if r.unit:
                unit = r.unit

    sorted_dates = sorted(points_by_date.keys())
    data_points = [
        ComparisonDataPoint(period_date=d, values=points_by_date[d])
        for d in sorted_dates
    ]

    return ComparisonResponse(
        indicator_slug=indicator,
        indicator_name=ind_name,
        unit=unit,
        countries=country_list,
        data=data_points,
    )


@router.post("/refresh/{country_code}", response_model=RefreshResponse, tags=["Cache Management"])
async def refresh_cache(country_code: str) -> RefreshResponse:
    """Trigger an on-demand cache refresh for a country's indicators."""
    if settings.read_only_cache:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cache refresh is disabled in READ_ONLY_CACHE public demo mode",
        )

    iso3 = country_code.upper()
    refreshed: list[str] = []

    for ind in DASHBOARD_INDICATORS:
        provider = cache_manager.registry.get_provider(ind, iso3)
        if provider:
            await cache_manager.get_series(
                country_code=iso3,
                indicator_slug=ind,
                force_refresh=True,
            )
            refreshed.append(ind)

    return RefreshResponse(
        country_code=iso3,
        status="SUCCESS",
        refreshed_indicators=refreshed,
    )
