"""
Tests for Layer 8: Outcome Analysis and Learning Loop.
"""

from __future__ import annotations

import json
from database.models import StrategyRecord
from learning.learning_service import LearningService


def test_learning_service_processes_outcome(
    strategy_repo,
    outcome_repo,
    experience_manager,
    sample_analytics_result,
):
    strat = StrategyRecord(
        id="strat_test_learn",
        brand_id="brand_learn",
        objective="Drive Tech Engagement",
        target_audience="Engineers",
        recommended_platforms_json=json.dumps(["youtube"]),
        content_themes_json=json.dumps([{"topic": "Debugging", "priority": "high"}]),
        recommended_formats_json=json.dumps([{"format_name": "short"}]),
        posting_recommendations_json=json.dumps({"frequency_per_week": 3.0}),
        rationale="Initial baseline test",
        supporting_evidence_json=json.dumps({}),
        recalled_memories_json=json.dumps([]),
    )
    strategy_repo.create(strat)

    service = LearningService(
        strategy_repo=strategy_repo,
        memory_updater=None,  # defaults to clean memory updater
    )

    outcome_analysis = service.process_strategy_outcome(
        strategy_id="strat_test_learn",
        new_analytics=sample_analytics_result,
    )

    assert outcome_analysis.strategy_id == "strat_test_learn"
    assert len(outcome_analysis.metric_comparisons) > 0
    assert outcome_analysis.extracted_reusable_lesson != ""
    assert outcome_analysis.hindsight_memory_id is not None

    # Verify outcome persisted in database
    db_outcome = outcome_repo.get_by_strategy_id("strat_test_learn")
    assert db_outcome is not None
    assert db_outcome.hindsight_memory_id == outcome_analysis.hindsight_memory_id
