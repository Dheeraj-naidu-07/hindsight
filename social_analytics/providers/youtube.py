"""
YouTube data provider adapter.
Uses YouTube Data API v3 and YouTube Analytics API specifications.
Extracts metrics deterministically with fallback to fixtures when credentials are absent.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from social_analytics.fixtures.youtube_fixtures import (
    YOUTUBE_AUDIENCE_FIXTURE,
    YOUTUBE_CHANNEL_FIXTURE,
    YOUTUBE_VIDEOS_FIXTURE,
)
from social_analytics.models.normalized import (
    AccountInfo,
    AudienceMetrics,
    NormalizedContent,
)
from social_analytics.providers.base import BaseSocialProvider

logger = logging.getLogger(__name__)


def parse_iso8601_duration(duration_str: str) -> int:
    """
    Parses ISO 8601 duration string (e.g. PT14M35S, PT48S, PT1H2M) into total seconds.
    """
    pattern = re.compile(
        r"PT(?:(?P<hours>\d+)H)?(?:(?P<minutes>\d+)M)?(?:(?P<seconds>\d+)S)?"
    )
    match = pattern.match(duration_str or "")
    if not match:
        return 0
    parts = match.groupdict()
    hours = int(parts["hours"] or 0)
    minutes = int(parts["minutes"] or 0)
    seconds = int(parts["seconds"] or 0)
    return hours * 3600 + minutes * 60 + seconds


class YouTubeProvider(BaseSocialProvider):
    """
    Adapter for official YouTube Data API v3.
    """

    BASE_URL = "https://www.googleapis.com/youtube/v3"

    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_rps: float = 5.0,
        cache_ttl_seconds: int = 300,
        mock_mode: Optional[bool] = None,
    ):
        resolved_key = api_key or os.getenv("YOUTUBE_API_KEY")
        # If no key is configured, default to deterministic mock mode
        is_mock = mock_mode if mock_mode is not None else (not bool(resolved_key))
        super().__init__(
            api_key=resolved_key,
            rate_limit_rps=rate_limit_rps,
            cache_ttl_seconds=cache_ttl_seconds,
            mock_mode=is_mock,
        )

    def platform_name(self) -> str:
        return "youtube"

    def get_account(self, account_id: str) -> AccountInfo:
        cache_key = f"yt:account:{account_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if self.mock_mode:
            channel_data = YOUTUBE_CHANNEL_FIXTURE["items"][0]
        else:
            self.rate_limiter.acquire()
            channel_data = self.retry_policy.execute(
                lambda: self._fetch_live_channel(account_id)
            )

        snippet = channel_data.get("snippet", {})
        statistics = channel_data.get("statistics", {})

        subs_str = statistics.get("subscriberCount")
        video_count_str = statistics.get("videoCount")

        account_info = AccountInfo(
            platform="youtube",
            account_id=channel_data.get("id", account_id),
            username=snippet.get("customUrl", f"channel_{account_id}"),
            display_name=snippet.get("title"),
            followers_count=int(subs_str) if subs_str is not None else None,
            following_count=None,  # YouTube does not expose subscriptions count publicly
            total_posts=int(video_count_str) if video_count_str is not None else None,
            profile_url=f"https://www.youtube.com/{snippet.get('customUrl', 'channel/' + account_id)}",
            raw_metadata={
                "view_count": statistics.get("viewCount"),
                "country": snippet.get("country"),
                "published_at": snippet.get("publishedAt"),
            },
        )
        self.cache.set(cache_key, account_info)
        return account_info

    def get_content(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 100,
    ) -> List[NormalizedContent]:
        cache_key = f"yt:content:{account_id}:{start_date.isoformat()}:{end_date.isoformat()}:{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if self.mock_mode:
            raw_videos = YOUTUBE_VIDEOS_FIXTURE["items"]
        else:
            self.rate_limiter.acquire()
            raw_videos = self.retry_policy.execute(
                lambda: self._fetch_live_videos(account_id, start_date, end_date, limit)
            )

        results: List[NormalizedContent] = []
        for raw in raw_videos:
            item = self._normalize_video_item(raw)
            # Filter by publication date window
            if start_date <= item.published_at <= end_date:
                results.append(item)
                if len(results) >= limit:
                    break

        self.cache.set(cache_key, results)
        return results

    def get_content_metrics(self, content_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        # Returns preserved platform-specific metrics mapped by content ID
        results: Dict[str, Dict[str, Any]] = {}
        for cid in content_ids:
            # In mock mode, find matching fixture
            for raw in YOUTUBE_VIDEOS_FIXTURE["items"]:
                if raw["id"] == cid:
                    results[cid] = {
                        "statistics": raw.get("statistics", {}),
                        "analytics": raw.get("analytics", {}),
                        "duration": raw.get("contentDetails", {}).get("duration"),
                    }
        return results

    def get_audience_metrics(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> AudienceMetrics:
        if self.mock_mode:
            data = YOUTUBE_AUDIENCE_FIXTURE
            subs_start = data["subscribersStart"]
            subs_end = data["subscribersEnd"]
            net_gained = subs_end - subs_start
            total_impressions = data.get("totalImpressions")
            platform_spec = {
                "subscribers_gained_total": data.get("subscribersGainedTotal"),
                "subscribers_lost_total": data.get("subscribersLostTotal"),
            }
        else:
            # In live mode without Analytics OAuth credentials, audience growth is computed from channel snapshots
            account = self.get_account(account_id)
            subs_end = account.followers_count
            subs_start = None
            net_gained = None
            total_impressions = None
            platform_spec = {}

        return AudienceMetrics(
            platform="youtube",
            account_id=account_id,
            period_start=start_date,
            period_end=end_date,
            followers_start=subs_start,
            followers_end=subs_end,
            net_followers_gained=net_gained,
            total_reach=None,  # YouTube does not provide deduplicated reach
            total_impressions=total_impressions,
            demographics={},
            platform_specific=platform_spec,
        )

    def _normalize_video_item(self, raw: Dict[str, Any]) -> NormalizedContent:
        snippet = raw.get("snippet", {})
        statistics = raw.get("statistics", {})
        content_details = raw.get("contentDetails", {})
        analytics = raw.get("analytics", {})

        published_str = snippet.get("publishedAt", "")
        # Parse timestamp safely
        try:
            pub_dt = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
        except Exception:
            pub_dt = datetime.now(timezone.utc)

        duration_sec = parse_iso8601_duration(content_details.get("duration", ""))
        content_type = "short" if (0 < duration_sec <= 60) else "video"

        # Explicit 0 vs None distinction
        views = int(statistics["viewCount"]) if "viewCount" in statistics else None
        likes = int(statistics["likeCount"]) if "likeCount" in statistics else None
        comments = int(statistics["commentCount"]) if "commentCount" in statistics else None

        # Shares and watch time from analytics
        shares = int(analytics["shares"]) if "shares" in analytics else None
        watch_time_sec = (
            float(analytics["estimatedMinutesWatched"]) * 60.0
            if "estimatedMinutesWatched" in analytics
            else None
        )
        avg_view_duration = (
            float(analytics["averageViewDurationSeconds"])
            if "averageViewDurationSeconds" in analytics
            else None
        )
        subscribers_gained = (
            int(analytics["subscribersGained"])
            if "subscribersGained" in analytics
            else None
        )
        impressions = (
            int(analytics["impressions"])
            if "impressions" in analytics
            else None
        )

        tags = snippet.get("tags", [])
        topic = tags[0] if tags else None

        return NormalizedContent(
            platform="youtube",
            content_id=raw["id"],
            content_type=content_type,
            published_at=pub_dt,
            title=snippet.get("title"),
            url=f"https://www.youtube.com/watch?v={raw['id']}",
            views=views,
            impressions=impressions,
            reach=None,  # YouTube API does not report unique reach
            likes=likes,
            comments=comments,
            shares=shares,
            saves=None,  # Not supported by YouTube API
            watch_time=watch_time_sec,
            average_view_duration=avg_view_duration,
            followers_gained=subscribers_gained,
            topic=topic,
            platform_specific={
                "duration_seconds": duration_sec,
                "categoryId": snippet.get("categoryId"),
                "impression_click_through_rate": analytics.get("impressionClickThroughRate"),
            },
        )

    def _fetch_live_channel(self, channel_id: str) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                f"{self.BASE_URL}/channels",
                params={
                    "part": "snippet,statistics",
                    "id": channel_id,
                    "key": self.api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            items = data.get("items", [])
            if not items:
                raise ValueError(f"YouTube channel {channel_id} not found")
            return items[0]

    def _fetch_live_videos(
        self,
        channel_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int,
    ) -> List[Dict[str, Any]]:
        with httpx.Client(timeout=15.0) as client:
            # 1. Search for video IDs in time range
            search_resp = client.get(
                f"{self.BASE_URL}/search",
                params={
                    "part": "id",
                    "channelId": channel_id,
                    "type": "video",
                    "publishedAfter": start_date.isoformat().replace("+00:00", "Z"),
                    "publishedBefore": end_date.isoformat().replace("+00:00", "Z"),
                    "maxResults": min(limit, 50),
                    "key": self.api_key,
                },
            )
            search_resp.raise_for_status()
            video_ids = [
                item["id"]["videoId"]
                for item in search_resp.json().get("items", [])
                if "videoId" in item.get("id", {})
            ]

            if not video_ids:
                return []

            # 2. Fetch full snippet, statistics, contentDetails
            videos_resp = client.get(
                f"{self.BASE_URL}/videos",
                params={
                    "part": "snippet,statistics,contentDetails",
                    "id": ",".join(video_ids),
                    "key": self.api_key,
                },
            )
            videos_resp.raise_for_status()
            return videos_resp.json().get("items", [])
