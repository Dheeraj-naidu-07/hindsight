"""
End-to-End Test for the Complete 10-Layer Content Strategy Agent.
Strictly verifies the central HackWithHyderabad 3.0 problem statement:
INTERACTION 1: Historical Analytics -> Strategy A (Exploratory baseline)
OUTCOME LOOP:  Execution Results -> Social Analytics -> Learning -> Hindsight Retain
INTERACTION 2: New Analytics + Hindsight Recalled Lesson -> Strategy B (Measurably altered by learned experience)
"""

from __future__ import annotations

from agent.orchestrator.agent_orchestrator import ContentStrategyAgentOrchestrator
from learning.learning_service import LearningService
from models.brand import BrandProfile, BrandVoicePreferences


def test_complete_hindsight_learning_loop_e2e(
    brand_repo,
    strategy_repo,
    outcome_repo,
    sample_analytics_result,
    hindsight_wrapper,
):
    brand = BrandProfile(
        brand_id="e2e_agentic_brand",
        name="Agentic Cloud Systems",
        identity="Enterprise Infrastructure and Observability Platform",
        target_audience="DevOps and Distributed Systems Engineers",
        voice_preferences=BrandVoicePreferences(
            tone="Deeply technical, evidence-first",
            communication_style="Hands-on debugging and architectural diagrams",
            preferred_topics=["Distributed Tracing", "Kubernetes", "Memory Leaks"],
        ),
    )

    orchestrator = ContentStrategyAgentOrchestrator(
        brand_repo=brand_repo,
        strategy_repo=strategy_repo,
    )

    learning_service = LearningService(
        strategy_repo=strategy_repo,
    )

    # -------------------------------------------------------------------------
    # STEP 1: Interaction 1 -> Strategy A (No prior memory in Hindsight bank)
    # -------------------------------------------------------------------------
    strategy_a, analytics_a, context_a = orchestrator.execute_strategy_pipeline(
        brand_id=brand.brand_id,
        platform="youtube",
        account_id="UC_x5XG1OV2P6uZZ5FSM9Ttw",
        objective="Establish technical presence",
        analytics_result=sample_analytics_result,
        custom_brand_profile=brand,
    )

    assert strategy_a is not None
    assert strategy_a.brand_id == brand.brand_id
    # In Interaction 1, there were zero prior memories
    assert len(strategy_a.recalled_experiences) == 0
    assert "Initial exploratory strategy" in strategy_a.rationale
    assert strategy_a.posting_recommendations.frequency_per_week == 2.0
    primary_format_a = strategy_a.recommended_formats[0].format_name
    assert primary_format_a == "video"

    # -------------------------------------------------------------------------
    # STEP 2: Actual Performance -> Outcome Analysis -> Learn -> Hindsight Retain
    # -------------------------------------------------------------------------
    execution_analytics = sample_analytics_result.model_copy(deep=True)
    baseline_median = sample_analytics_result.baseline.median_engagement_rate or 1.0
    execution_analytics.content_summary.median_engagement_rate = round(baseline_median * 1.35, 2)

    outcome_analysis = learning_service.process_strategy_outcome(
        strategy_id=strategy_a.strategy_id,
        new_analytics=execution_analytics,
    )

    assert outcome_analysis.strategy_id == strategy_a.strategy_id
    assert outcome_analysis.hindsight_memory_id is not None
    reusable_lesson = outcome_analysis.extracted_reusable_lesson
    assert "outperformed account baselines" in reusable_lesson.lower() or "relative er" in reusable_lesson.lower()

    # -------------------------------------------------------------------------
    # STEP 3: Interaction 2 -> New Request + Hindsight Recall -> Strategy B
    # -------------------------------------------------------------------------
    strategy_b, analytics_b, context_b = orchestrator.execute_strategy_pipeline(
        brand_id=brand.brand_id,
        platform="youtube",
        account_id="UC_x5XG1OV2P6uZZ5FSM9Ttw",
        objective="Accelerate engineering adoption",
        analytics_result=sample_analytics_result,
        custom_brand_profile=brand,
    )

    # Verify Strategy B incorporated the Hindsight memory
    assert strategy_b is not None
    assert strategy_b.strategy_id != strategy_a.strategy_id
    assert len(strategy_b.recalled_experiences) > 0

    recalled_citation = strategy_b.recalled_experiences[0]
    assert recalled_citation.memory_id == outcome_analysis.hindsight_memory_id
    assert "Hindsight learning" in strategy_b.rationale

    # Verify Strategy B is measurably different from Strategy A
    primary_format_b = strategy_b.recommended_formats[0].format_name
    assert primary_format_b == "short"  # Shifted from video to short based on learned lesson!
    assert strategy_b.posting_recommendations.frequency_per_week == 4.0  # Increased cadence for high-yield format!

    # Verify topic shift to debugging & practical breakdowns
    assert any("Debugging" in theme.topic for theme in strategy_b.content_themes)
