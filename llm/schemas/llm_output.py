"""
Structured output schema for LLM strategy generation.
Enforces typed parsing and prevents math hallucinations.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class LLMContentTheme(BaseModel):
    topic: str
    priority: str = Field("medium", description="high | medium | low")
    rationale: str
    angle: str
    is_gap_fill: bool = False


class LLMRecommendedFormat(BaseModel):
    format_name: str
    platform: str
    recommended_cadence: str
    rationale: str


class LLMPostingRecommendations(BaseModel):
    frequency_per_week: float
    optimal_cadence_notes: str
    platform_allocation: Dict[str, float] = Field(default_factory=dict)


class LLMMemoryCitation(BaseModel):
    memory_id: Optional[str] = None
    lesson: str
    influence_on_strategy: str


class LLMStrategyOutput(BaseModel):
    objective: str
    rationale: str
    content_themes: List[LLMContentTheme]
    recommended_formats: List[LLMRecommendedFormat]
    posting_recommendations: LLMPostingRecommendations
    recalled_experience_citations: List[LLMMemoryCitation] = Field(default_factory=list)
    suggested_experiments: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
