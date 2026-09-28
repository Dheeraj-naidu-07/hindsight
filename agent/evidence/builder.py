"""
Evidence & Grounded Context Builder.
Assembles current analytics evidence, content gap signals, and recalled Hindsight experiences
into a unified, strictly bounded GroundedStrategyContext.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from agent.context.grounded_context import GroundedStrategyContext
from agent.recall.recall_selector import RecallSelector
from models.brand import BrandProfile
from services.analytics_service.service import AnalyticsService
from social_analytics.models.output import AnalyticsResult

logger = logging.getLogger(__name__)


class GroundedContextBuilder:
    """Builds complete GroundedStrategyContext from analytics and Hindsight memory."""

    def __init__(
        self,
        analytics_service: Optional[AnalyticsService] = None,
        recall_selector: Optional[RecallSelector] = None,
    ):
        self.analytics_service = analytics_service or AnalyticsService()
        self.recall_selector = recall_selector or RecallSelector()

    def build_context(
        self,
        brand: BrandProfile,
        objective: str,
        platform: str,
        analytics: AnalyticsResult,
        memory_bank_id: Optional[str] = None,
    ) -> GroundedStrategyContext:
        """Construct the grounded context separating analytics facts from recalled memories."""
        # 1. Deterministic evidence and gap extraction
        evidence = self.analytics_service.extract_evidence(
            analytics=analytics,
            brand_preferred_topics=brand.voice_preferences.preferred_topics,
        )

        # 2. Targeted memory recall from Hindsight
        bank_id = memory_bank_id or brand.brand_id
        recalled_memories = self.recall_selector.select_relevant_memories(
            bank_id=bank_id,
            platform=platform,
            objective=objective,
            evidence=evidence,
        )

        # 3. Explicit statistical and scope limitations
        limitations: List[str] = []
        if evidence.insufficient_sample_size:
            limitations.append(
                f"Sample size ({evidence.sample_size}) is below standard statistical threshold (5); "
                "findings must be treated as indicative rather than statistically conclusive."
            )
        if not recalled_memories:
            limitations.append(
                "No prior experiences recorded in Hindsight for this specific platform/topic set. "
                "Strategy relies purely on current analytics baseline."
            )

        return GroundedStrategyContext(
            brand=brand,
            objective=objective,
            target_platform=platform,
            current_evidence=evidence,
            recalled_experiences=recalled_memories,
            content_gaps=evidence.content_gaps,
            limitations=limitations,
        )
