"""
Tests for Layer 7: Content Strategy Agent Orchestration.
"""

from __future__ import annotations

from agent.orchestrator.agent_orchestrator import ContentStrategyAgentOrchestrator
from models.strategy import ContentStrategy


def test_agent_orchestrator_pipeline_execution(
    sample_brand,
    sample_analytics_result,
    brand_repo,
    strategy_repo,
    content_repo,
    hindsight_wrapper,
):
    orchestrator = ContentStrategyAgentOrchestrator(
        brand_repo=brand_repo,
        strategy_repo=strategy_repo,
    )

    strategy, analytics, context = orchestrator.execute_strategy_pipeline(
        brand_id=sample_brand.brand_id,
        platform="youtube",
        account_id="UC_x5XG1OV2P6uZZ5FSM9Ttw",
        objective="Drive engineering engagement and technical authority",
        analytics_result=sample_analytics_result,
        custom_brand_profile=sample_brand,
    )

    assert isinstance(strategy, ContentStrategy)
    assert strategy.brand_id == sample_brand.brand_id
    assert len(strategy.content_themes) > 0
    assert len(strategy.recommended_formats) > 0
    assert strategy.posting_recommendations.frequency_per_week > 0

    # Verify strategy was persisted to database
    db_strat = strategy_repo.get_by_id(strategy.strategy_id)
    assert db_strat is not None
    assert db_strat.objective == strategy.objective
