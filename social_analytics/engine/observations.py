"""
Deterministic observation generation engine.
Produces factual, quantitative statements with explicit evidence structures.
Avoids speculative advice, marketing recommendations, or causal claims.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from social_analytics.models.output import (
    BaselineMetrics,
    ContentTypePerformance,
    Observation,
    PeriodComparison,
)


def generate_content_type_observations(
    content_types: Dict[str, ContentTypePerformance],
) -> List[Observation]:
    """
    Compares content formats that have sufficient sample size (>= 1 post each).
    Emits factual relative differences in median engagement rate or median engagements.
    """
    observations: List[Observation] = []
    types_list = list(content_types.items())

    # Sort pairs to compare top format against others
    for i in range(len(types_list)):
        for j in range(i + 1, len(types_list)):
            name_a, perf_a = types_list[i]
            name_b, perf_b = types_list[j]

            # Compare by median_engagement_rate if available on both
            rate_a = perf_a.median_engagement_rate
            rate_b = perf_b.median_engagement_rate

            if rate_a is not None and rate_b is not None and rate_b > 0 and rate_a != rate_b:
                if rate_a > rate_b:
                    diff_pct = round(((rate_a - rate_b) / rate_b) * 100.0, 1)
                    higher_name, lower_name = name_a, name_b
                    higher_rate, lower_rate = rate_a, rate_b
                    s_higher, s_lower = perf_a.count, perf_b.count
                else:
                    diff_pct = round(((rate_b - rate_a) / rate_a) * 100.0, 1)
                    higher_name, lower_name = name_b, name_a
                    higher_rate, lower_rate = rate_b, rate_a
                    s_higher, s_lower = perf_b.count, perf_a.count

                observations.append(
                    Observation(
                        type="content_type_comparison",
                        observation=(
                            f"{higher_name.capitalize()} format content had {diff_pct}% higher "
                            f"median engagement rate than {lower_name} format content."
                        ),
                        evidence={
                            "metric": "median_engagement_rate",
                            "higher_format": higher_name,
                            "lower_format": lower_name,
                            "higher_value": higher_rate,
                            "lower_value": lower_rate,
                            "difference_percent": diff_pct,
                            "sample_sizes": {
                                higher_name: s_higher,
                                lower_name: s_lower,
                            },
                        },
                    )
                )

            # Compare by median_engagements if rates are not available
            elif perf_a.median_engagements != perf_b.median_engagements:
                eng_a = perf_a.median_engagements
                eng_b = perf_b.median_engagements
                if eng_a > eng_b and eng_b > 0:
                    diff_pct = round(((eng_a - eng_b) / eng_b) * 100.0, 1)
                    observations.append(
                        Observation(
                            type="content_type_comparison",
                            observation=(
                                f"{name_a.capitalize()} format content had {diff_pct}% higher "
                                f"median total engagements than {name_b} format content."
                            ),
                            evidence={
                                "metric": "median_engagements",
                                "difference_percent": diff_pct,
                                "sample_sizes": {
                                    name_a: perf_a.count,
                                    name_b: perf_b.count,
                                },
                            },
                        )
                    )

    return observations


def generate_period_trend_observations(
    period_comp: PeriodComparison,
) -> List[Observation]:
    """
    Generates observations comparing the current period with the previous period.
    """
    observations: List[Observation] = []
    if not period_comp.has_previous_period:
        return observations

    # Engagement rate change (distinguishing pp from relative %)
    er_change = period_comp.engagement_rate_change
    if er_change and er_change.relative_change_percent is not None:
        rel_change = er_change.relative_change_percent
        pp_change = er_change.percentage_points_change
        direction = "above" if rel_change > 0 else "below"
        abs_rel = abs(rel_change)
        observations.append(
            Observation(
                type="period_trend",
                observation=(
                    f"Current period median engagement rate is {abs_rel}% {direction} "
                    f"the previous period ({'+' if (pp_change or 0) >= 0 else ''}{pp_change} pp)."
                ),
                evidence={
                    "metric": "median_engagement_rate",
                    "current_value": er_change.current_value,
                    "previous_value": er_change.previous_value,
                    "relative_change_percent": rel_change,
                    "percentage_points_change": pp_change,
                },
            )
        )

    # Views change
    v_change = period_comp.views_change
    if v_change and v_change.relative_change_percent is not None:
        direction = "increased" if v_change.relative_change_percent > 0 else "decreased"
        observations.append(
            Observation(
                type="period_trend",
                observation=(
                    f"Total views {direction} by {abs(v_change.relative_change_percent)}% "
                    f"compared to the previous period."
                ),
                evidence={
                    "metric": "total_views",
                    "current_value": v_change.current_value,
                    "previous_value": v_change.previous_value,
                    "relative_change_percent": v_change.relative_change_percent,
                    "absolute_change": v_change.absolute_change,
                },
            )
        )

    return observations


def generate_topic_observations(
    topic_perf: Dict[str, Dict[str, Any]],
    baseline: BaselineMetrics,
) -> List[Observation]:
    """
    Generates observations for topics performing substantially above or below baseline.
    """
    observations: List[Observation] = []
    base_rate = baseline.median_engagement_rate

    for topic, stats in topic_perf.items():
        sample_size = stats.get("count", 0)
        t_rate = stats.get("median_engagement_rate")

        if t_rate is not None and base_rate is not None and base_rate > 0:
            diff_pct = round(((t_rate - base_rate) / base_rate) * 100.0, 1)
            direction = "higher" if diff_pct > 0 else "lower"
            observations.append(
                Observation(
                    type="topic_comparison",
                    observation=(
                        f"Content in topic '{topic}' had a {abs(diff_pct)}% {direction} "
                        f"median engagement rate than the account historical baseline."
                    ),
                    evidence={
                        "topic": topic,
                        "metric": "median_engagement_rate",
                        "topic_median": t_rate,
                        "historical_baseline": base_rate,
                        "difference_percent": diff_pct,
                        "sample_size": sample_size,
                    },
                )
            )
    return observations


def compile_all_observations(
    content_types: Dict[str, ContentTypePerformance],
    period_comp: PeriodComparison,
    topic_perf: Dict[str, Dict[str, Any]],
    baseline: BaselineMetrics,
) -> List[Observation]:
    """
    Aggregates all deterministic observations across dimensions.
    """
    results: List[Observation] = []
    results.extend(generate_content_type_observations(content_types))
    results.extend(generate_period_trend_observations(period_comp))
    results.extend(generate_topic_observations(topic_perf, baseline))
    return results
