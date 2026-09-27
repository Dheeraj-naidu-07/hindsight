"""
Normalized data models for social media content, accounts, and audience metrics.
Adheres to strict representation rules:
- 0 indicates the platform explicitly reported 0.
- None (null) indicates the metric is unavailable/unsupported.
- Unavailable metrics are never silently converted to 0.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class NormalizedContent(BaseModel):
    """
    Standard normalized schema for an individual piece of social media content.
    """
    model_config = ConfigDict(extra="ignore")

    platform: Literal["youtube", "instagram", "reddit"] = Field(
        ..., description="Social platform name"
    )
    content_id: str = Field(..., description="Unique platform identifier for the content item")
    content_type: str = Field(
        ..., description="Content format, e.g. 'video', 'short', 'reel', 'post', 'carousel', 'submission'"
    )
    published_at: datetime = Field(..., description="UTC publication timestamp")
    title: Optional[str] = Field(None, description="Title, caption headline, or post title")
    url: Optional[str] = Field(None, description="Direct URL to content item")

    # Volume and exposure metrics
    views: Optional[int] = Field(
        None, description="Total video/content views. None if unavailable; 0 if explicitly reported 0."
    )
    impressions: Optional[int] = Field(
        None, description="Total impressions. None if unavailable; 0 if explicitly reported 0."
    )
    reach: Optional[int] = Field(
        None, description="Unique accounts reached. None if unavailable; 0 if explicitly reported 0."
    )

    # Core interaction metrics
    likes: Optional[int] = Field(
        None, description="Total likes or upvotes. None if unavailable; 0 if explicitly reported 0."
    )
    comments: Optional[int] = Field(
        None, description="Total comments or replies. None if unavailable; 0 if explicitly reported 0."
    )
    shares: Optional[int] = Field(
        None, description="Total shares, reposts, or crossposts. None if unavailable; 0 if explicitly reported 0."
    )
    saves: Optional[int] = Field(
        None, description="Total saves or bookmarks. None if unavailable; 0 if explicitly reported 0."
    )

    # Consumption / watch metrics
    watch_time: Optional[float] = Field(
        None, description="Total watch time in seconds. None if unavailable."
    )
    average_view_duration: Optional[float] = Field(
        None, description="Average view duration in seconds. None if unavailable."
    )

    # Audience conversion
    followers_gained: Optional[int] = Field(
        None, description="Followers/subscribers directly attributed to this content item."
    )

    # Context & categorization
    topic: Optional[str] = Field(
        None, description="Topic tag, category name, or subreddit"
    )

    # Platform-specific preserved attributes
    platform_specific: Dict[str, Any] = Field(
        default_factory=dict,
        description="Preserved raw metrics unique to the platform (e.g. upvote_ratio, CTR, etc.)"
    )


class AccountInfo(BaseModel):
    """
    Standard normalized schema for a social media account or profile.
    """
    model_config = ConfigDict(extra="ignore")

    platform: Literal["youtube", "instagram", "reddit"]
    account_id: str
    username: str
    display_name: Optional[str] = None
    followers_count: Optional[int] = None
    following_count: Optional[int] = None
    total_posts: Optional[int] = None
    profile_url: Optional[str] = None
    raw_metadata: Dict[str, Any] = Field(default_factory=dict)


class AudienceMetrics(BaseModel):
    """
    Aggregated audience exposure and follower growth for an analysis window.
    """
    model_config = ConfigDict(extra="ignore")

    platform: Literal["youtube", "instagram", "reddit"]
    account_id: str
    period_start: datetime
    period_end: datetime
    followers_start: Optional[int] = None
    followers_end: Optional[int] = None
    net_followers_gained: Optional[int] = None
    total_reach: Optional[int] = None
    total_impressions: Optional[int] = None
    demographics: Dict[str, Any] = Field(default_factory=dict)
    platform_specific: Dict[str, Any] = Field(default_factory=dict)
