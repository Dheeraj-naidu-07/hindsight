"""
Tests for Layer 2: Database and Application Repositories.
"""

from __future__ import annotations

import json
from database.models import (
    BrandRecord,
    ContentItemRecord,
    ContentPerformanceRecord,
    StrategyRecord,
    StrategyOutcomeRecord,
)


def test_brand_repository_crud(brand_repo):
    brand = BrandRecord(
        id="brand_1",
        name="Acme Tech",
        identity="Enterprise Cloud Solutions",
        target_audience="DevOps Engineers",
        voice_tone="Professional",
        communication_style="Technical whitepapers",
    )
    brand_repo.create(brand)

    retrieved = brand_repo.get_by_id("brand_1")
    assert retrieved is not None
    assert retrieved.name == "Acme Tech"
    assert retrieved.target_audience == "DevOps Engineers"


def test_content_and_performance_repository(content_repo):
    item = ContentItemRecord(
        id="yt_12345",
        brand_id="brand_1",
        platform="youtube",
        content_id="12345",
        topic="Docker",
        content_type="short",
        title="Docker Optimization Tips",
        url="https://youtube.com/watch?v=12345",
        published_at="2026-09-15T12:00:00Z",
    )
    content_repo.save_content_item(item)

    perf = ContentPerformanceRecord(
        id="perf_1",
        content_item_id="yt_12345",
        views=15000,
        engagements=850,
        engagement_rate=5.67,
        likes=700,
        comments=100,
        shares=50,
        saves=None,
        measured_at="2026-09-20T12:00:00Z",
        source="youtube_analytics",
    )
    content_repo.save_performance(perf)

    results = content_repo.get_content_with_latest_performance("brand_1")
    assert len(results) == 1
    c, p = results[0]
    assert c.id == "yt_12345"
    assert p is not None
    assert p.views == 15000
    assert p.engagement_rate == 5.67


def test_strategy_and_outcome_repository(strategy_repo, outcome_repo, brand_repo):
    brand = BrandRecord(
        id="brand_2",
        name="Agentic AI Labs",
        identity="Agentic Systems",
        target_audience="AI Engineers",
        voice_tone="Cutting-edge",
        communication_style="Tutorials",
    )
    brand_repo.create(brand)

    strat = StrategyRecord(
        id="strat_abc",
        brand_id="brand_2",
        objective="Lead Generation",
        target_audience="AI Engineers",
        recommended_platforms_json=json.dumps(["youtube"]),
        content_themes_json=json.dumps([{"topic": "Agents", "priority": "high"}]),
        recommended_formats_json=json.dumps([{"format": "short"}]),
        posting_recommendations_json=json.dumps({"frequency": 3}),
        rationale="Empirical testing",
        supporting_evidence_json=json.dumps({"data": 1}),
        recalled_memories_json=json.dumps([]),
    )
    strategy_repo.create(strat)

    retrieved = strategy_repo.get_by_id("strat_abc")
    assert retrieved is not None
    assert retrieved.objective == "Lead Generation"
    assert retrieved.recommended_platforms == ["youtube"]

    outcome = StrategyOutcomeRecord(
        id="out_xyz",
        strategy_id="strat_abc",
        actual_metrics_json=json.dumps({"views": 25000}),
        expected_metrics_json=json.dumps([{"metric": "views"}]),
        observed_difference="Exceeded expectations by +25%",
        reusable_lesson="Shorts on Agent architectures drive outsized reach",
        hindsight_memory_id="mem_999",
    )
    outcome_repo.create(outcome)

    retrieved_out = outcome_repo.get_by_strategy_id("strat_abc")
    assert retrieved_out is not None
    assert retrieved_out.reusable_lesson == "Shorts on Agent architectures drive outsized reach"
    assert retrieved_out.hindsight_memory_id == "mem_999"
