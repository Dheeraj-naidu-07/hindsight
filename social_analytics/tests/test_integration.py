"""
End-to-end integration tests for Social Media Analytics Engine.
Validates the complete execution flow:
Mock Platform API Data -> Normalization -> Analytics -> Observations -> Final Structured JSON Contract.
"""

from datetime import datetime, timezone
import json
import pytest

from social_analytics.engine.analytics_engine import SocialMediaAnalyticsEngine
from social_analytics.models.output import AnalyticsResult
from social_analytics.providers.instagram import InstagramProvider
from social_analytics.providers.reddit import RedditProvider
from social_analytics.providers.youtube import YouTubeProvider


def test_youtube_end_to_end_integration():
    provider = YouTubeProvider(mock_mode=True)
    engine = SocialMediaAnalyticsEngine(provider)

    start_date = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end_date = datetime(2026, 9, 30, tzinfo=timezone.utc)

    result = engine.run_analysis(
        account_id="UC_x5XG1OV2P6uZZ5FSM9Ttw",
        start_date=start_date,
        end_date=end_date,
    )

    # 1. Type validation
    assert isinstance(result, AnalyticsResult)

    # 2. Convert to clean JSON serializable dict
    result_dict = result.model_dump()
    json_str = json.dumps(result_dict)
    assert json_str is not None

    # 3. Check all required top-level contract sections
    expected_sections = [
        "account",
        "period",
        "content_summary",
        "growth",
        "baseline",
        "top_content",
        "bottom_content",
        "content_type_performance",
        "period_comparison",
        "observations",
        "platform_specific_metrics",
        "data_quality",
    ]
    for section in expected_sections:
        assert section in result_dict, f"Missing section: {section}"

    # 4. Content assertions
    assert result.account.platform == "youtube"
    assert result.account.current_followers == 24500
    assert result.content_summary.total_posts == 4
    assert result.content_summary.posts_by_type.get("video") == 2
    assert result.content_summary.posts_by_type.get("short") == 2
    assert result.content_summary.engagement_rate_basis == "impressions"
    assert result.baseline.sample_size == 4
    assert len(result.top_content) > 0
    assert len(result.observations) > 0


def test_instagram_end_to_end_integration():
    provider = InstagramProvider(mock_mode=True)
    engine = SocialMediaAnalyticsEngine(provider)

    start_date = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end_date = datetime(2026, 9, 30, tzinfo=timezone.utc)

    result = engine.run_analysis(
        account_id="17841405822384912",
        start_date=start_date,
        end_date=end_date,
    )

    assert isinstance(result, AnalyticsResult)
    result_dict = result.model_dump()

    assert result.account.platform == "instagram"
    assert result.account.username == "tech_architect_daily"
    assert result.content_summary.total_posts == 4
    # Instagram uses reach as primary denominator basis
    assert result.content_summary.engagement_rate_basis == "reach"
    assert "reel" in result.content_type_performance
    assert "carousel" in result.content_type_performance
    assert result.growth.followers_start == 17850
    assert result.growth.followers_end == 18400
    assert result.growth.absolute_follower_growth == 550
    assert result.data_quality.source_platform == "instagram"


def test_reddit_end_to_end_integration():
    provider = RedditProvider(mock_mode=True)
    engine = SocialMediaAnalyticsEngine(provider)

    start_date = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end_date = datetime(2026, 9, 30, tzinfo=timezone.utc)

    result = engine.run_analysis(
        account_id="u/DistributedDev",
        start_date=start_date,
        end_date=end_date,
    )

    assert isinstance(result, AnalyticsResult)
    result_dict = result.model_dump()

    assert result.account.platform == "reddit"
    assert result.content_summary.total_posts == 4
    # Reddit has no reach or impressions, so engagement_rate is None
    assert result.content_summary.engagement_rate_basis is None
    assert result.content_summary.median_engagement_rate is None
    assert result.content_summary.total_engagements > 0
    assert "views" in result.data_quality.unavailable_metrics
    assert "impressions" in result.data_quality.unavailable_metrics
