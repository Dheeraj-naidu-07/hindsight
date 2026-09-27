"""
Unit tests for historical baseline calculations and relative difference percentage.
"""

from datetime import datetime, timezone
import pytest

from social_analytics.engine.baselines import (
    compare_item_to_baseline,
    compute_account_baseline,
)
from social_analytics.models.normalized import NormalizedContent


def create_sample_item(content_id: str, views: int, reach: int, likes: int, comments: int, shares: int):
    return NormalizedContent(
        platform="instagram",
        content_id=content_id,
        content_type="post",
        published_at=datetime.now(timezone.utc),
        views=views,
        reach=reach,
        likes=likes,
        comments=comments,
        shares=shares,
        saves=10,
    )


def test_compute_account_baseline():
    # 3 historical posts
    items = [
        create_sample_item("p1", views=1000, reach=800, likes=40, comments=5, shares=5),   # eng = 60, rate = 7.5%
        create_sample_item("p2", views=2000, reach=1500, likes=90, comments=10, shares=10), # eng = 120, rate = 8.0%
        create_sample_item("p3", views=5000, reach=4000, likes=200, comments=20, shares=20), # eng = 250, rate = 6.25%
    ]

    baseline = compute_account_baseline(items)
    assert baseline.sample_size == 3
    assert baseline.median_views == 2000.0
    assert baseline.median_engagements == 120.0
    assert baseline.median_shares == 10.0
    assert baseline.median_comments == 10.0
    # rates are [6.25, 7.5, 8.0] -> median is 7.5
    assert baseline.median_engagement_rate == 7.5


def test_compare_item_to_baseline_relative_difference():
    # Baseline engagement rate = 4.8%
    # Content item rate = 7.4%
    # Formula: ((7.4 - 4.8) / 4.8) * 100 = 54.17%
    items = [
        create_sample_item("p1", views=1000, reach=1000, likes=40, comments=4, shares=4),  # eng = 58 -> rate = 5.8
        create_sample_item("p2", views=1000, reach=1000, likes=30, comments=4, shares=4),  # eng = 48 -> rate = 4.8 (median)
        create_sample_item("p3", views=1000, reach=1000, likes=20, comments=4, shares=4),  # eng = 38 -> rate = 3.8
    ]
    baseline = compute_account_baseline(items)

    test_item = NormalizedContent(
        platform="instagram",
        content_id="target_post",
        content_type="post",
        published_at=datetime.now(timezone.utc),
        reach=1000,
        likes=60,
        comments=8,
        shares=6,
        saves=0, # total eng = 74 -> rate = 7.4%
    )

    comp = compare_item_to_baseline(test_item, baseline, preferred_metric="engagement_rate")
    assert comp.metric == "engagement_rate"
    assert comp.content_value == 7.4
    assert comp.historical_median == 4.8
    assert comp.relative_difference_percent == 54.17


def test_empty_baseline_handling():
    baseline = compute_account_baseline([])
    assert baseline.sample_size == 0
    assert baseline.median_views is None
    assert baseline.median_engagements == 0.0

    test_item = create_sample_item("p_test", views=100, reach=100, likes=10, comments=2, shares=1)
    comp = compare_item_to_baseline(test_item, baseline)
    assert comp.content_value is not None
    assert comp.relative_difference_percent is None
