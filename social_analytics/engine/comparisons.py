"""
Comparison logic for time periods, content formats, and thematic topics.
Strictly distinguishes percentage-point change (pp) from relative percentage change (%).
Applies non-causal analytical comparisons.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Dict, List, Optional, Tuple

from social_analytics.engine.baselines import BaselineMetrics, compare_item_to_baseline
from social_analytics.engine.metrics import (
    calculate_engagement_rate,
    calculate_item_engagements,
    resolve_rate_denominator,
    safe_median,
)
from social_analytics.models.normalized import NormalizedContent
from social_analytics.models.output import (
    ContentPerformanceItem,
    ContentTypePerformance,
    MetricChange,
    PeriodComparison,
    PeriodInfo,
)


def calculate_metric_change(
    current: Optional[float],
    previous: Optional[float],
    is_rate_metric: bool = False,
) -> Optional[MetricChange]:
    """
    Computes delta between current and previous values.
    For rate metrics (e.g. engagement rate %):
      - percentage_points_change = current - previous (in pp)
      - relative_change_percent = ((current - previous) / previous) * 100 (in %)
    For volume metrics (e.g. views, engagements):
      - absolute_change = current - previous
      - relative_change_percent = ((current - previous) / previous) * 100
      - percentage_points_change = None
    """
    if current is None or previous is None:
        return MetricChange(
            current_value=current,
            previous_value=previous,
            absolute_change=None,
            percentage_points_change=None,
            relative_change_percent=None,
        )

    abs_diff = round(current - previous, 4)
    rel_pct: Optional[float] = None
    if previous != 0:
        rel_pct = round(((current - previous) / abs(previous)) * 100.0, 2)

    pp_change: Optional[float] = None
    if is_rate_metric:
        pp_change = round(current - previous, 4)

    return MetricChange(
        current_value=round(current, 4),
        previous_value=round(previous, 4),
        absolute_change=abs_diff,
        percentage_points_change=pp_change,
        relative_change_percent=rel_pct,
    )


def compare_periods(
    current_metrics: Dict[str, Optional[float]],
    previous_metrics: Dict[str, Optional[float]],
    previous_period_info: Optional[PeriodInfo] = None,
) -> PeriodComparison:
    """
    Constructs a comprehensive comparison between Current Period and Previous Period.
    """
    if not previous_metrics:
        return PeriodComparison(
            has_previous_period=False,
            previous_period=None,
            views_change=None,
            engagement_change=None,
            engagement_rate_change=None,
            follower_change=None,
            posting_frequency_change=None,
            median_performance_change={},
        )

    views_change = calculate_metric_change(
        current_metrics.get("total_views"),
        previous_metrics.get("total_views"),
        is_rate_metric=False,
    )
    engagement_change = calculate_metric_change(
        current_metrics.get("total_engagements"),
        previous_metrics.get("total_engagements"),
        is_rate_metric=False,
    )
    engagement_rate_change = calculate_metric_change(
        current_metrics.get("median_engagement_rate"),
        previous_metrics.get("median_engagement_rate"),
        is_rate_metric=True,
    )
    follower_change = calculate_metric_change(
        current_metrics.get("follower_growth"),
        previous_metrics.get("follower_growth"),
        is_rate_metric=False,
    )
    posting_frequency_change = calculate_metric_change(
        current_metrics.get("posting_frequency_per_week"),
        previous_metrics.get("posting_frequency_per_week"),
        is_rate_metric=False,
    )

    median_changes: Dict[str, Optional[MetricChange]] = {
        "median_views": calculate_metric_change(
            current_metrics.get("median_views"),
            previous_metrics.get("median_views"),
            is_rate_metric=False,
        ),
        "median_engagements": calculate_metric_change(
            current_metrics.get("median_engagements"),
            previous_metrics.get("median_engagements"),
            is_rate_metric=False,
        ),
        "median_engagement_rate": calculate_metric_change(
            current_metrics.get("median_engagement_rate"),
            previous_metrics.get("median_engagement_rate"),
            is_rate_metric=True,
        ),
    }

    return PeriodComparison(
        has_previous_period=True,
        previous_period=previous_period_info,
        views_change=views_change,
        engagement_change=engagement_change,
        engagement_rate_change=engagement_rate_change,
        follower_change=follower_change,
        posting_frequency_change=posting_frequency_change,
        median_performance_change=median_changes,
    )


def rank_content_items(
    items: List[NormalizedContent],
    baseline: BaselineMetrics,
    limit: int = 5,
) -> Tuple[List[ContentPerformanceItem], List[ContentPerformanceItem]]:
    """
    Ranks content items into top-performing and bottom-performing lists.
    Primary ranking metric: engagement_rate (if available) or total engagements.
    """
    if not items:
        return [], []

    scored_items: List[Tuple[float, ContentPerformanceItem]] = []
    for item in items:
        eng = calculate_item_engagements(item)
        denom, basis = resolve_rate_denominator(item)
        rate = calculate_engagement_rate(eng, denom) if denom else None

        # Sort key: use engagement_rate if available, otherwise total engagements
        sort_key = rate if rate is not None else float(eng)

        baseline_comp = compare_item_to_baseline(
            item, baseline, preferred_metric="engagement_rate" if rate is not None else "engagements"
        )

        perf_item = ContentPerformanceItem(
            content_id=item.content_id,
            title=item.title,
            content_type=item.content_type,
            published_at=item.published_at.isoformat(),
            views=item.views,
            likes=item.likes,
            comments=item.comments,
            shares=item.shares,
            saves=item.saves,
            total_engagements=eng,
            engagement_rate=rate,
            engagement_rate_basis=basis,
            baseline_comparison=baseline_comp,
        )
        scored_items.append((sort_key, perf_item))

    scored_items.sort(key=lambda x: x[0], reverse=True)
    top_content = [item for _, item in scored_items[:limit]]
    bottom_content = [item for _, item in reversed(scored_items[-limit:])]

    return top_content, bottom_content


def analyze_content_type_performance(
    items: List[NormalizedContent],
) -> Dict[str, ContentTypePerformance]:
    """
    Computes performance aggregated by content format/type (e.g. video, short, reel, post, carousel).
    """
    if not items:
        return {}

    total_count = len(items)
    grouped: Dict[str, List[NormalizedContent]] = defaultdict(list)
    for item in items:
        grouped[item.content_type].append(item)

    results: Dict[str, ContentTypePerformance] = {}
    for ctype, citems in grouped.items():
        views_list = [float(it.views) for it in citems if it.views is not None]
        eng_list = [float(calculate_item_engagements(it)) for it in citems]

        rates_list: List[float] = []
        bases_set = set()
        for it in citems:
            denom, basis = resolve_rate_denominator(it)
            if denom and denom > 0:
                r = calculate_engagement_rate(calculate_item_engagements(it), denom)
                if r is not None:
                    rates_list.append(r)
                if basis:
                    bases_set.add(basis)

        dominant_basis = list(bases_set)[0] if len(bases_set) == 1 else (", ".join(bases_set) if bases_set else None)

        results[ctype] = ContentTypePerformance(
            count=len(citems),
            median_views=safe_median(views_list),
            median_engagements=safe_median(eng_list) or 0.0,
            median_engagement_rate=safe_median(rates_list),
            engagement_rate_basis=dominant_basis,
            share_of_total_content_pct=round((len(citems) / total_count) * 100.0, 2),
        )

    return results


def analyze_topic_performance(
    items: List[NormalizedContent],
) -> Dict[str, Dict[str, Any]]:
    """
    Aggregates performance by topic/category when available.
    """
    grouped: Dict[str, List[NormalizedContent]] = defaultdict(list)
    for item in items:
        if item.topic:
            grouped[item.topic].append(item)

    topic_perf: Dict[str, Dict[str, Any]] = {}
    for topic, titems in grouped.items():
        views_list = [float(it.views) for it in titems if it.views is not None]
        eng_list = [float(calculate_item_engagements(it)) for it in titems]
        rates_list = []
        for it in titems:
            denom, _ = resolve_rate_denominator(it)
            if denom and denom > 0:
                r = calculate_engagement_rate(calculate_item_engagements(it), denom)
                if r is not None:
                    rates_list.append(r)

        topic_perf[topic] = {
            "count": len(titems),
            "median_views": safe_median(views_list),
            "median_engagements": safe_median(eng_list) or 0.0,
            "median_engagement_rate": safe_median(rates_list),
        }
    return topic_perf
