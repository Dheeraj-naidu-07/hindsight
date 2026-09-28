"""
Strategy Endpoints.
Handles generating new grounded strategies and retrieving historical strategies.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Header, Query, status
from agent.orchestrator.agent_orchestrator import ContentStrategyAgentOrchestrator
from api.dependencies.deps import get_orchestrator, get_strategy_repository
from api.errors.handlers import APIError, NotFoundError
from api.schemas.requests import GenerateStrategyRequest
from api.schemas.responses import StrategyResponse
from database.repositories.strategy_repository import StrategyRepository
from models.strategy import (
    ContentStrategy,
    ContentTheme,
    PostingRecommendations,
    RecommendedFormat,
    RecalledExperienceCitation,
)

from datetime import datetime, timezone

router = APIRouter(prefix="/api/v1/strategy", tags=["Strategy"])


def _ensure_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@router.post("/generate", response_model=StrategyResponse, status_code=status.HTTP_200_OK)
def generate_strategy(
    req: GenerateStrategyRequest,
    x_api_key: Optional[str] = Header(None, alias="X-API-Key"),
    x_platform_api_key: Optional[str] = Header(None, alias="X-Platform-API-Key"),
    x_llm_api_key: Optional[str] = Header(None, alias="X-LLM-API-Key"),
    orchestrator: ContentStrategyAgentOrchestrator = Depends(get_orchestrator),
) -> StrategyResponse:
    start_dt = _ensure_utc(req.start_date)
    end_dt = _ensure_utc(req.end_date)

    if start_dt and end_dt and start_dt > end_dt:
        raise APIError("start_date cannot be after end_date", status_code=400)

    platform_key = req.platform_api_key or x_platform_api_key or x_api_key
    llm_key = req.llm_api_key or x_llm_api_key or x_api_key

    strategy, analytics, context = orchestrator.execute_strategy_pipeline(
        brand_id=req.brand_id,
        platform=req.platform,
        account_id=req.account_id,
        objective=req.objective,
        start_date=start_dt,
        end_date=end_dt,
        analytics_result=req.analytics_result,
        custom_brand_profile=req.custom_brand_profile,
        platform_api_key=platform_key,
        llm_api_key=llm_key,
    )

    return StrategyResponse(
        strategy=strategy,
        analytics_snapshot={
            "platform": analytics.account.platform,
            "sample_size": analytics.data_quality.sample_size,
            "median_engagement_rate": analytics.content_summary.median_engagement_rate,
            "basis": analytics.content_summary.engagement_rate_basis,
            "top_formats": context.current_evidence.top_content_formats,
            "gaps_count": len(context.content_gaps),
        },
        recalled_memories_count=len(strategy.recalled_experiences),
    )


@router.get("/history", response_model=List[ContentStrategy])
def list_strategy_history(
    brand_id: str = Query(..., description="Brand ID to filter strategies"),
    limit: int = Query(20, ge=1, le=100),
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
) -> List[ContentStrategy]:
    records = strategy_repo.list_by_brand(brand_id, limit=limit)
    strategies: List[ContentStrategy] = []
    for r in records:
        strategies.append(
            ContentStrategy(
                strategy_id=r.id,
                brand_id=r.brand_id,
                objective=r.objective,
                target_audience=r.target_audience,
                recommended_platforms=r.recommended_platforms,
                content_themes=[ContentTheme(**t) for t in r.content_themes],
                recommended_formats=[RecommendedFormat(**f) for f in r.recommended_formats],
                posting_recommendations=PostingRecommendations(**r.posting_recommendations),
                rationale=r.rationale,
                supporting_analytics=r.supporting_evidence if isinstance(r.supporting_evidence, list) else r.supporting_evidence.get("observations", []),
                recalled_experiences=[RecalledExperienceCitation(**m) for m in r.recalled_memories],
                confidence_and_limitations=(r.confidence_notes or "").split("\n") if r.confidence_notes else [],
                suggested_experiments=r.experiments,
                created_at=r.created_at,
            )
        )
    return strategies


@router.get("/{strategy_id}", response_model=ContentStrategy)
def get_strategy_by_id(
    strategy_id: str,
    strategy_repo: StrategyRepository = Depends(get_strategy_repository),
) -> ContentStrategy:
    r = strategy_repo.get_by_id(strategy_id)
    if not r:
        raise NotFoundError(f"Strategy with ID '{strategy_id}' not found")

    return ContentStrategy(
        strategy_id=r.id,
        brand_id=r.brand_id,
        objective=r.objective,
        target_audience=r.target_audience,
        recommended_platforms=r.recommended_platforms,
        content_themes=[ContentTheme(**t) for t in r.content_themes],
        recommended_formats=[RecommendedFormat(**f) for f in r.recommended_formats],
        posting_recommendations=PostingRecommendations(**r.posting_recommendations),
        rationale=r.rationale,
        supporting_analytics=r.supporting_evidence if isinstance(r.supporting_evidence, list) else r.supporting_evidence.get("observations", []),
        recalled_experiences=[RecalledExperienceCitation(**m) for m in r.recalled_memories],
        confidence_and_limitations=(r.confidence_notes or "").split("\n") if r.confidence_notes else [],
        suggested_experiments=r.experiments,
        created_at=r.created_at,
    )
