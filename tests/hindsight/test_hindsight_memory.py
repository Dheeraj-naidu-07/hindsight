"""
Tests for Layer 4 & 5: Hindsight Memory Integration & Bounded Recall.
"""

from __future__ import annotations

from hindsight.schemas.memory_models import MemoryRecallQuery, ReusableExperience


def test_experience_manager_retains_and_deduplicates(experience_manager, experience_retriever):
    exp1 = ReusableExperience(
        bank_id="brand_test_bank",
        lesson="Educational short-form technical content performed above baseline across multiple posts.",
        strategy_used="Promote debugging tutorials on YouTube",
        platform="youtube",
        content_type="short",
        topic="Debugging",
        observed_outcome="+38.2% median ER over baseline",
        supporting_evidence={"delta_pct": 38.2, "sample_size": 10},
        tags=["youtube", "short", "debugging"],
    )

    mem_id = experience_manager.remember_experience(exp1)
    assert mem_id is not None

    # Test deduplication: identical experience should be skipped
    dup_id = experience_manager.remember_experience(exp1)
    assert dup_id is None

    # Recall experience
    query = MemoryRecallQuery(
        bank_id="brand_test_bank",
        query="debugging short format engagement",
        platform="youtube",
    )
    results = experience_retriever.recall_experiences(query, max_items=5)
    assert len(results) == 1
    assert "Educational short-form technical content" in results[0].text
    assert "youtube" in results[0].text.lower()


def test_bounded_recall_caps_items(experience_manager, experience_retriever):
    bank = "bounded_bank"
    for i in range(10):
        exp = ReusableExperience(
            bank_id=bank,
            lesson=f"Lesson number {i}: Unique insight for testing recall bounds on architecture.",
            strategy_used=f"Strategy {i}",
            platform="youtube",
            content_type="video",
            observed_outcome=f"Metric delta {i}",
            tags=["youtube", "video"],
        )
        experience_manager.remember_experience(exp)

    query = MemoryRecallQuery(
        bank_id=bank,
        query="Unique insight architecture",
        platform="youtube",
    )
    # Request cap at 3
    results = experience_retriever.recall_experiences(query, max_items=3)
    assert len(results) <= 3
