"""
Strategy Outcome and Lesson Learning models.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class OutcomeComparison(BaseModel):
    metric: str
    expected_direction: str = Field(..., description="higher | lower | stable | above_baseline")
    actual_value: Optional[float] = None
    historical_baseline_value: Optional[float] = None
    relative_difference_percent: Optional[float] = None
    observation: str


class StrategyOutcomeAnalysis(BaseModel):
    outcome_id: str
    strategy_id: str
    brand_id: str
    analysis_timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metric_comparisons: List[OutcomeComparison]
    observed_difference: str = Field(
        ..., description="Objective synthesis of differences between plan and performance"
    )
    extracted_reusable_lesson: str = Field(
        ..., description="High-signal, non-causal strategic takeaway for Hindsight memory"
    )
    hindsight_memory_id: Optional[str] = None
    raw_analytics_summary: Dict[str, Any] = Field(default_factory=dict)
