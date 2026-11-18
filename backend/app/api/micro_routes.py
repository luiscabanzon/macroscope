from fastapi import APIRouter, HTTPException, Query, status

from app.schemas.micro import (
    CompanyFundamentalsResponse,
    CompetitorBenchmarkResponse,
)
from app.services.fundamentals import FundamentalsService

router = APIRouter(prefix="/companies", tags=["Micro Fundamentals & Benchmarking"])
fundamentals_service = FundamentalsService()


@router.get("/{ticker}/fundamentals", response_model=CompanyFundamentalsResponse)
async def get_company_fundamentals(ticker: str) -> CompanyFundamentalsResponse:
    """Retrieve full company financial statement history, margins, and LTM summary."""
    data = await fundamentals_service.get_fundamentals(ticker)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker.upper()}' not found in database",
        )
    return data


@router.get("/{ticker}/benchmark", response_model=CompetitorBenchmarkResponse)
async def get_competitor_benchmark(
    ticker: str,
    metric: str = Query(
        "operating_margin",
        description="Metric to compare: operating_margin, net_margin, gross_margin, rnd_intensity, revenue_growth_yoy",
    ),
) -> CompetitorBenchmarkResponse:
    """Compare selected financial metric across direct peer rivals."""
    data = await fundamentals_service.get_competitor_benchmark(ticker, metric=metric)
    if not data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with ticker '{ticker.upper()}' not found or has no peer data",
        )
    return data
