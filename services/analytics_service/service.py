"""
Analytics Integration Service.
Acts as the official boundary adapter between the SocialMediaAnalyticsEngine
and the downstream Agent Orchestrator.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from database.connection import get_db
from database.models import ContentItemRecord, ContentPerformanceRecord
from database.repositories.content_repository import ContentRepository
from services.analytics_service.evidence_extractor import (
    AnalyticsEvidenceExtractor,
    FormattedEvidence,
)
from social_analytics.engine.analytics_engine import SocialMediaAnalyticsEngine
from social_analytics.models.normalized import NormalizedContent
from social_analytics.models.output import AnalyticsResult
from social_analytics.providers.base import BaseSocialProvider
from social_analytics.providers.instagram import InstagramProvider
from social_analytics.providers.reddit import RedditProvider
from social_analytics.providers.youtube import YouTubeProvider

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service consuming SocialMediaAnalyticsEngine to provide grounded analytics to downstream agents."""

    def __init__(self, content_repo: Optional[ContentRepository] = None):
        self.content_repo = content_repo or ContentRepository(get_db())

    def get_provider_for_platform(
        self,
        platform: Literal["youtube", "instagram", "reddit"],
        api_key: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> BaseSocialProvider:
        """Instantiate official platform provider with provided or environment API keys."""
        if platform == "youtube":
            return YouTubeProvider(api_key=api_key)
        elif platform == "instagram":
            return InstagramProvider(access_token=api_key)
        elif platform == "reddit":
            return RedditProvider(client_id=api_key, client_secret=client_secret)
        raise ValueError(f"Unsupported social platform: {platform}")

    def run_analytics(
        self,
        platform: Literal["youtube", "instagram", "reddit"],
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        previous_period_start: Optional[datetime] = None,
        previous_period_end: Optional[datetime] = None,
        historical_baseline_items: Optional[List[NormalizedContent]] = None,
        content_items: Optional[List[NormalizedContent]] = None,
        provider: Optional[BaseSocialProvider] = None,
        api_key: Optional[str] = None,
        client_secret: Optional[str] = None,
    ) -> AnalyticsResult:
        """
        Execute deterministic analytics via SocialMediaAnalyticsEngine.
        DOES NOT recalculate or duplicate metrics.
        """
        active_provider = provider or self.get_provider_for_platform(
            platform,
            api_key=api_key,
            client_secret=client_secret,
        )
        engine = SocialMediaAnalyticsEngine(active_provider)

        result = engine.run_analysis(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            previous_period_start=previous_period_start,
            previous_period_end=previous_period_end,
            historical_baseline_items=historical_baseline_items,
            content_items=content_items,
        )
        return result

    def extract_evidence(
        self,
        analytics: AnalyticsResult,
        brand_preferred_topics: Optional[List[str]] = None,
    ) -> FormattedEvidence:
        """Extract evidence and gap signals from AnalyticsResult."""
        return AnalyticsEvidenceExtractor.extract_evidence(
            analytics=analytics,
            brand_preferred_topics=brand_preferred_topics,
        )

    def persist_analytics_items(
        self,
        brand_id: str,
        analytics: AnalyticsResult,
    ) -> None:
        """Optionally record analyzed items and their performance in the local application DB."""
        measured_at = analytics.data_quality.collection_timestamp
        for item in analytics.top_content + analytics.bottom_content:
            record_id = f"{analytics.account.platform}_{item.content_id}"
            c_record = ContentItemRecord(
                id=record_id,
                brand_id=brand_id,
                platform=analytics.account.platform,
                content_id=item.content_id,
                topic=None,
                content_type=item.content_type,
                title=item.title,
                url=None,
                published_at=item.published_at,
                metadata_json="{}",
            )
            self.content_repo.save_content_item(c_record)

            perf_record = ContentPerformanceRecord(
                id=f"perf_{record_id}_{measured_at}",
                content_item_id=record_id,
                views=item.views,
                engagements=item.total_engagements,
                engagement_rate=item.engagement_rate,
                likes=item.likes,
                comments=item.comments,
                shares=item.shares,
                saves=item.saves,
                measured_at=measured_at,
                source=f"{analytics.account.platform}_analytics",
            )
            self.content_repo.save_performance(perf_record)
