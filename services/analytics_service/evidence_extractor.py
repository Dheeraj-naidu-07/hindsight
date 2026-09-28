"""
Deterministic Evidence Extractor.
Extracts empirical facts, format rankings, topic signals, and content gaps
from AnalyticsResult without LLM approximation or hallucination.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Set
from pydantic import BaseModel, Field
from social_analytics.models.output import AnalyticsResult


class ContentGapSignal(BaseModel):
    topic: str
    status: str = Field(..., description="uncovered | underrepresented | overrepresented | well_covered")
    frequency_count: int
    rationale: str


class FormattedEvidence(BaseModel):
    platform: str
    sample_size: int
    total_posts: int
    median_engagement_rate: Optional[float] = None
    engagement_rate_basis: Optional[str] = None
    top_performing_topics: List[str] = Field(default_factory=list)
    underperforming_topics: List[str] = Field(default_factory=list)
    top_content_formats: List[str] = Field(default_factory=list)
    bottom_content_formats: List[str] = Field(default_factory=list)
    content_gaps: List[ContentGapSignal] = Field(default_factory=list)
    key_observations: List[str] = Field(default_factory=list)
    data_quality_warnings: List[str] = Field(default_factory=list)
    insufficient_sample_size: bool = False


class AnalyticsEvidenceExtractor:
    """Extracts structured evidence items from an AnalyticsResult."""

    @staticmethod
    def extract_evidence(
        analytics: AnalyticsResult,
        brand_preferred_topics: Optional[List[str]] = None,
    ) -> FormattedEvidence:
        brand_preferred_topics = brand_preferred_topics or []
        
        # 1. Platform & general summary
        platform = analytics.account.platform
        sample_size = analytics.data_quality.sample_size
        total_posts = analytics.content_summary.total_posts
        median_er = analytics.content_summary.median_engagement_rate
        er_basis = analytics.content_summary.engagement_rate_basis

        # 2. Topic performance extraction from top_content and bottom_content
        topic_frequency: Dict[str, int] = {}
        high_perf_topics: List[str] = []
        low_perf_topics: List[str] = []

        for item in analytics.top_content:
            # Check baseline relative difference
            topic_str = item.title or item.content_id
            if item.baseline_comparison.relative_difference_percent is not None and item.baseline_comparison.relative_difference_percent > 0:
                high_perf_topics.append(f"{item.content_type}: {topic_str[:50]}")
            # Track format
            topic_frequency[item.content_type] = topic_frequency.get(item.content_type, 0) + 1

        for item in analytics.bottom_content:
            topic_str = item.title or item.content_id
            if item.baseline_comparison.relative_difference_percent is not None and item.baseline_comparison.relative_difference_percent < 0:
                low_perf_topics.append(f"{item.content_type}: {topic_str[:50]}")
            topic_frequency[item.content_type] = topic_frequency.get(item.content_type, 0) + 1

        # 3. Format rankings from content_type_performance
        sorted_formats = sorted(
            analytics.content_type_performance.items(),
            key=lambda x: (x[1].median_engagement_rate or 0.0),
            reverse=True,
        )
        top_formats = [f"{fmt} (median ER: {data.median_engagement_rate}%)" for fmt, data in sorted_formats if data.median_engagement_rate is not None]
        bottom_formats = [f"{fmt} (median ER: {data.median_engagement_rate}%)" for fmt, data in reversed(sorted_formats) if data.median_engagement_rate is not None]

        # 4. Content Gap Analysis: Compare brand target topics vs covered content
        content_gaps: List[ContentGapSignal] = []
        covered_topics_lower: Set[str] = set()

        for item in analytics.top_content + analytics.bottom_content:
            if item.title:
                for word in item.title.lower().split():
                    covered_topics_lower.add(word.strip("#,.-!?"))

        for preferred in brand_preferred_topics:
            pref_lower = preferred.lower()
            matching_mentions = sum(
                1 for item in (analytics.top_content + analytics.bottom_content)
                if item.title and pref_lower in item.title.lower()
            )
            if matching_mentions == 0:
                content_gaps.append(
                    ContentGapSignal(
                        topic=preferred,
                        status="uncovered",
                        frequency_count=0,
                        rationale=f"Zero content published under brand pillar '{preferred}' in analyzed period.",
                    )
                )
            elif matching_mentions == 1:
                content_gaps.append(
                    ContentGapSignal(
                        topic=preferred,
                        status="underrepresented",
                        frequency_count=1,
                        rationale=f"Only 1 post published for core pillar '{preferred}', representing a potential volume gap.",
                    )
                )
            else:
                content_gaps.append(
                    ContentGapSignal(
                        topic=preferred,
                        status="well_covered",
                        frequency_count=matching_mentions,
                        rationale=f"Core pillar '{preferred}' covered {matching_mentions} times.",
                    )
                )

        # 5. Key observations
        key_obs = [obs.observation for obs in analytics.observations]

        # 6. Quality warnings
        quality_warnings = list(analytics.data_quality.data_quality_warnings)
        if analytics.data_quality.insufficient_sample_size:
            quality_warnings.append(
                f"Sample size {sample_size} is low; rankings should be treated as indicative."
            )

        return FormattedEvidence(
            platform=platform,
            sample_size=sample_size,
            total_posts=total_posts,
            median_engagement_rate=median_er,
            engagement_rate_basis=er_basis,
            top_performing_topics=high_perf_topics[:5],
            underperforming_topics=low_perf_topics[:5],
            top_content_formats=top_formats[:3],
            bottom_content_formats=bottom_formats[:3],
            content_gaps=content_gaps,
            key_observations=key_obs,
            data_quality_warnings=quality_warnings,
            insufficient_sample_size=analytics.data_quality.insufficient_sample_size,
        )
