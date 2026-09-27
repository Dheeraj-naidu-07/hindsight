"""Engine package for social analytics."""

from social_analytics.engine.analytics_engine import SocialMediaAnalyticsEngine
from social_analytics.engine.baselines import (
    compare_item_to_baseline,
    compute_account_baseline,
)
from social_analytics.engine.comparisons import (
    analyze_content_type_performance,
    analyze_topic_performance,
    calculate_metric_change,
    compare_periods,
    rank_content_items,
)
from social_analytics.engine.metrics import (
    calculate_component_rate,
    calculate_engagement_rate,
    calculate_follower_growth,
    calculate_item_engagements,
    calculate_posting_frequency,
    calculate_view_rate,
    resolve_rate_denominator,
    safe_mean,
    safe_median,
)
from social_analytics.engine.observations import (
    compile_all_observations,
    generate_content_type_observations,
    generate_period_trend_observations,
    generate_topic_observations,
)
from social_analytics.engine.quality import assess_data_quality

__all__ = [
    "SocialMediaAnalyticsEngine",
    "compute_account_baseline",
    "compare_item_to_baseline",
    "calculate_metric_change",
    "compare_periods",
    "rank_content_items",
    "analyze_content_type_performance",
    "analyze_topic_performance",
    "calculate_item_engagements",
    "resolve_rate_denominator",
    "calculate_engagement_rate",
    "calculate_component_rate",
    "calculate_view_rate",
    "calculate_follower_growth",
    "calculate_posting_frequency",
    "safe_median",
    "safe_mean",
    "generate_content_type_observations",
    "generate_period_trend_observations",
    "generate_topic_observations",
    "compile_all_observations",
    "assess_data_quality",
]
