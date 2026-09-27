"""
Instagram Graph API data provider adapter.
Uses official Instagram Graph API specifications.
Extracts metrics deterministically with fallback to fixtures when credentials are absent.
"""

from __future__ import annotations

import logging
import os
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from social_analytics.fixtures.instagram_fixtures import (
    INSTAGRAM_AUDIENCE_FIXTURE,
    INSTAGRAM_MEDIA_FIXTURE,
    INSTAGRAM_USER_FIXTURE,
)
from social_analytics.models.normalized import (
    AccountInfo,
    AudienceMetrics,
    NormalizedContent,
)
from social_analytics.providers.base import BaseSocialProvider

logger = logging.getLogger(__name__)


def extract_primary_hashtag(caption: Optional[str]) -> Optional[str]:
    """Extracts first valid hashtag without '#' symbol as topic tag."""
    if not caption:
        return None
    matches = re.findall(r"#(\w+)", caption)
    return matches[0].lower() if matches else None


class InstagramProvider(BaseSocialProvider):
    """
    Adapter for official Instagram Graph API.
    """

    GRAPH_API_BASE = "https://graph.facebook.com/v19.0"

    def __init__(
        self,
        access_token: Optional[str] = None,
        rate_limit_rps: float = 3.0,
        cache_ttl_seconds: int = 300,
        mock_mode: Optional[bool] = None,
    ):
        token = access_token or os.getenv("INSTAGRAM_ACCESS_TOKEN")
        is_mock = mock_mode if mock_mode is not None else (not bool(token))
        super().__init__(
            api_key=token,
            rate_limit_rps=rate_limit_rps,
            cache_ttl_seconds=cache_ttl_seconds,
            mock_mode=is_mock,
        )

    def platform_name(self) -> str:
        return "instagram"

    def get_account(self, account_id: str) -> AccountInfo:
        cache_key = f"ig:account:{account_id}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if self.mock_mode:
            raw_user = INSTAGRAM_USER_FIXTURE
        else:
            self.rate_limiter.acquire()
            raw_user = self.retry_policy.execute(
                lambda: self._fetch_live_user(account_id)
            )

        account_info = AccountInfo(
            platform="instagram",
            account_id=raw_user.get("id", account_id),
            username=raw_user.get("username", f"user_{account_id}"),
            display_name=raw_user.get("name"),
            followers_count=raw_user.get("followers_count"),
            following_count=raw_user.get("follows_count"),
            total_posts=raw_user.get("media_count"),
            profile_url=f"https://www.instagram.com/{raw_user.get('username')}/",
            raw_metadata={
                "biography": raw_user.get("biography"),
                "profile_picture_url": raw_user.get("profile_picture_url"),
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
        cache_key = f"ig:content:{account_id}:{start_date.isoformat()}:{end_date.isoformat()}:{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if self.mock_mode:
            raw_media_items = INSTAGRAM_MEDIA_FIXTURE["data"]
        else:
            self.rate_limiter.acquire()
            raw_media_items = self.retry_policy.execute(
                lambda: self._fetch_live_media(account_id, limit)
            )

        results: List[NormalizedContent] = []
        for raw in raw_media_items:
            item = self._normalize_media_item(raw)
            if start_date <= item.published_at <= end_date:
                results.append(item)
                if len(results) >= limit:
                    break

        self.cache.set(cache_key, results)
        return results

    def get_content_metrics(self, content_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        for cid in content_ids:
            for raw in INSTAGRAM_MEDIA_FIXTURE["data"]:
                if raw["id"] == cid:
                    results[cid] = {
                        "insights": raw.get("insights", {}),
                        "media_type": raw.get("media_type"),
                        "media_product_type": raw.get("media_product_type"),
                    }
        return results

    def get_audience_metrics(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> AudienceMetrics:
        if self.mock_mode:
            data = INSTAGRAM_AUDIENCE_FIXTURE
            followers_start = data.get("followers_start")
            followers_end = data.get("followers_end")
            net_gained = (
                followers_end - followers_start
                if (followers_end is not None and followers_start is not None)
                else None
            )
            total_reach = data.get("total_reach")
            total_impressions = data.get("total_impressions")
        else:
            account = self.get_account(account_id)
            followers_end = account.followers_count
            followers_start = None
            net_gained = None
            total_reach = None
            total_impressions = None

        return AudienceMetrics(
            platform="instagram",
            account_id=account_id,
            period_start=start_date,
            period_end=end_date,
            followers_start=followers_start,
            followers_end=followers_end,
            net_followers_gained=net_gained,
            total_reach=total_reach,
            total_impressions=total_impressions,
            demographics={},
            platform_specific={},
        )

    def _normalize_media_item(self, raw: Dict[str, Any]) -> NormalizedContent:
        raw_ts = raw.get("timestamp", "")
        try:
            pub_dt = datetime.fromisoformat(raw_ts)
        except Exception:
            pub_dt = datetime.now(timezone.utc)

        media_type = raw.get("media_type", "IMAGE")
        product_type = raw.get("media_product_type", "FEED")

        if product_type == "REELS" or media_type == "VIDEO":
            content_type = "reel"
        elif media_type == "CAROUSEL_ALBUM":
            content_type = "carousel"
        else:
            content_type = "post"

        caption = raw.get("caption")
        topic = extract_primary_hashtag(caption)

        # Parse insights metrics if available
        insights_data = raw.get("insights", {}).get("data", [])
        metric_dict: Dict[str, int] = {}
        for entry in insights_data:
            name = entry.get("name")
            vals = entry.get("values", [])
            if vals and "value" in vals[0]:
                metric_dict[name] = vals[0]["value"]

        impressions = metric_dict.get("impressions")
        reach = metric_dict.get("reach")
        saved = metric_dict.get("saved")
        shares = metric_dict.get("shares")
        plays = metric_dict.get("plays")

        likes = raw.get("like_count")
        comments = raw.get("comments_count")

        # For Instagram videos/reels, plays is mapped to views
        views = plays if (plays is not None) else None

        return NormalizedContent(
            platform="instagram",
            content_id=raw["id"],
            content_type=content_type,
            published_at=pub_dt,
            title=caption[:100] + "..." if caption and len(caption) > 100 else caption,
            url=raw.get("permalink"),
            views=views,
            impressions=impressions,
            reach=reach,
            likes=likes,
            comments=comments,
            shares=shares,
            saves=saved,
            watch_time=None,  # Not provided in Graph API
            average_view_duration=None,  # Not provided in Graph API
            followers_gained=None,  # Graph API media insights do not track post-level follower conversions
            topic=topic,
            platform_specific={
                "media_type": media_type,
                "media_product_type": product_type,
                "plays": plays,
            },
        )

    def _fetch_live_user(self, user_id: str) -> Dict[str, Any]:
        with httpx.Client(timeout=10.0) as client:
            resp = client.get(
                f"{self.GRAPH_API_BASE}/{user_id}",
                params={
                    "fields": "id,username,name,biography,followers_count,follows_count,media_count,profile_picture_url",
                    "access_token": self.api_key,
                },
            )
            resp.raise_for_status()
            return resp.json()

    def _fetch_live_media(self, user_id: str, limit: int) -> List[Dict[str, Any]]:
        with httpx.Client(timeout=15.0) as client:
            resp = client.get(
                f"{self.GRAPH_API_BASE}/{user_id}/media",
                params={
                    "fields": "id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count,insights.metric(impressions,reach,saved,shares,plays)",
                    "limit": min(limit, 100),
                    "access_token": self.api_key,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", [])
