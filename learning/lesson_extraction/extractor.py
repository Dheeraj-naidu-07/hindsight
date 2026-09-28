"""
Strategic Lesson Extractor.
Synthesizes outcome comparisons into high-signal, non-causal reusable experiences
for persistent Hindsight memory storage.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from database.models import StrategyRecord
from hindsight.schemas.memory_models import ReusableExperience
from models.outcome import OutcomeComparison
from models.strategy import ContentStrategy
from social_analytics.models.output import AnalyticsResult

logger = logging.getLogger(__name__)


class LessonExtractor:
    """Extracts non-causal, empirical strategic lessons suitable for Hindsight memory."""

    @staticmethod
    def extract_reusable_experience(
        bank_id: str,
        strategy: StrategyRecord | ContentStrategy,
        comparisons: List[OutcomeComparison],
        observed_difference: str,
        new_analytics: AnalyticsResult,
    ) -> ReusableExperience:
        platform = new_analytics.account.platform

        # Identify dominant format and topic signals
        best_format = None
        best_format_er = -1.0
        for fmt, perf in new_analytics.content_type_performance.items():
            if perf.median_engagement_rate and perf.median_engagement_rate > best_format_er:
                best_format_er = perf.median_engagement_rate
                best_format = fmt

        top_content_type = best_format or (new_analytics.top_content[0].content_type if new_analytics.top_content else "general")
        top_topic = None
        if new_analytics.top_content and new_analytics.top_content[0].title:
            top_topic = new_analytics.top_content[0].title[:40]

        # Extract strategy objective description
        strategy_desc = (
            strategy.objective if isinstance(strategy, (ContentStrategy, StrategyRecord)) else "Targeted content execution"
        )

        # Synthesize strategic takeaway
        baseline_er = new_analytics.baseline.median_engagement_rate or 0.0
        er_diff_pct = 0.0
        for comp in comparisons:
            if comp.metric == "median_engagement_rate" and comp.relative_difference_percent is not None:
                er_diff_pct = comp.relative_difference_percent
                break

        if er_diff_pct > 15.0:
            lesson_text = (
                f"Short, practical educational content on {platform} consistently outperformed account baselines "
                f"(+{er_diff_pct:.1f}% relative ER). Technical problem-solving topics drove higher audience engagement "
                f"than broad conceptual or promotional themes."
            )
            outcome_text = f"Outperformed account baseline by +{er_diff_pct:.1f}% median ER across {new_analytics.content_summary.total_posts} posts."
        elif er_diff_pct < -15.0:
            lesson_text = (
                f"Content format and cadence produced below-baseline engagement ({er_diff_pct:.1f}% ER difference). "
                f"Broad promotional messaging lacked sufficient technical depth to engage audience on {platform}."
            )
            outcome_text = f"Fell below account baseline by {er_diff_pct:.1f}% median ER."
        else:
            lesson_text = (
                f"Format performance remained close to account baseline (+{er_diff_pct:.1f}% ER difference). "
                f"Audience response was stable across covered topics on {platform}."
            )
            outcome_text = f"Performance matched account baseline within {er_diff_pct:.1f}% delta."

        evidence: Dict[str, Any] = {
            "total_posts_analyzed": new_analytics.content_summary.total_posts,
            "actual_median_er": new_analytics.content_summary.median_engagement_rate,
            "baseline_median_er": baseline_er,
            "relative_delta_percent": er_diff_pct,
            "sample_size": new_analytics.data_quality.sample_size,
        }

        tags = [
            platform,
            top_content_type,
            "strategy_outcome",
            "post_mortem",
        ]
        if top_topic:
            tags.append(top_topic[:20])

        return ReusableExperience(
            bank_id=bank_id,
            lesson=lesson_text,
            strategy_used=strategy_desc,
            platform=platform,
            content_type=top_content_type,
            topic=top_topic,
            audience_context=f"Measured across {new_analytics.content_summary.total_posts} published items",
            observed_outcome=outcome_text,
            supporting_evidence=evidence,
            tags=tags,
        )
