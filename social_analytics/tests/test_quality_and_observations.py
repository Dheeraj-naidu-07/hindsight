"""
Unit tests for data quality assessment and deterministic observation generation.
"""

from datetime import datetime, timezone
import pytest

from social_analytics.engine.observations import (
    generate_content_type_observations,
    generate_period_trend_observations,
)
from social_analytics.engine.quality import assess_data_quality
from social_analytics.models.normalized import NormalizedContent
from social_analytics.models.output import (
    ContentTypePerformance,
    MetricChange,
    PeriodComparison,
)


def test_insufficient_sample_size_flag():
    # Only 2 items (< 5 threshold)
    items = [
        NormalizedContent(
            platform="youtube",
            content_id="v1",
            content_type="video",
            published_at=datetime.now(timezone.utc),
            views=1000,
        ),
        NormalizedContent(
            platform="youtube",
            content_id="v2",
            content_type="video",
            published_at=datetime.now(timezone.utc),
            views=2000,
        ),
    ]
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 15, tzinfo=timezone.utc)

    quality = assess_data_quality(platform="youtube", items=items, start_date=start, end_date=end)

    assert quality.sample_size == 2
    assert quality.insufficient_sample_size is True
    assert any("insufficient_sample_size" in w for w in quality.data_quality_warnings)


def test_sufficient_sample_size():
    items = [
        NormalizedContent(
            platform="instagram",
            content_id=f"ig_{i}",
            content_type="post",
            published_at=datetime.now(timezone.utc),
            likes=10,
        )
        for i in range(6)
    ]
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 30, tzinfo=timezone.utc)

    quality = assess_data_quality(platform="instagram", items=items, start_date=start, end_date=end)
    assert quality.sample_size == 6
    assert quality.insufficient_sample_size is False


def test_unavailable_metrics_per_platform():
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 30, tzinfo=timezone.utc)

    yt_q = assess_data_quality(platform="youtube", items=[], start_date=start, end_date=end)
    assert "saves" in yt_q.unavailable_metrics
    assert "reach" in yt_q.unavailable_metrics

    rd_q = assess_data_quality(platform="reddit", items=[], start_date=start, end_date=end)
    assert "views" in rd_q.unavailable_metrics
    assert "impressions" in rd_q.unavailable_metrics


def test_content_type_observations_non_causal():
    content_types = {
        "short_video": ContentTypePerformance(
            count=12,
            median_views=42000.0,
            median_engagements=2500.0,
            median_engagement_rate=5.8,
            engagement_rate_basis="impressions",
            share_of_total_content_pct=60.0,
        ),
        "image_post": ContentTypePerformance(
            count=8,
            median_views=15000.0,
            median_engagements=900.0,
            median_engagement_rate=4.08,
            engagement_rate_basis="impressions",
            share_of_total_content_pct=40.0,
        ),
    }

    obs = generate_content_type_observations(content_types)
    assert len(obs) >= 1
    first = obs[0]
    assert first.type == "content_type_comparison"
    # Strict check: must NOT claim causation
    assert "cause" not in first.observation.lower()
    assert "higher" in first.observation.lower()
    # Evidence must contain sample sizes and numerical metrics
    assert "sample_sizes" in first.evidence
    assert first.evidence["sample_sizes"]["short_video"] == 12
    assert first.evidence["sample_sizes"]["image_post"] == 8


def test_period_trend_observation_distinguishes_pp():
    period_comp = PeriodComparison(
        has_previous_period=True,
        engagement_rate_change=MetricChange(
            current_value=4.1,
            previous_value=5.0,
            percentage_points_change=-0.9,
            relative_change_percent=-18.0,
        ),
    )
    obs = generate_period_trend_observations(period_comp)
    assert len(obs) == 1
    assert "18.0% below the previous period" in obs[0].observation
    assert "-0.9 pp" in obs[0].observation
    assert obs[0].evidence["percentage_points_change"] == -0.9
    assert obs[0].evidence["relative_change_percent"] == -18.0
