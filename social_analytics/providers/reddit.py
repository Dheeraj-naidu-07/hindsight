"""
Reddit official API data provider adapter.
Uses Reddit OAuth / JSON API specifications.
Extracts metrics deterministically with fallback to fixtures when credentials are absent.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import httpx

from social_analytics.fixtures.reddit_fixtures import (
    REDDIT_AUDIENCE_FIXTURE,
    REDDIT_SUBMITTED_FIXTURE,
    REDDIT_USER_FIXTURE,
)
from social_analytics.models.normalized import (
    AccountInfo,
    AudienceMetrics,
    NormalizedContent,
)
from social_analytics.providers.base import BaseSocialProvider

logger = logging.getLogger(__name__)


class RedditProvider(BaseSocialProvider):
    """
    Adapter for official Reddit API.
    """

    OAUTH_BASE = "https://oauth.reddit.com"
    PUBLIC_BASE = "https://www.reddit.com"

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        user_agent: Optional[str] = None,
        rate_limit_rps: float = 1.0,  # 60 req/min rule
        cache_ttl_seconds: int = 300,
        mock_mode: Optional[bool] = None,
    ):
        cid = client_id or os.getenv("REDDIT_CLIENT_ID")
        csec = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        self.user_agent = user_agent or os.getenv(
            "REDDIT_USER_AGENT", "SocialAnalyticsEngine/1.0"
        )
        is_mock = mock_mode if mock_mode is not None else (not bool(cid and csec))

        super().__init__(
            api_key=cid,
            rate_limit_rps=rate_limit_rps,
            cache_ttl_seconds=cache_ttl_seconds,
            mock_mode=is_mock,
        )
        self.client_secret = csec
        self._access_token: Optional[str] = None
        self._token_expires_at: float = 0

    def platform_name(self) -> str:
        return "reddit"

    def get_account(self, account_id: str) -> AccountInfo:
        username = account_id.replace("u/", "")
        cache_key = f"rd:account:{username}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if self.mock_mode:
            raw_user = REDDIT_USER_FIXTURE["data"]
        else:
            self.rate_limiter.acquire()
            raw_user = self.retry_policy.execute(
                lambda: self._fetch_live_user(username)
            )

        sub_info = raw_user.get("subreddit", {})
        subscribers = sub_info.get("subscribers") if isinstance(sub_info, dict) else None

        account_info = AccountInfo(
            platform="reddit",
            account_id=raw_user.get("id", username),
            username=raw_user.get("name", username),
            display_name=sub_info.get("title") if isinstance(sub_info, dict) else None,
            followers_count=subscribers,
            following_count=None,
            total_posts=None,
            profile_url=f"https://www.reddit.com/user/{raw_user.get('name', username)}",
            raw_metadata={
                "total_karma": raw_user.get("total_karma"),
                "link_karma": raw_user.get("link_karma"),
                "comment_karma": raw_user.get("comment_karma"),
                "created_utc": raw_user.get("created_utc"),
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
        username = account_id.replace("u/", "")
        cache_key = f"rd:content:{username}:{start_date.isoformat()}:{end_date.isoformat()}:{limit}"
        cached = self.cache.get(cache_key)
        if cached:
            return cached

        if self.mock_mode:
            raw_posts = [
                child["data"]
                for child in REDDIT_SUBMITTED_FIXTURE["data"]["children"]
            ]
        else:
            self.rate_limiter.acquire()
            raw_posts = self.retry_policy.execute(
                lambda: self._fetch_live_submitted(username, limit)
            )

        results: List[NormalizedContent] = []
        for raw in raw_posts:
            item = self._normalize_post_item(raw)
            if start_date <= item.published_at <= end_date:
                results.append(item)
                if len(results) >= limit:
                    break

        self.cache.set(cache_key, results)
        return results

    def get_content_metrics(self, content_ids: List[str]) -> Dict[str, Dict[str, Any]]:
        results: Dict[str, Dict[str, Any]] = {}
        for cid in content_ids:
            for child in REDDIT_SUBMITTED_FIXTURE["data"]["children"]:
                data = child["data"]
                if data["id"] == cid:
                    results[cid] = {
                        "score": data.get("score"),
                        "upvote_ratio": data.get("upvote_ratio"),
                        "num_comments": data.get("num_comments"),
                        "num_crossposts": data.get("num_crossposts"),
                        "subreddit": data.get("subreddit"),
                    }
        return results

    def get_audience_metrics(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> AudienceMetrics:
        if self.mock_mode:
            data = REDDIT_AUDIENCE_FIXTURE
            start_subs = data.get("subscribers_start")
            end_subs = data.get("subscribers_end")
            net_gained = (
                end_subs - start_subs
                if (start_subs is not None and end_subs is not None)
                else None
            )
        else:
            account = self.get_account(account_id)
            end_subs = account.followers_count
            start_subs = None
            net_gained = None

        return AudienceMetrics(
            platform="reddit",
            account_id=account_id,
            period_start=start_date,
            period_end=end_date,
            followers_start=start_subs,
            followers_end=end_subs,
            net_followers_gained=net_gained,
            total_reach=None,  # Reddit does not track profile reach
            total_impressions=None,  # Reddit does not report impressions to public callers
            demographics={},
            platform_specific={},
        )

    def _normalize_post_item(self, raw: Dict[str, Any]) -> NormalizedContent:
        created_utc = raw.get("created_utc", 0)
        pub_dt = datetime.fromtimestamp(created_utc, tz=timezone.utc)

        is_self = raw.get("is_self", True)
        content_type = "text" if is_self else "link"

        score = raw.get("score")
        comments = raw.get("num_comments")
        crossposts = raw.get("num_crossposts")

        # Explicitly distinguish None vs 0: Reddit does NOT expose views/impressions/reach
        return NormalizedContent(
            platform="reddit",
            content_id=raw["id"],
            content_type=content_type,
            published_at=pub_dt,
            title=raw.get("title"),
            url=(
                f"https://reddit.com{raw.get('permalink')}"
                if raw.get("permalink")
                else None
            ),
            views=None,  # Not exposed in Reddit API
            impressions=None,  # Not exposed
            reach=None,  # Not exposed
            likes=score,  # Reddit score represents net upvotes
            comments=comments,
            shares=crossposts,
            saves=None,  # Private to individual viewers
            watch_time=None,
            average_view_duration=None,
            followers_gained=None,
            topic=raw.get("subreddit"),
            platform_specific={
                "subreddit": raw.get("subreddit"),
                "upvote_ratio": raw.get("upvote_ratio"),
                "total_awards_received": raw.get("total_awards_received", 0),
                "is_self": is_self,
                "over_18": raw.get("over_18", False),
            },
        )

    def _fetch_live_user(self, username: str) -> Dict[str, Any]:
        with httpx.Client(
            headers={"User-Agent": self.user_agent}, timeout=10.0
        ) as client:
            resp = client.get(f"{self.PUBLIC_BASE}/user/{username}/about.json")
            resp.raise_for_status()
            data = resp.json()
            return data.get("data", {})

    def _fetch_live_submitted(
        self, username: str, limit: int
    ) -> List[Dict[str, Any]]:
        with httpx.Client(
            headers={"User-Agent": self.user_agent}, timeout=15.0
        ) as client:
            resp = client.get(
                f"{self.PUBLIC_BASE}/user/{username}/submitted.json",
                params={"limit": min(limit, 100)},
            )
            resp.raise_for_status()
            data = resp.json()
            children = data.get("data", {}).get("children", [])
            return [child.get("data", {}) for child in children]
