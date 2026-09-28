"""
Learning Service Orchestrator.
Executes the second critical loop:
PREVIOUS STRATEGY -> ACTUAL NEW PERFORMANCE -> SOCIAL ANALYTICS -> COMPARE CONTEXT -> EXTRACT LESSON -> HINDSIGHT REMEMBER -> FUTURE STRATEGY IMPROVES.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional
from database.connection import get_db
from database.repositories.strategy_repository import StrategyRepository
from learning.lesson_extraction.extractor import LessonExtractor
from learning.memory_update.updater import MemoryUpdater
from learning.outcome_analysis.analyzer import OutcomeAnalyzer
from models.outcome import StrategyOutcomeAnalysis
from social_analytics.models.output import AnalyticsResult

logger = logging.getLogger(__name__)


class LearningService:
    """Coordinates post-strategy performance analysis, lesson extraction, and Hindsight memory update."""

    def __init__(
        self,
        strategy_repo: Optional[StrategyRepository] = None,
        outcome_analyzer: Optional[OutcomeAnalyzer] = None,
        lesson_extractor: Optional[LessonExtractor] = None,
        memory_updater: Optional[MemoryUpdater] = None,
    ):
        from database.repositories.outcome_repository import OutcomeRepository
        self.strategy_repo = strategy_repo or StrategyRepository(get_db())
        self.analyzer = outcome_analyzer or OutcomeAnalyzer()
        self.extractor = lesson_extractor or LessonExtractor()
        self.updater = memory_updater or MemoryUpdater(outcome_repo=OutcomeRepository(self.strategy_repo.db))

    def process_strategy_outcome(
        self,
        strategy_id: str,
        new_analytics: AnalyticsResult,
        outcome_id: Optional[str] = None,
    ) -> StrategyOutcomeAnalysis:
        """
        Processes post-execution results:
        1. Fetches previous strategy.
        2. Compares actual results against baseline and recommendations.
        3. Extracts high-signal reusable lesson.
        4. Retains memory into Hindsight.
        5. Saves outcome record to database.
        """
        strategy = self.strategy_repo.get_by_id(strategy_id)
        if not strategy:
            raise ValueError(f"Strategy with ID '{strategy_id}' not found in database.")

        brand_id = strategy.brand_id

        # 1. Compare actual performance against plan
        comparisons, observed_diff = self.analyzer.analyze(
            strategy=strategy,
            new_analytics=new_analytics,
        )

        # 2. Extract non-causal, reusable experience
        experience = self.extractor.extract_reusable_experience(
            bank_id=brand_id,
            strategy=strategy,
            comparisons=comparisons,
            observed_difference=observed_diff,
            new_analytics=new_analytics,
        )

        outcome_id = outcome_id or f"out_{uuid.uuid4().hex[:12]}"
        analysis = StrategyOutcomeAnalysis(
            outcome_id=outcome_id,
            strategy_id=strategy_id,
            brand_id=brand_id,
            metric_comparisons=comparisons,
            observed_difference=observed_diff,
            extracted_reusable_lesson=experience.lesson,
            raw_analytics_summary={
                "total_posts": new_analytics.content_summary.total_posts,
                "median_er": new_analytics.content_summary.median_engagement_rate,
                "er_basis": new_analytics.content_summary.engagement_rate_basis,
                "platform": new_analytics.account.platform,
            },
        )

        # 3. Store in Hindsight & persist in DB
        memory_id = self.updater.update_memory_and_record_outcome(
            strategy_id=strategy_id,
            brand_id=brand_id,
            experience=experience,
            outcome_analysis=analysis,
        )
        analysis.hindsight_memory_id = memory_id

        return analysis
