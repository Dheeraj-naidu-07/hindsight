"""
Unit tests for platform data normalization.
Verifies:
- 0 means explicitly reported 0.
- None (null) means unavailable.
- Never converts unavailable to 0.
- Preserves platform-specific attributes.
"""

from datetime import datetime, timezone
import pytest

from social_analytics.fixtures.instagram_fixtures import (
    INSTAGRAM_MEDIA_FIXTURE,
    INSTAGRAM_USER_FIXTURE,
)
from social_analytics.fixtures.reddit_fixtures import (
    REDDIT_SUBMITTED_FIXTURE,
    REDDIT_USER_FIXTURE,
)
from social_analytics.fixtures.youtube_fixtures import (
    YOUTUBE_CHANNEL_FIXTURE,
    YOUTUBE_VIDEOS_FIXTURE,
)
from social_analytics.providers.instagram import InstagramProvider, extract_primary_hashtag
from social_analytics.providers.reddit import RedditProvider
from social_analytics.providers.youtube import YouTubeProvider, parse_iso8601_duration


def test_youtube_duration_parser():
    assert parse_iso8601_duration("PT48S") == 48
    assert parse_iso8601_duration("PT14M35S") == 14 * 60 + 35
    assert parse_iso8601_duration("PT1H2M3S") == 3600 + 120 + 3
    assert parse_iso8601_duration("") == 0


def test_youtube_normalization():
    provider = YouTubeProvider(mock_mode=True)
    raw_video = YOUTUBE_VIDEOS_FIXTURE["items"][0]  # 14m35s video
    raw_short = YOUTUBE_VIDEOS_FIXTURE["items"][1]  # 48s short

    norm_video = provider._normalize_video_item(raw_video)
    norm_short = provider._normalize_video_item(raw_short)

    assert norm_video.platform == "youtube"
    assert norm_video.content_type == "video"
    assert norm_video.views == 12500
    assert norm_video.likes == 890
    assert norm_video.comments == 142
    assert norm_video.impressions == 115000
    assert norm_video.reach is None  # YouTube does not report reach
    assert norm_video.saves is None  # YouTube does not have saves

    # Short format verification
    assert norm_short.content_type == "short"
    assert norm_short.views == 45200


def test_instagram_hashtag_extractor():
    caption = "Building scalable AI memory! #systemdesign #python #agents"
    assert extract_primary_hashtag(caption) == "systemdesign"
    assert extract_primary_hashtag("No hashtags here") is None


def test_instagram_normalization():
    provider = InstagramProvider(mock_mode=True)
    raw_carousel = INSTAGRAM_MEDIA_FIXTURE["data"][0]
    raw_reel = INSTAGRAM_MEDIA_FIXTURE["data"][1]

    norm_carousel = provider._normalize_media_item(raw_carousel)
    norm_reel = provider._normalize_media_item(raw_reel)

    assert norm_carousel.platform == "instagram"
    assert norm_carousel.content_type == "carousel"
    assert norm_carousel.reach == 11500
    assert norm_carousel.impressions == 14200
    assert norm_carousel.saves == 280
    assert norm_carousel.shares == 94
    assert norm_carousel.views is None  # Carousel has no plays
    assert norm_carousel.watch_time is None  # Instagram API does not expose watch time

    assert norm_reel.content_type == "reel"
    assert norm_reel.views == 27800  # Reel plays mapped to views


def test_reddit_normalization():
    provider = RedditProvider(mock_mode=True)
    raw_post = REDDIT_SUBMITTED_FIXTURE["data"]["children"][0]["data"]

    norm_post = provider._normalize_post_item(raw_post)
    assert norm_post.platform == "reddit"
    assert norm_post.content_id == "rd_post_201"
    assert norm_post.likes == 340  # Reddit score
    assert norm_post.comments == 82
    assert norm_post.shares == 6  # crossposts
    assert norm_post.views is None  # Unavailable on Reddit
    assert norm_post.impressions is None  # Unavailable on Reddit
    assert norm_post.reach is None  # Unavailable on Reddit
    assert norm_post.saves is None  # Unavailable on Reddit
    assert norm_post.topic == "MachineLearning"
    assert norm_post.platform_specific["upvote_ratio"] == 0.94
