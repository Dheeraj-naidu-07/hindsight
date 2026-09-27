"""Fixtures package for social analytics."""

from social_analytics.fixtures.youtube_fixtures import (
    YOUTUBE_AUDIENCE_FIXTURE,
    YOUTUBE_CHANNEL_FIXTURE,
    YOUTUBE_VIDEOS_FIXTURE,
)
from social_analytics.fixtures.instagram_fixtures import (
    INSTAGRAM_AUDIENCE_FIXTURE,
    INSTAGRAM_MEDIA_FIXTURE,
    INSTAGRAM_USER_FIXTURE,
)
from social_analytics.fixtures.reddit_fixtures import (
    REDDIT_AUDIENCE_FIXTURE,
    REDDIT_SUBMITTED_FIXTURE,
    REDDIT_USER_FIXTURE,
)

__all__ = [
    "YOUTUBE_AUDIENCE_FIXTURE",
    "YOUTUBE_CHANNEL_FIXTURE",
    "YOUTUBE_VIDEOS_FIXTURE",
    "INSTAGRAM_AUDIENCE_FIXTURE",
    "INSTAGRAM_MEDIA_FIXTURE",
    "INSTAGRAM_USER_FIXTURE",
    "REDDIT_AUDIENCE_FIXTURE",
    "REDDIT_SUBMITTED_FIXTURE",
    "REDDIT_USER_FIXTURE",
]
