"""
Tests for Layer 3: Social Analytics Integration & Evidence Extraction.
Verifies AnalyticsResult -> backend evidence -> content gap detection.
"""

from __future__ import annotations

from services.analytics_service.service import AnalyticsService
from services.analytics_service.evidence_extractor import AnalyticsEvidenceExtractor


def test_analytics_service_extracts_evidence_deterministically(sample_analytics_result, sample_brand):
    service = AnalyticsService()
    evidence = service.extract_evidence(
        analytics=sample_analytics_result,
        brand_preferred_topics=sample_brand.voice_preferences.preferred_topics,
    )

    assert evidence.platform == "youtube"
    assert evidence.total_posts == sample_analytics_result.content_summary.total_posts
    assert evidence.sample_size == sample_analytics_result.data_quality.sample_size
    assert len(evidence.key_observations) == len(sample_analytics_result.observations)
    assert len(evidence.top_content_formats) > 0


def test_content_gap_detection(sample_analytics_result):
    preferred_topics = ["Distributed Systems", "Debugging", "Quantum Computing"]
    evidence = AnalyticsEvidenceExtractor.extract_evidence(
        analytics=sample_analytics_result,
        brand_preferred_topics=preferred_topics,
    )

    gap_topics = {g.topic: g.status for g in evidence.content_gaps}
    assert "Quantum Computing" in gap_topics
    assert gap_topics["Quantum Computing"] == "uncovered"


def test_insufficient_sample_size_flag(sample_analytics_result):
    evidence = AnalyticsEvidenceExtractor.extract_evidence(sample_analytics_result)
    assert evidence.insufficient_sample_size == sample_analytics_result.data_quality.insufficient_sample_size
