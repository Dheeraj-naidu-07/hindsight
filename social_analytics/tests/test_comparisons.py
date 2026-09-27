"""
Unit tests for period comparisons and distinguishing percentage points (pp) from relative percent (%).
"""

import pytest

from social_analytics.engine.comparisons import (
    calculate_metric_change,
    compare_periods,
)
from social_analytics.models.output import PeriodInfo


def test_distinguish_pp_from_relative_percentage():
    # 4% -> 5%
    # pp change = +1.0 pp
    # relative change = ((5 - 4) / 4) * 100 = +25.0%
    change = calculate_metric_change(current=5.0, previous=4.0, is_rate_metric=True)
    assert change is not None
    assert change.current_value == 5.0
    assert change.previous_value == 4.0
    assert change.percentage_points_change == 1.0
    assert change.relative_change_percent == 25.0
    assert change.absolute_change == 1.0


def test_negative_rate_change():
    # 8.0% -> 6.0%
    # pp change = -2.0 pp
    # relative change = -25.0%
    change = calculate_metric_change(current=6.0, previous=8.0, is_rate_metric=True)
    assert change is not None
    assert change.percentage_points_change == -2.0
    assert change.relative_change_percent == -25.0


def test_volume_metric_change_no_pp():
    # Views: 10,000 -> 15,000 (+5,000 views, +50%)
    change = calculate_metric_change(current=15000.0, previous=10000.0, is_rate_metric=False)
    assert change is not None
    assert change.absolute_change == 5000.0
    assert change.relative_change_percent == 50.0
    assert change.percentage_points_change is None


def test_previous_is_zero_volume():
    change = calculate_metric_change(current=50.0, previous=0.0, is_rate_metric=False)
    assert change is not None
    assert change.absolute_change == 50.0
    assert change.relative_change_percent is None


def test_compare_periods_structure():
    curr = {
        "total_views": 20000.0,
        "total_engagements": 1200.0,
        "median_engagement_rate": 6.0,
        "follower_growth": 300.0,
        "posting_frequency_per_week": 4.0,
        "median_views": 5000.0,
        "median_engagements": 300.0,
    }
    prev = {
        "total_views": 16000.0,
        "total_engagements": 1000.0,
        "median_engagement_rate": 5.0,
        "follower_growth": 250.0,
        "posting_frequency_per_week": 3.0,
        "median_views": 4000.0,
        "median_engagements": 250.0,
    }
    pinfo = PeriodInfo(start_date="2026-08-01T00:00:00Z", end_date="2026-08-31T00:00:00Z", days=30.0)
    comp = compare_periods(curr, prev, pinfo)

    assert comp.has_previous_period is True
    assert comp.views_change.relative_change_percent == 25.0
    assert comp.engagement_change.relative_change_percent == 20.0
    assert comp.engagement_rate_change.percentage_points_change == 1.0
    assert comp.engagement_rate_change.relative_change_percent == 20.0
