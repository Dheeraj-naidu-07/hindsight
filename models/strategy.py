"""
Content Strategy domain models.
Defines structured strategies produced by the agent.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ContentTheme(BaseModel):
    topic: str = Field(..., description="Topic or theme name")
    priority: str = Field("medium", description="Priority level: high | medium | low")
    rationale: str = Field(..., description="Why this topic was selected based on evidence or gap analysis")
    angle: str = Field(..., description="Specific editorial angle or thesis")
    is_gap_fill: bool = Field(False, description="True if this theme addresses an underrepresented content gap")


class RecommendedFormat(BaseModel):
    format_name: str = Field(..., description="Content format (e.g., short, video, carousel, discussion)")
    platform: str = Field(..., description="Target platform")
    recommended_cadence: str = Field(..., description="Cadence (e.g. 2x per week)")
    rationale: str = Field(..., description="Empirical rationale based on historical analytics and memory")


class PostingRecommendations(BaseModel):
    frequency_per_week: float = Field(..., description="Target posts per week")
    optimal_cadence_notes: str = Field(..., description="Cadence guidance")
    platform_allocation: Dict[str, float] = Field(
        default_factory=dict, description="Percentage distribution across platforms"
    )


class RecalledExperienceCitation(BaseModel):
    memory_id: Optional[str] = None
    lesson: str = Field(..., description="The recalled strategic lesson from Hindsight")
    context: Optional[str] = Field(None, description="Context in which this lesson was originally learned")
    influence_on_strategy: str = Field(..., description="How this recalled lesson directly guided this strategy")


class ContentStrategy(BaseModel):
    strategy_id: str = Field(..., description="Unique strategy identifier")
    brand_id: str = Field(..., description="Brand ID")
    objective: str = Field(..., description="Core business / marketing objective")
    target_audience: str = Field(..., description="Target audience definition")
    recommended_platforms: List[str] = Field(..., description="List of focus platforms")
    content_themes: List[ContentTheme] = Field(..., description="Prioritized content themes and angles")
    recommended_formats: List[RecommendedFormat] = Field(..., description="Recommended formats per platform")
    posting_recommendations: PostingRecommendations = Field(..., description="Cadence and volume guidelines")
    rationale: str = Field(..., description="Overall strategic rationale synthesizing facts and memory")
    supporting_analytics: List[Dict[str, Any]] = Field(
        default_factory=list, description="Factual references from AnalyticsResult observations"
    )
    recalled_experiences: List[RecalledExperienceCitation] = Field(
        default_factory=list, description="Explicit citations to recalled Hindsight experiences"
    )
    confidence_and_limitations: List[str] = Field(
        default_factory=list, description="Statistical warnings, sample size limitations, and boundaries"
    )
    suggested_experiments: List[str] = Field(
        default_factory=list, description="Structured hypotheses to test in future posts"
    )
    created_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="ISO 8601 creation timestamp"
    )
