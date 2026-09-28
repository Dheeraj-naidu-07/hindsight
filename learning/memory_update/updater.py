"""
Memory Updater for Hindsight.
Persists synthesized experiences to Hindsight memory bank and logs DB outcomes.
"""

from __future__ import annotations

import json
import logging
import uuid
from typing import Optional
from database.connection import get_db
from database.models import StrategyOutcomeRecord
from database.repositories.outcome_repository import OutcomeRepository
from hindsight.memory.experience_manager import ExperienceManager
from hindsight.schemas.memory_models import ReusableExperience
from models.outcome import StrategyOutcomeAnalysis

logger = logging.getLogger(__name__)


class MemoryUpdater:
    """Coordinates writing experiences to Hindsight and updating database outcome records."""

    def __init__(
        self,
        experience_manager: Optional[ExperienceManager] = None,
        outcome_repo: Optional[OutcomeRepository] = None,
    ):
        self.experience_manager = experience_manager or ExperienceManager()
        self.outcome_repo = outcome_repo or OutcomeRepository(get_db())

    def update_memory_and_record_outcome(
        self,
        strategy_id: str,
        brand_id: str,
        experience: ReusableExperience,
        outcome_analysis: StrategyOutcomeAnalysis,
    ) -> str:
        """
        1. Store experience in Hindsight memory bank.
        2. Persist outcome analysis in database.
        """
        # Store in Hindsight
        memory_id = self.experience_manager.remember_experience(experience)
        outcome_analysis.hindsight_memory_id = memory_id

        # Persist in DB
        db_record = StrategyOutcomeRecord(
            id=outcome_analysis.outcome_id or f"out_{uuid.uuid4().hex[:12]}",
            strategy_id=strategy_id,
            actual_metrics_json=json.dumps(outcome_analysis.raw_analytics_summary),
            expected_metrics_json=json.dumps([c.model_dump() for c in outcome_analysis.metric_comparisons]),
            observed_difference=outcome_analysis.observed_difference,
            reusable_lesson=experience.lesson,
            hindsight_memory_id=memory_id,
            created_at=outcome_analysis.analysis_timestamp,
        )
        self.outcome_repo.create(db_record)

        logger.info(
            f"Successfully updated Hindsight memory '{memory_id}' and recorded outcome for strategy '{strategy_id}'"
        )
        return memory_id or "mem_deduplicated"
