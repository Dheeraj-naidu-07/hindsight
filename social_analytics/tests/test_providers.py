"""
Unit tests for social data providers: rate limiting, caching, retries, and pagination.
"""

from datetime import datetime, timezone
import pytest

from social_analytics.providers.base import RateLimiter, RetryPolicy, TTLCache
from social_analytics.providers.instagram import InstagramProvider
from social_analytics.providers.reddit import RedditProvider
from social_analytics.providers.youtube import YouTubeProvider


def test_ttl_cache_expiration():
    cache = TTLCache(default_ttl_seconds=1)
    cache.set("key1", "val1")
    assert cache.get("key1") == "val1"
    # Overwrite with 0 second TTL to trigger instant expiration
    cache.set("key2", "val2", ttl_seconds=-1)
    assert cache.get("key2") is None


def test_rate_limiter_acquire():
    limiter = RateLimiter(requests_per_second=50.0, burst=5)
    # Should acquire 5 tokens quickly
    for _ in range(5):
        limiter.acquire()


def test_retry_policy_success():
    policy = RetryPolicy(max_retries=2, base_delay_seconds=0.01)
    attempts = [0]

    def flaky_func():
        attempts[0] += 1
        if attempts[0] < 2:
            raise ConnectionError("Temporary network glitch")
        return "success"

    result = policy.execute(flaky_func)
    assert result == "success"
    assert attempts[0] == 2


def test_retry_policy_exhaustion():
    policy = RetryPolicy(max_retries=2, base_delay_seconds=0.01)

    def failing_func():
        raise ValueError("Permanent failure")

    with pytest.raises(ValueError):
        policy.execute(failing_func)


def test_youtube_provider_mock_content_and_metrics():
    provider = YouTubeProvider(mock_mode=True)
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 30, tzinfo=timezone.utc)

    account = provider.get_account("UC_x5XG1OV2P6uZZ5FSM9Ttw")
    assert account.followers_count == 24500

    content = provider.get_content("UC_x5XG1OV2P6uZZ5FSM9Ttw", start, end)
    assert len(content) == 4

    metrics = provider.get_content_metrics(["yt_vid_001"])
    assert "yt_vid_001" in metrics
    assert "statistics" in metrics["yt_vid_001"]


def test_instagram_provider_mock_content():
    provider = InstagramProvider(mock_mode=True)
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 30, tzinfo=timezone.utc)

    account = provider.get_account("17841405822384912")
    assert account.username == "tech_architect_daily"

    content = provider.get_content("17841405822384912", start, end)
    assert len(content) == 4


def test_reddit_provider_mock_content():
    provider = RedditProvider(mock_mode=True)
    start = datetime(2026, 9, 1, tzinfo=timezone.utc)
    end = datetime(2026, 9, 30, tzinfo=timezone.utc)

    account = provider.get_account("u/DistributedDev")
    assert account.username == "DistributedDev"

    content = provider.get_content("u/DistributedDev", start, end)
    assert len(content) == 4
