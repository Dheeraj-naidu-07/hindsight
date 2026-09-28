"""
Outcome and Post-Mortem Learning Endpoints.
Executes the feedback loop: Strategy -> Performance -> Learning -> Hindsight Update.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, status
from api.dependencies.deps import get_learning_service
from api.errors.handlers import APIError, NotFoundError
from api.schemas.requests import RecordOutcomeRequest
from api.schemas.responses import OutcomeResponse
from learning.learning_service import LearningService
from services.analytics_service.service import AnalyticsService

router = APIRouter(prefix="/api/v1/strategy", tags=["Outcome & Learning"])


@router.post("/outcome", response_model=OutcomeResponse, status_code=status.HTTP_201_CREATED)
def record_strategy_outcome(
    req: RecordOutcomeRequest,
    learning_service: LearningService = Depends(get_learning_service),
) -> OutcomeResponse:
    try:
        analytics = req.analytics_result
        if analytics is None:
            strategy = learning_service.strategy_repo.get_by_id(req.strategy_id)
            if not strategy:
                raise NotFoundError(f"Strategy with ID '{req.strategy_id}' not found")

            platform = req.platform or (
                strategy.recommended_platforms[0] if strategy.recommended_platforms else "youtube"
            )
            account_id = req.account_id
            if not account_id:
                raise APIError(
                    "account_id is required when analytics_result is omitted",
                    status_code=400,
                )
            now = datetime.now(timezone.utc)
            start = now - timedelta(days=30)
            analytics = AnalyticsService().run_analytics(
                platform=platform,
                account_id=account_id,
                start_date=start,
                end_date=now,
                previous_period_start=start - timedelta(days=30),
                previous_period_end=start,
                api_key=req.platform_api_key,
            )

        analysis = learning_service.process_strategy_outcome(
            strategy_id=req.strategy_id,
            new_analytics=analytics,
        )
        return OutcomeResponse(
            outcome=analysis,
            reusable_lesson_stored=analysis.extracted_reusable_lesson,
            hindsight_memory_id=analysis.hindsight_memory_id,
        )
    except NotFoundError:
        raise
    except ValueError as e:
        raise NotFoundError(str(e))
    except Exception as e:
        raise APIError(f"Failed to process outcome: {e}", status_code=500)
