"""
Outcome Analyzer.
Compares actual post-execution performance from AnalyticsResult against
the previous strategy recommendations and historical baselines.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple
from database.models import StrategyRecord
from models.outcome import OutcomeComparison
from models.strategy import ContentStrategy
from social_analytics.models.output import AnalyticsResult

logger = logging.getLogger(__name__)


class OutcomeAnalyzer:
    """Analyzes differences between planned strategy recommendations and actual subsequent performance."""

    @staticmethod
    def analyze(
        strategy: StrategyRecord | ContentStrategy,
        new_analytics: AnalyticsResult,
    ) -> Tuple[List[OutcomeComparison], str]:
        """
        Compare actual metrics against the strategy expectations and account baselines.
        Returns detailed metric comparisons and a factual synthesis summary.
        """
        comparisons: List[OutcomeComparison] = []
        differences: List[str] = []

        baseline_er = new_analytics.baseline.median_engagement_rate
        actual_median_er = new_analytics.content_summary.median_engagement_rate

        # 1. Overall Account Engagement Rate vs Baseline
        if baseline_er is not None and actual_median_er is not None:
            rel_diff = ((actual_median_er - baseline_er) / baseline_er) * 100.0 if baseline_er > 0 else 0.0
            direction = "above_baseline" if rel_diff > 0 else "below_baseline"
            obs = f"Account median ER was {actual_median_er:.2f}% vs historical baseline {baseline_er:.2f}% ({rel_diff:+.1f}%)."
            comparisons.append(
                OutcomeComparison(
                    metric="median_engagement_rate",
                    expected_direction="above_baseline",
                    actual_value=actual_median_er,
                    historical_baseline_value=baseline_er,
                    relative_difference_percent=round(rel_diff, 1),
                    observation=obs,
                )
            )
            differences.append(obs)

        # 2. Content Type / Format Performance Breakdown
        recommended_format_names = []
        if isinstance(strategy, ContentStrategy):
            recommended_format_names = [f.format_name.lower() for f in strategy.recommended_formats]
        else:
            recommended_format_names = [f.get("format_name", "").lower() for f in strategy.recommended_formats]

        for fmt, perf in new_analytics.content_type_performance.items():
            fmt_lower = fmt.lower()
            is_recommended = fmt_lower in recommended_format_names
            fmt_er = perf.median_engagement_rate
            if fmt_er is not None and baseline_er is not None:
                fmt_diff = ((fmt_er - baseline_er) / baseline_er) * 100.0 if baseline_er > 0 else 0.0
                fmt_obs = (
                    f"Format '{fmt}' (recommended: {is_recommended}) achieved median ER of {fmt_er:.2f}% "
                    f"({fmt_diff:+.1f}% relative to account baseline)."
                )
                comparisons.append(
                    OutcomeComparison(
                        metric=f"format_{fmt}_engagement_rate",
                        expected_direction="higher" if is_recommended else "neutral",
                        actual_value=fmt_er,
                        historical_baseline_value=baseline_er,
                        relative_difference_percent=round(fmt_diff, 1),
                        observation=fmt_obs,
                    )
                )
                if is_recommended or abs(fmt_diff) > 20.0:
                    differences.append(fmt_obs)

        # 3. Top Performing Content Alignment
        if new_analytics.top_content:
            top_item = new_analytics.top_content[0]
            top_obs = (
                f"Top performing content was '{top_item.title or top_item.content_id}' ({top_item.content_type}) "
                f"with {top_item.total_engagements} total engagements."
            )
            differences.append(top_obs)

        observed_difference_summary = " ".join(differences)
        return comparisons, observed_difference_summary
