"""
Unit tests for deterministic metric calculations, edge cases, and zero denominators.
"""

from datetime import datetime, timezone
import pytest

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
from social_analytics.models.normalized import NormalizedContent


def test_calculate_item_engagements():
    # Only available metrics are summed
    item = NormalizedContent(
        platform="youtube",
        content_id="test_1",
        content_type="video",
        published_at=datetime.now(timezone.utc),
        likes=100,
        comments=20,
        shares=10,
        saves=None,  # unavailable on YouTube
    )
    assert calculate_item_engagements(item) == 130


def test_calculate_item_engagements_explicit_zero():
    item = NormalizedContent(
        platform="instagram",
        content_id="test_2",
        content_type="post",
        published_at=datetime.now(timezone.utc),
        likes=0,
        comments=0,
        shares=0,
        saves=0,
    )
    assert calculate_item_engagements(item) == 0


def test_resolve_rate_denominator_prefers_reach():
    item = NormalizedContent(
        platform="instagram",
        content_id="test_3",
        content_type="reel",
        published_at=datetime.now(timezone.utc),
        reach=5000,
        impressions=7500,
    )
    denom, basis = resolve_rate_denominator(item)
    assert denom == 5000
    assert basis == "reach"


def test_resolve_rate_denominator_falls_back_to_impressions():
    item = NormalizedContent(
        platform="youtube",
        content_id="test_4",
        content_type="video",
        published_at=datetime.now(timezone.utc),
        reach=None,
        impressions=12000,
    )
    denom, basis = resolve_rate_denominator(item)
    assert denom == 12000
    assert basis == "impressions"


def test_resolve_rate_denominator_none_when_unavailable():
    item = NormalizedContent(
        platform="reddit",
        content_id="test_5",
        content_type="submission",
        published_at=datetime.now(timezone.utc),
        reach=None,
        impressions=None,
    )
    denom, basis = resolve_rate_denominator(item)
    assert denom is None
    assert basis is None


def test_calculate_engagement_rate_standard():
    rate = calculate_engagement_rate(engagements=250, denominator=5000)
    assert rate == 5.0


def test_calculate_engagement_rate_zero_denominator():
    # Must safely return None without throwing ZeroDivisionError
    assert calculate_engagement_rate(engagements=10, denominator=0) is None
    assert calculate_engagement_rate(engagements=10, denominator=None) is None


def test_component_rates():
    # Like rate, comment rate, share rate, save rate
    denom = 1000
    assert calculate_component_rate(50, denom) == 5.0
    assert calculate_component_rate(15, denom) == 1.5
    assert calculate_component_rate(5, denom) == 0.5
    assert calculate_component_rate(None, denom) is None
    assert calculate_component_rate(50, 0) is None


def test_calculate_view_rate():
    assert calculate_view_rate(views=500, impressions=2000) == 25.0
    assert calculate_view_rate(views=None, impressions=2000) is None
    assert calculate_view_rate(views=500, impressions=0) is None


def test_safe_median_odd_even_empty():
    assert safe_median([10.0, 20.0, 30.0]) == 20.0
    assert safe_median([10.0, 20.0, 30.0, 40.0]) == 25.0
    assert safe_median([]) is None


def test_safe_mean():
    assert safe_mean([10.0, 20.0, 30.0]) == 20.0
    assert safe_mean([]) is None


def test_follower_growth():
    abs_growth, pct_growth = calculate_follower_growth(start=10000, end=11500)
    assert abs_growth == 1500
    assert pct_growth == 15.0

    # Start is 0 or None
    abs_zero, pct_zero = calculate_follower_growth(start=0, end=50)
    assert abs_zero == 50
    assert pct_zero is None

    abs_none, pct_none = calculate_follower_growth(start=None, end=100)
    assert abs_none is None
    assert pct_none is None


def test_posting_frequency():
    per_day, per_week = calculate_posting_frequency(post_count=14, period_days=28.0)
    assert per_day == 0.5
    assert per_week == 3.5

    zero_day, zero_week = calculate_posting_frequency(post_count=5, period_days=0.0)
    assert zero_day == 0.0
    assert zero_week == 0.0
