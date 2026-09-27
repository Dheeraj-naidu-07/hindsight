"""
Main Social Media Analytics Engine orchestrator.
Coordinates:
Platform Data -> Normalization -> Deterministic Analytics -> Baselines -> Observations -> Final Structured Output.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from social_analytics.engine.baselines import (
    compute_account_baseline,
)
from social_analytics.engine.comparisons import (
    analyze_content_type_performance,
    analyze_topic_performance,
    compare_periods,
    rank_content_items,
)
from social_analytics.engine.metrics import (
    calculate_component_rate,
    calculate_engagement_rate,
    calculate_follower_growth,
    calculate_item_engagements,
    calculate_posting_frequency,
    calculate_view_rate,
    resolve_rate_denominator,
    safe_mean,
    safe_median,
)
from social_analytics.engine.observations import compile_all_observations
from social_analytics.engine.quality import assess_data_quality
from social_analytics.models.normalized import NormalizedContent
from social_analytics.models.output import (
    AccountSummary,
    AnalyticsResult,
    ContentSummary,
    GrowthSummary,
    PeriodInfo,
)
from social_analytics.providers.base import BaseSocialProvider

logger = logging.getLogger(__name__)


class SocialMediaAnalyticsEngine:
    """
    Independent, deterministic social media analytics engine.
    Produces high-fidelity, validated analytical models and structured JSON.
    """

    def __init__(self, provider: BaseSocialProvider):
        self.provider = provider

    def run_analysis(
        self,
        account_id: str,
        start_date: datetime,
        end_date: datetime,
        previous_period_start: Optional[datetime] = None,
        previous_period_end: Optional[datetime] = None,
        historical_baseline_items: Optional[List[NormalizedContent]] = None,
        content_items: Optional[List[NormalizedContent]] = None,
        limit: int = 100,
    ) -> AnalyticsResult:
        """
        Executes end-to-end analytical pipeline for an account and date window.
        """
        platform = self.provider.platform_name()
        duration_days = max(
            0.1, (end_date - start_date).total_seconds() / 86400.0
        )

        # 1. Account profile snapshot
        account_info = self.provider.get_account(account_id)

        # 2. Retrieve content items (allow caller to supply pre-fetched items for testing)
        if content_items is None:
            current_items = self.provider.get_content(
                account_id=account_id,
                start_date=start_date,
                end_date=end_date,
                limit=limit,
            )
        else:
            current_items = content_items

        # 3. Audience metrics
        audience = self.provider.get_audience_metrics(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
        )

        # 4. Previous period (if configured)
        previous_items: List[NormalizedContent] = []
        previous_period_info: Optional[PeriodInfo] = None
        if previous_period_start and previous_period_end:
            prev_days = max(
                0.1,
                (previous_period_end - previous_period_start).total_seconds()
                / 86400.0,
            )
            previous_period_info = PeriodInfo(
                start_date=previous_period_start.isoformat(),
                end_date=previous_period_end.isoformat(),
                days=round(prev_days, 2),
            )
            previous_items = self.provider.get_content(
                account_id=account_id,
                start_date=previous_period_start,
                end_date=previous_period_end,
                limit=limit,
            )

        # 5. Account Baselines (historical items > previous items > current items)
        baseline_corpus = (
            historical_baseline_items
            if historical_baseline_items is not None
            else (previous_items if previous_items else current_items)
        )
        baseline = compute_account_baseline(baseline_corpus)

        # 6. Current Content Summary calculations
        total_posts = len(current_items)
        posts_by_type: Dict[str, int] = {}
        for it in current_items:
            posts_by_type[it.content_type] = posts_by_type.get(it.content_type, 0) + 1

        total_views: Optional[int] = None
        valid_views = [it.views for it in current_items if it.views is not None]
        if valid_views:
            total_views = sum(valid_views)

        item_engagements = [calculate_item_engagements(it) for it in current_items]
        total_engagements = sum(item_engagements)

        avg_eng = (
            round(total_engagements / total_posts, 2) if total_posts > 0 else 0.0
        )
        median_views = (
            safe_median([float(v) for v in valid_views]) if valid_views else None
        )
        median_eng = (
            safe_median([float(e) for e in item_engagements])
            if item_engagements
            else 0.0
        )

        # Determine dominant rate denominator basis across items
        rates: List[float] = []
        like_rates: List[float] = []
        comment_rates: List[float] = []
        share_rates: List[float] = []
        save_rates: List[float] = []
        view_rates: List[float] = []
        bases_encountered = set()

        for it in current_items:
            denom, basis = resolve_rate_denominator(it)
            if denom and denom > 0:
                eng = calculate_item_engagements(it)
                r = calculate_engagement_rate(eng, denom)
                if r is not None:
                    rates.append(r)
                if basis:
                    bases_encountered.add(basis)

                lr = calculate_component_rate(it.likes, denom)
                if lr is not None:
                    like_rates.append(lr)

                cr = calculate_component_rate(it.comments, denom)
                if cr is not None:
                    comment_rates.append(cr)

                sr = calculate_component_rate(it.shares, denom)
                if sr is not None:
                    share_rates.append(sr)

                svr = calculate_component_rate(it.saves, denom)
                if svr is not None:
                    save_rates.append(svr)

            vr = calculate_view_rate(it.views, it.impressions)
            if vr is not None:
                view_rates.append(vr)

        median_rate = safe_median(rates)
        dominant_basis = (
            list(bases_encountered)[0]
            if len(bases_encountered) == 1
            else (", ".join(bases_encountered) if bases_encountered else None)
        )

        posts_per_day, posts_per_week = calculate_posting_frequency(
            total_posts, duration_days
        )

        content_summary = ContentSummary(
            total_posts=total_posts,
            posts_by_type=posts_by_type,
            total_views=total_views,
            total_engagements=total_engagements,
            average_engagement_per_content=avg_eng,
            median_views=median_views,
            median_engagements=median_eng or 0.0,
            median_engagement_rate=median_rate,
            engagement_rate_basis=dominant_basis,
            like_rate=safe_mean(like_rates),
            comment_rate=safe_mean(comment_rates),
            share_rate=safe_mean(share_rates),
            save_rate=safe_mean(save_rates),
            view_rate=safe_mean(view_rates),
            posting_frequency_per_day=posts_per_day,
            posting_frequency_per_week=posts_per_week,
        )

        # 7. Growth Summary
        abs_growth, pct_growth = calculate_follower_growth(
            audience.followers_start, audience.followers_end
        )
        growth_summary = GrowthSummary(
            followers_start=audience.followers_start,
            followers_end=audience.followers_end,
            absolute_follower_growth=abs_growth,
            percentage_follower_growth=pct_growth,
        )

        # 8. Content Rankings (Top & Bottom)
        top_content, bottom_content = rank_content_items(
            current_items, baseline=baseline, limit=5
        )

        # 9. Format Breakdown
        content_type_perf = analyze_content_type_performance(current_items)

        # 10. Topic Performance
        topic_perf = analyze_topic_performance(current_items)

        # 11. Period Comparison
        current_period_metric_dict: Dict[str, Optional[float]] = {
            "total_views": float(total_views) if total_views is not None else None,
            "total_engagements": float(total_engagements),
            "median_views": median_views,
            "median_engagements": median_eng,
            "median_engagement_rate": median_rate,
            "follower_growth": float(abs_growth) if abs_growth is not None else None,
            "posting_frequency_per_week": posts_per_week,
        }

        previous_period_metric_dict: Dict[str, Optional[float]] = {}
        if previous_items:
            prev_views = [it.views for it in previous_items if it.views is not None]
            prev_engs = [calculate_item_engagements(it) for it in previous_items]
            prev_rates = []
            for it in previous_items:
                d, _ = resolve_rate_denominator(it)
                if d and d > 0:
                    r = calculate_engagement_rate(calculate_item_engagements(it), d)
                    if r is not None:
                        prev_rates.append(r)

            p_days = (
                previous_period_info.days if previous_period_info else duration_days
            )
            _, prev_per_week = calculate_posting_frequency(
                len(previous_items), p_days
            )

            previous_period_metric_dict = {
                "total_views": float(sum(prev_views)) if prev_views else None,
                "total_engagements": float(sum(prev_engs)),
                "median_views": safe_median([float(v) for v in prev_views])
                if prev_views
                else None,
                "median_engagements": safe_median([float(e) for e in prev_engs])
                or 0.0,
                "median_engagement_rate": safe_median(prev_rates),
                "follower_growth": None,
                "posting_frequency_per_week": prev_per_week,
            }

        period_comparison = compare_periods(
            current_metrics=current_period_metric_dict,
            previous_metrics=previous_period_metric_dict,
            previous_period_info=previous_period_info,
        )

        # 12. Deterministic Observations
        observations = compile_all_observations(
            content_types=content_type_perf,
            period_comp=period_comparison,
            topic_perf=topic_perf,
            baseline=baseline,
        )

        # 13. Platform-specific metrics compilation
        platform_metrics: Dict[str, Any] = {}
        if platform == "youtube":
            total_watch_time = sum(
                it.watch_time for it in current_items if it.watch_time is not None
            )
            durations = [
                it.platform_specific.get("duration_seconds", 0)
                for it in current_items
                if it.platform_specific.get("duration_seconds")
            ]
            platform_metrics = {
                "total_watch_time_seconds": round(total_watch_time, 2)
                if total_watch_time
                else None,
                "average_duration_seconds": safe_mean([float(d) for d in durations]),
                "total_impressions": sum(
                    it.impressions for it in current_items if it.impressions is not None
                ),
            }
        elif platform == "instagram":
            total_reach = sum(it.reach for it in current_items if it.reach is not None)
            total_saves = sum(it.saves for it in current_items if it.saves is not None)
            platform_metrics = {
                "total_reach": total_reach if total_reach > 0 else None,
                "total_saves": total_saves if total_saves > 0 else None,
                "total_impressions": sum(
                    it.impressions for it in current_items if it.impressions is not None
                ),
            }
        elif platform == "reddit":
            ratios = [
                float(it.platform_specific["upvote_ratio"])
                for it in current_items
                if "upvote_ratio" in it.platform_specific
            ]
            platform_metrics = {
                "average_upvote_ratio": safe_mean(ratios),
                "total_score": sum(it.likes for it in current_items if it.likes is not None),
                "total_comments": sum(
                    it.comments for it in current_items if it.comments is not None
                ),
            }

        # 14. Data Quality Audit
        data_quality = assess_data_quality(
            platform=platform,  # type: ignore
            items=current_items,
            start_date=start_date,
            end_date=end_date,
        )

        return AnalyticsResult(
            account=AccountSummary(
                platform=platform,  # type: ignore
                account_id=account_info.account_id,
                username=account_info.username,
                display_name=account_info.display_name,
                current_followers=account_info.followers_count,
                total_posts_analyzed=total_posts,
            ),
            period=PeriodInfo(
                start_date=start_date.isoformat(),
                end_date=end_date.isoformat(),
                days=round(duration_days, 2),
            ),
            content_summary=content_summary,
            growth=growth_summary,
            baseline=baseline,
            top_content=top_content,
            bottom_content=bottom_content,
            content_type_performance=content_type_perf,
            period_comparison=period_comparison,
            observations=observations,
            platform_specific_metrics=platform_metrics,
            data_quality=data_quality,
        )
