"""
Historical baseline calculations and item-to-baseline comparison.
Uses medians to prevent viral outliers from skewing reference standards.
"""

from __future__ import annotations

from typing import List, Optional

from social_analytics.engine.metrics import (
    calculate_engagement_rate,
    calculate_item_engagements,
    resolve_rate_denominator,
    safe_median,
)
from social_analytics.models.normalized import NormalizedContent
from social_analytics.models.output import BaselineComparison, BaselineMetrics


def compute_account_baseline(
    historical_content: List[NormalizedContent],
) -> BaselineMetrics:
    """
    Computes standard historical baseline statistics from a set of historical posts.
    """
    if not historical_content:
        return BaselineMetrics(
            median_views=None,
            median_engagements=0.0,
            median_engagement_rate=None,
            median_shares=None,
            median_comments=None,
            sample_size=0,
        )

    views_list: List[float] = [
        float(item.views) for item in historical_content if item.views is not None
    ]
    engagements_list: List[float] = [
        float(calculate_item_engagements(item)) for item in historical_content
    ]
    shares_list: List[float] = [
        float(item.shares) for item in historical_content if item.shares is not None
    ]
    comments_list: List[float] = [
        float(item.comments) for item in historical_content if item.comments is not None
    ]

    rates_list: List[float] = []
    for item in historical_content:
        denom, _ = resolve_rate_denominator(item)
        if denom is not None and denom > 0:
            eng = calculate_item_engagements(item)
            rate = calculate_engagement_rate(eng, denom)
            if rate is not None:
                rates_list.append(rate)

    return BaselineMetrics(
        median_views=safe_median(views_list),
        median_engagements=safe_median(engagements_list) or 0.0,
        median_engagement_rate=safe_median(rates_list),
        median_shares=safe_median(shares_list),
        median_comments=safe_median(comments_list),
        sample_size=len(historical_content),
    )


def compare_item_to_baseline(
    item: NormalizedContent,
    baseline: BaselineMetrics,
    preferred_metric: str = "engagement_rate",
) -> BaselineComparison:
    """
    Calculates content item performance relative to historical baseline.
    Formula for relative difference percent:
      ((content_value - historical_median) / historical_median) * 100
    """
    content_value: Optional[float] = None
    historical_median: Optional[float] = None

    if preferred_metric == "engagement_rate":
        denom, _ = resolve_rate_denominator(item)
        if denom and denom > 0:
            content_value = calculate_engagement_rate(
                calculate_item_engagements(item), denom
            )
        historical_median = baseline.median_engagement_rate

    elif preferred_metric == "views":
        content_value = float(item.views) if item.views is not None else None
        historical_median = baseline.median_views

    elif preferred_metric == "engagements":
        content_value = float(calculate_item_engagements(item))
        historical_median = baseline.median_engagements

    elif preferred_metric == "shares":
        content_value = float(item.shares) if item.shares is not None else None
        historical_median = baseline.median_shares

    elif preferred_metric == "comments":
        content_value = float(item.comments) if item.comments is not None else None
        historical_median = baseline.median_comments

    # Fallback to total engagements if preferred metric (e.g. rate) is unavailable on this item
    if content_value is None and preferred_metric == "engagement_rate":
        preferred_metric = "engagements"
        content_value = float(calculate_item_engagements(item))
        historical_median = baseline.median_engagements

    rel_diff: Optional[float] = None
    if (
        content_value is not None
        and historical_median is not None
        and historical_median > 0
    ):
        rel_diff = round(
            ((content_value - historical_median) / historical_median) * 100.0, 2
        )

    return BaselineComparison(
        metric=preferred_metric,
        content_value=round(content_value, 4) if content_value is not None else None,
        historical_median=round(historical_median, 4)
        if historical_median is not None
        else None,
        relative_difference_percent=rel_diff,
    )
