from collections import defaultdict
from datetime import datetime
import logging
from typing import Any

from app.config import settings
from app.data.cik_mapping import get_cik_for_ticker
from app.db.database import (
    get_company_by_ticker,
    get_company_competitors,
    get_connection,
)
from app.schemas.micro import (
    BenchmarkPoint,
    CompanyFundamentalsResponse,
    CompetitorBenchmarkResponse,
    FinancialPeriodPoint,
    SummaryMetrics,
)
from app.services.cache_manager import CacheManager

logger = logging.getLogger(__name__)

FUNDAMENTAL_SLUGS = [
    "revenue",
    "net_income",
    "operating_income",
    "gross_profit",
    "rnd_expense",
]

METRIC_LABELS: dict[str, dict[str, str]] = {
    "operating_margin": {"name": "Operating Margin", "unit": "%"},
    "net_margin": {"name": "Net Profit Margin", "unit": "%"},
    "gross_margin": {"name": "Gross Margin", "unit": "%"},
    "rnd_intensity": {"name": "R&D Intensity", "unit": "%"},
    "revenue_growth_yoy": {"name": "YoY Revenue Growth", "unit": "%"},
    "revenue": {"name": "Revenue", "unit": "USD"},
}


def normalize_to_calendar_quarter(date_str: str) -> str:
    """Normalize irregular fiscal period end dates to standard calendar quarter end dates."""
    try:
        parts = [int(p) for p in date_str.split("-")]
        year, month = parts[0], parts[1]
        if month == 1:
            return f"{year - 1}-12-31"
        elif month in (2, 3, 4):
            return f"{year}-03-31"
        elif month in (5, 6, 7):
            return f"{year}-06-30"
        elif month in (8, 9, 10):
            return f"{year}-09-30"
        else:
            return f"{year}-12-31"
    except Exception:
        return date_str


class FundamentalsService:
    """Service calculating financial ratios, statement trends, and peer competitor benchmarks."""

    def __init__(
        self,
        cache_manager: CacheManager | None = None,
        db_path: str | None = None,
    ) -> None:
        self.cache_manager = cache_manager or CacheManager(db_path=db_path)
        self.db_path = db_path or settings.db_path

    async def get_fundamentals(self, ticker: str) -> CompanyFundamentalsResponse | None:
        """Retrieve complete financial statement history and ratios for a company."""
        clean_ticker = ticker.upper()

        async with get_connection(self.db_path) as conn:
            company = await get_company_by_ticker(conn, clean_ticker)
            if not company:
                return None

        # Map: (frequency, period_date) -> dict of {slug: value}
        points_map: dict[tuple[str, str], dict[str, float]] = defaultdict(dict)

        for slug in FUNDAMENTAL_SLUGS:
            records, _, _ = await self.cache_manager.get_series(
                country_code=clean_ticker,
                indicator_slug=slug,
            )
            for r in records:
                points_map[(r.frequency, r.period_date)][slug] = r.value

        annual_points: list[FinancialPeriodPoint] = []
        quarterly_points: list[FinancialPeriodPoint] = []

        # Sort dates chronologically
        sorted_keys = sorted(points_map.keys(), key=lambda k: k[1])

        # Calculate ratios and YoY growth
        prev_annual_rev: float | None = None
        quarterly_rev_history: list[tuple[str, float]] = []

        for (freq, date) in sorted_keys:
            vals = points_map[(freq, date)]
            rev = vals.get("revenue")
            net = vals.get("net_income")
            op = vals.get("operating_income")
            gp = vals.get("gross_profit")
            rnd = vals.get("rnd_expense")

            # Margin calculations
            gm = round((gp / rev) * 100, 2) if gp is not None and rev and rev > 0 else None
            om = round((op / rev) * 100, 2) if op is not None and rev and rev > 0 else None
            nm = round((net / rev) * 100, 2) if net is not None and rev and rev > 0 else None
            rndi = round((rnd / rev) * 100, 2) if rnd is not None and rev and rev > 0 else None

            # Revenue Growth YoY
            rev_growth: float | None = None
            if freq == "A":
                if rev is not None and prev_annual_rev and prev_annual_rev > 0:
                    rev_growth = round(((rev - prev_annual_rev) / prev_annual_rev) * 100, 2)
                if rev is not None:
                    prev_annual_rev = rev

                annual_points.append(
                    FinancialPeriodPoint(
                        period_date=date,
                        frequency="A",
                        revenue=rev,
                        net_income=net,
                        operating_income=op,
                        gross_profit=gp,
                        rnd_expense=rnd,
                        gross_margin=gm,
                        operating_margin=om,
                        net_margin=nm,
                        rnd_intensity=rndi,
                        revenue_growth_yoy=rev_growth,
                    )
                )
            else:
                # Quarterly
                if rev is not None:
                    if len(quarterly_rev_history) >= 4:
                        prior_rev = quarterly_rev_history[-4][1]
                        if prior_rev > 0:
                            rev_growth = round(((rev - prior_rev) / prior_rev) * 100, 2)
                    quarterly_rev_history.append((date, rev))

                quarterly_points.append(
                    FinancialPeriodPoint(
                        period_date=date,
                        frequency="Q",
                        revenue=rev,
                        net_income=net,
                        operating_income=op,
                        gross_profit=gp,
                        rnd_expense=rnd,
                        gross_margin=gm,
                        operating_margin=om,
                        net_margin=nm,
                        rnd_intensity=rndi,
                        revenue_growth_yoy=rev_growth,
                    )
                )

        # Compute Summary LTM Metrics
        summary = self._compute_summary_metrics(annual_points, quarterly_points)

        return CompanyFundamentalsResponse(
            ticker=clean_ticker,
            company_name=company.name,
            sector=company.sector,
            industry=company.industry,
            cik=get_cik_for_ticker(clean_ticker),
            summary_metrics=summary,
            annual_series=annual_points,
            quarterly_series=quarterly_points,
        )

    def _compute_summary_metrics(
        self,
        annual: list[FinancialPeriodPoint],
        quarterly: list[FinancialPeriodPoint],
    ) -> SummaryMetrics:
        """Compute rolling LTM revenue and latest margin health."""
        ltm_rev: float | None = None
        rev_growth: float | None = None
        op_margin: float | None = None
        net_margin: float | None = None
        gross_margin: float | None = None
        rnd_intensity: float | None = None

        if quarterly and len(quarterly) >= 4:
            last_4 = quarterly[-4:]
            ltm_rev = sum(q.revenue for q in last_4 if q.revenue is not None)
            latest = quarterly[-1]
            op_margin = latest.operating_margin
            net_margin = latest.net_margin
            gross_margin = latest.gross_margin
            rnd_intensity = latest.rnd_intensity
            rev_growth = latest.revenue_growth_yoy
        elif annual:
            latest = annual[-1]
            ltm_rev = latest.revenue
            op_margin = latest.operating_margin
            net_margin = latest.net_margin
            gross_margin = latest.gross_margin
            rnd_intensity = latest.rnd_intensity
            rev_growth = latest.revenue_growth_yoy

        return SummaryMetrics(
            ltm_revenue=ltm_rev,
            revenue_growth_yoy=rev_growth,
            operating_margin=op_margin,
            net_margin=net_margin,
            gross_margin=gross_margin,
            rnd_intensity=rnd_intensity,
        )

    async def get_competitor_benchmark(
        self,
        ticker: str,
        metric: str = "operating_margin",
    ) -> CompetitorBenchmarkResponse | None:
        """Compare financial metrics of a company against its direct competitors."""
        clean_ticker = ticker.upper()

        async with get_connection(self.db_path) as conn:
            company = await get_company_by_ticker(conn, clean_ticker)
            if not company:
                return None
            competitor_tuples = await get_company_competitors(conn, clean_ticker)

        # Select top 4 competitors
        peer_tickers = [clean_ticker] + [c[0].ticker for c in competitor_tuples[:4]]
        dates_to_values: dict[str, dict[str, float]] = defaultdict(dict)

        for peer in peer_tickers:
            fundamentals = await self.get_fundamentals(peer)
            if not fundamentals:
                continue

            # Prioritize quarterly series for higher resolution, or annual if quarterly is empty
            series = fundamentals.quarterly_series if fundamentals.quarterly_series else fundamentals.annual_series

            for point in series:
                val = getattr(point, metric, None)
                if val is not None:
                    cal_quarter = normalize_to_calendar_quarter(point.period_date)
                    dates_to_values[cal_quarter][peer] = val

        sorted_dates = sorted(dates_to_values.keys())
        benchmark_points = [
            BenchmarkPoint(period_date=d, values=dates_to_values[d])
            for d in sorted_dates
            if clean_ticker in dates_to_values[d]  # Only include dates where target company has data
        ]

        meta = METRIC_LABELS.get(metric, {"name": metric.replace("_", " ").title(), "unit": "%"})

        return CompetitorBenchmarkResponse(
            target_ticker=clean_ticker,
            metric=metric,
            metric_name=meta["name"],
            unit=meta["unit"],
            competitors=[p for p in peer_tickers if p != clean_ticker],
            data=benchmark_points,
        )
