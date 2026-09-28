"""
API Response Schemas.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from models.outcome import StrategyOutcomeAnalysis
from models.strategy import ContentStrategy


class StrategyResponse(BaseModel):
    strategy: ContentStrategy
    analytics_snapshot: Dict[str, Any] = Field(
        default_factory=dict, description="Summary of metrics that grounded this strategy"
    )
    recalled_memories_count: int = Field(0, description="Count of Hindsight memories incorporated")


class OutcomeResponse(BaseModel):
    outcome: StrategyOutcomeAnalysis
    reusable_lesson_stored: str
    hindsight_memory_id: Optional[str] = None


class MemoryListResponse(BaseModel):
    bank_id: str
    count: int
    memories: List[Dict[str, Any]]
