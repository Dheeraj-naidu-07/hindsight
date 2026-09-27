"""
Contract models defining the final, stable JSON output consumed by downstream
services and backend orchestrators without requiring knowledge of raw social APIs.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class AccountSummary(BaseModel):
    """Account identity and snapshot summary."""
    model_config = ConfigDict(extra="ignore")

    platform: Literal["youtube", "instagram", "reddit"]
    account_id: str
    username: str
    display_name: Optional[str] = None
    current_followers: Optional[int] = None
    total_posts_analyzed: int


class PeriodInfo(BaseModel):
    """Analysis timeframe details."""
    model_config = ConfigDict(extra="ignore")

    start_date: str = Field(..., description="ISO 8601 formatted start timestamp")
    end_date: str = Field(..., description="ISO 8601 formatted end timestamp")
    days: float = Field(..., description="Exact duration of period in decimal days")


class ContentSummary(BaseModel):
    """Deterministic volume, aggregate engagement, and rate metrics."""
    model_config = ConfigDict(extra="ignore")

    total_posts: int
    posts_by_type: Dict[str, int]
    total_views: Optional[int] = None
    total_engagements: int
    average_engagement_per_content: float
    median_views: Optional[float] = None
    median_engagements: float
    median_engagement_rate: Optional[float] = None
    engagement_rate_basis: Optional[str] = Field(
        None, description="'reach' | 'impressions' | None. Explicitly notes denominator used."
    )
    like_rate: Optional[float] = None
    comment_rate: Optional[float] = None
    share_rate: Optional[float] = None
    save_rate: Optional[float] = None
    view_rate: Optional[float] = None
    posting_frequency_per_day: float
    posting_frequency_per_week: float


class GrowthSummary(BaseModel):
    """Follower/subscriber trajectory over the period."""
    model_config = ConfigDict(extra="ignore")

    followers_start: Optional[int] = None
    followers_end: Optional[int] = None
    absolute_follower_growth: Optional[int] = None
    percentage_follower_growth: Optional[float] = None


class BaselineMetrics(BaseModel):
    """Historical account medians used as reference standards."""
    model_config = ConfigDict(extra="ignore")

    median_views: Optional[float] = None
    median_engagements: float
    median_engagement_rate: Optional[float] = None
    median_shares: Optional[float] = None
    median_comments: Optional[float] = None
    sample_size: int


class BaselineComparison(BaseModel):
    """Item comparison against historical baseline."""
    model_config = ConfigDict(extra="ignore")

    metric: str
    content_value: Optional[float] = None
    historical_median: Optional[float] = None
    relative_difference_percent: Optional[float] = None


class ContentPerformanceItem(BaseModel):
    """Ranked piece of content with baseline relative delta."""
    model_config = ConfigDict(extra="ignore")

    content_id: str
    title: Optional[str] = None
    content_type: str
    published_at: str
    views: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    total_engagements: int
    engagement_rate: Optional[float] = None
    engagement_rate_basis: Optional[str] = None
    baseline_comparison: BaselineComparison


class ContentTypePerformance(BaseModel):
    """Performance breakdown grouped by content type."""
    model_config = ConfigDict(extra="ignore")

    count: int
    median_views: Optional[float] = None
    median_engagements: float
    median_engagement_rate: Optional[float] = None
    engagement_rate_basis: Optional[str] = None
    share_of_total_content_pct: float


class MetricChange(BaseModel):
    """
    Representation of change between periods.
    Carefully distinguishes percentage-point change from relative percentage change.
    """
    model_config = ConfigDict(extra="ignore")

    current_value: Optional[float] = None
    previous_value: Optional[float] = None
    absolute_change: Optional[float] = None
    percentage_points_change: Optional[float] = Field(
        None, description="Arithmetic difference (Current% - Previous%) in pp. Only for rate metrics."
    )
    relative_change_percent: Optional[float] = Field(
        None, description="Relative difference ((Current - Previous) / Previous) * 100 in %."
    )


class PeriodComparison(BaseModel):
    """Side-by-side comparison between Current Period and Previous Period."""
    model_config = ConfigDict(extra="ignore")

    has_previous_period: bool
    previous_period: Optional[PeriodInfo] = None
    views_change: Optional[MetricChange] = None
    engagement_change: Optional[MetricChange] = None
    engagement_rate_change: Optional[MetricChange] = None
    follower_change: Optional[MetricChange] = None
    posting_frequency_change: Optional[MetricChange] = None
    median_performance_change: Dict[str, Optional[MetricChange]] = Field(default_factory=dict)


class Observation(BaseModel):
    """
    Measurable, data-driven observation backed by evidence and sample sizes.
    Free from subjective marketing recommendations or causal claims.
    """
    model_config = ConfigDict(extra="ignore")

    type: str = Field(
        ...,
        description="'content_type_comparison' | 'period_trend' | 'baseline_comparison' | 'topic_comparison' | 'engagement_distribution'"
    )
    observation: str = Field(..., description="Factual, non-causal statement")
    evidence: Dict[str, Any] = Field(
        ...,
        description="Structured supporting numerical data including metrics and sample sizes"
    )


class DataQuality(BaseModel):
    """Audit trail of data completeness, sample size sufficiency, and warnings."""
    model_config = ConfigDict(extra="ignore")

    source_platform: Literal["youtube", "instagram", "reddit"]
    collection_timestamp: str
    analysis_period: Dict[str, Any]
    sample_size: int
    insufficient_sample_size: bool
    missing_metrics: List[str]
    unavailable_metrics: List[str]
    data_quality_warnings: List[str]


class AnalyticsResult(BaseModel):
    """
    Final JSON contract representing the complete analytics deliverable.
    """
    model_config = ConfigDict(extra="ignore")

    account: AccountSummary
    period: PeriodInfo
    content_summary: ContentSummary
    growth: GrowthSummary
    baseline: BaselineMetrics
    top_content: List[ContentPerformanceItem]
    bottom_content: List[ContentPerformanceItem]
    content_type_performance: Dict[str, ContentTypePerformance]
    period_comparison: PeriodComparison
    observations: List[Observation]
    platform_specific_metrics: Dict[str, Any]
    data_quality: DataQuality
