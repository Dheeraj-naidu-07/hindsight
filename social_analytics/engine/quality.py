"""
Data quality audit and metadata verification.
Detects missing metrics, identifies platform-level limitations,
and flags small sample sizes without manufacturing false confidence.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, Optional

from social_analytics.models.normalized import NormalizedContent
from social_analytics.models.output import DataQuality

# Platform inherent metric support maps
PLATFORM_UNAVAILABLE_METRICS: Dict[str, List[str]] = {
    "youtube": ["reach", "saves", "profile_visits"],
    "instagram": ["watch_time", "average_view_duration", "subscribers_gained"],
    "reddit": ["views", "impressions", "reach", "saves", "watch_time", "average_view_duration"],
}

MINIMUM_RELIABLE_SAMPLE_SIZE = 5


def assess_data_quality(
    platform: Literal["youtube", "instagram", "reddit"],
    items: List[NormalizedContent],
    start_date: datetime,
    end_date: datetime,
    known_warnings: Optional[List[str]] = None,
) -> DataQuality:
    """
    Evaluates completeness, platform limitations, and sample size validity.
    """
    now_iso = datetime.now(timezone.utc).isoformat()
    duration_days = round((end_date - start_date).total_seconds() / 86400.0, 2)
    sample_size = len(items)

    warnings: List[str] = list(known_warnings or [])
    unavailable = PLATFORM_UNAVAILABLE_METRICS.get(platform, [])

    # Check for insufficient sample size
    insufficient = sample_size < MINIMUM_RELIABLE_SAMPLE_SIZE
    if insufficient:
        warnings.append(
            f"insufficient_sample_size: Sample size ({sample_size}) is below statistical "
            f"reliability threshold ({MINIMUM_RELIABLE_SAMPLE_SIZE}). Medians and rankings should be interpreted with caution."
        )

    # Detect missing metrics (metrics supported by the platform, but null across all retrieved items)
    missing: List[str] = []
    if sample_size > 0:
        if platform in ("youtube", "instagram"):
            if all(it.impressions is None for it in items):
                missing.append("impressions")
        if platform == "youtube":
            if all(it.watch_time is None for it in items):
                missing.append("watch_time")
            if all(it.shares is None for it in items):
                missing.append("shares")
        if platform == "instagram":
            if all(it.reach is None for it in items):
                missing.append("reach")
            if all(it.saves is None for it in items):
                missing.append("saves")

    # Check for items with zero views/impressions leading to rate omission
    zero_denominator_count = sum(
        1 for it in items if (it.reach == 0 or it.impressions == 0)
    )
    if zero_denominator_count > 0:
        warnings.append(
            f"{zero_denominator_count} items had 0 reach/impressions; rate calculations were omitted to prevent division by zero."
        )

    return DataQuality(
        source_platform=platform,
        collection_timestamp=now_iso,
        analysis_period={
            "start": start_date.isoformat(),
            "end": end_date.isoformat(),
            "duration_days": duration_days,
        },
        sample_size=sample_size,
        insufficient_sample_size=insufficient,
        missing_metrics=missing,
        unavailable_metrics=unavailable,
        data_quality_warnings=warnings,
    )
