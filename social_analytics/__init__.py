"""
Social Media Analytics Engine.
Deterministic data normalization, metric calculation, baselines, observations, and structured contracts.
"""

from social_analytics.engine import (
    SocialMediaAnalyticsEngine,
    compare_item_to_baseline,
    compute_account_baseline,
)
from social_analytics.models import (
    AccountInfo,
    AccountSummary,
    AnalyticsResult,
    AudienceMetrics,
    BaselineComparison,
    BaselineMetrics,
    ContentPerformanceItem,
    ContentSummary,
    ContentTypePerformance,
    DataQuality,
    GrowthSummary,
    MetricChange,
    NormalizedContent,
    Observation,
    PeriodComparison,
    PeriodInfo,
)
from social_analytics.providers import (
    BaseSocialProvider,
    InstagramProvider,
    RedditProvider,
    YouTubeProvider,
)

__all__ = [
    "SocialMediaAnalyticsEngine",
    "BaseSocialProvider",
    "YouTubeProvider",
    "InstagramProvider",
    "RedditProvider",
    "NormalizedContent",
    "AccountInfo",
    "AudienceMetrics",
    "AnalyticsResult",
    "AccountSummary",
    "PeriodInfo",
    "ContentSummary",
    "GrowthSummary",
    "BaselineMetrics",
    "BaselineComparison",
    "ContentPerformanceItem",
    "ContentTypePerformance",
    "MetricChange",
    "PeriodComparison",
    "Observation",
    "DataQuality",
    "compute_account_baseline",
    "compare_item_to_baseline",
]
