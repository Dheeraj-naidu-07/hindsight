"""
Deterministic social media metric calculations.
Pure Python code-based calculations. No LLM inferences.
Handles missing metrics, explicit zeros, and zero denominators safely.
"""

from __future__ import annotations

import statistics
from typing import List, Optional, Tuple

from social_analytics.models.normalized import NormalizedContent


def calculate_item_engagements(item: NormalizedContent) -> int:
    """
    Computes total direct interactions for a single content item.
    Formula: sum of non-null values for likes + comments + shares + saves.
    """
    total = 0
    if item.likes is not None:
        total += item.likes
    if item.comments is not None:
        total += item.comments
    if item.shares is not None:
        total += item.shares
    if item.saves is not None:
        total += item.saves
    return total


def resolve_rate_denominator(item: NormalizedContent) -> Tuple[Optional[int], Optional[str]]:
    """
    Selects the best available denominator for rate calculations.
    Priority hierarchy:
    1. 'reach' (Unique accounts exposed - best representation of audience size)
    2. 'impressions' (Total exposure instances - fallback standard)

    Returns:
        (denominator_value, denominator_basis_name) or (None, None)
    """
    if item.reach is not None and item.reach > 0:
        return item.reach, "reach"
    if item.impressions is not None and item.impressions > 0:
        return item.impressions, "impressions"
    return None, None


def calculate_engagement_rate(
    engagements: int, denominator: Optional[int]
) -> Optional[float]:
    """
    Calculates engagement rate: (total_engagements / denominator) * 100.
    Returns None if denominator is None or <= 0.
    """
    if denominator is None or denominator <= 0:
        return None
    return round((engagements / denominator) * 100.0, 4)


def calculate_component_rate(
    numerator: Optional[int], denominator: Optional[int]
) -> Optional[float]:
    """
    Calculates component rate (e.g. like rate, comment rate, share rate, save rate).
    Returns None if numerator is None or denominator is None or <= 0.
    """
    if numerator is None or denominator is None or denominator <= 0:
        return None
    return round((numerator / denominator) * 100.0, 4)


def calculate_view_rate(
    views: Optional[int], impressions: Optional[int]
) -> Optional[float]:
    """
    Calculates view rate: (views / impressions) * 100.
    Returns None if impressions is None or <= 0, or views is None.
    """
    if views is None or impressions is None or impressions <= 0:
        return None
    return round((views / impressions) * 100.0, 4)


def safe_median(values: List[float]) -> Optional[float]:
    """Computes median of list. Returns None if list is empty."""
    if not values:
        return None
    return round(float(statistics.median(values)), 4)


def safe_mean(values: List[float]) -> Optional[float]:
    """Computes arithmetic mean of list. Returns None if list is empty."""
    if not values:
        return None
    return round(float(statistics.mean(values)), 4)


def calculate_follower_growth(
    start: Optional[int], end: Optional[int]
) -> Tuple[Optional[int], Optional[float]]:
    """
    Computes absolute follower change and relative percentage growth.
    Returns:
        (absolute_growth, percentage_growth)
    """
    if start is None or end is None:
        return None, None
    abs_growth = end - start
    if start > 0:
        pct_growth = round((abs_growth / start) * 100.0, 4)
    else:
        pct_growth = None
    return abs_growth, pct_growth


def calculate_posting_frequency(
    post_count: int, period_days: float
) -> Tuple[float, float]:
    """
    Computes posts per day and posts per week.
    """
    if period_days <= 0:
        return 0.0, 0.0
    per_day = round(post_count / period_days, 4)
    per_week = round(per_day * 7.0, 4)
    return per_day, per_week
