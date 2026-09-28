"""
Master Content Strategy Agent Orchestrator.
Coordinates the complete lifecycle:
User Request -> Analytics Engine -> Evidence & Gaps -> Hindsight Recall -> Grounded Context -> LLM Reasoning -> Strategy Validation -> DB Persistence.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Literal, Optional, Tuple

from agent.context.grounded_context import GroundedStrategyContext
from agent.evidence.builder import GroundedContextBuilder
from agent.strategy.generator import StrategyGenerator
from database.connection import get_db
from database.models import BrandRecord, StrategyRecord
from database.repositories.brand_repository import BrandRepository
from database.repositories.content_repository import ContentRepository
from database.repositories.strategy_repository import StrategyRepository
from models.brand import BrandProfile, BrandVoicePreferences
from models.strategy import ContentStrategy
from services.analytics_service.service import AnalyticsService
from social_analytics.models.output import AnalyticsResult

logger = logging.getLogger(__name__)


class ContentStrategyAgentOrchestrator:
    """Master agent orchestrator coordinating analytics, Hindsight memory, LLM, and persistence."""

    def __init__(
        self,
        analytics_service: Optional[AnalyticsService] = None,
        context_builder: Optional[GroundedContextBuilder] = None,
        strategy_generator: Optional[StrategyGenerator] = None,
        brand_repo: Optional[BrandRepository] = None,
        strategy_repo: Optional[StrategyRepository] = None,
        content_repo: Optional[ContentRepository] = None,
    ):
        db = strategy_repo.db if strategy_repo else (brand_repo.db if brand_repo else get_db())
        self.brand_repo = brand_repo or BrandRepository(db)
        self.strategy_repo = strategy_repo or StrategyRepository(db)
        resolved_content_repo = content_repo or ContentRepository(db)
        self.analytics_service = analytics_service or AnalyticsService(content_repo=resolved_content_repo)
        self.context_builder = context_builder or GroundedContextBuilder()
        self.strategy_generator = strategy_generator or StrategyGenerator()

    def execute_strategy_pipeline(
        self,
        brand_id: str,
        platform: Literal["youtube", "instagram", "reddit"],
        account_id: str,
        objective: str = "Maximize audience engagement and authority",
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        analytics_result: Optional[AnalyticsResult] = None,
        custom_brand_profile: Optional[BrandProfile] = None,
        platform_api_key: Optional[str] = None,
        llm_api_key: Optional[str] = None,
    ) -> Tuple[ContentStrategy, AnalyticsResult, GroundedStrategyContext]:
        """
        Execute the full 10-step strategy orchestration pipeline.
        Returns the final generated strategy, the underlying AnalyticsResult, and GroundedStrategyContext.
        """
        logger.info(f"Initiating Strategy Pipeline for brand '{brand_id}' on platform '{platform}'")

        # 1. Resolve Brand Profile
        brand = self._resolve_brand_profile(brand_id, custom_brand_profile)

        # 2. Run Analytics or consume provided AnalyticsResult
        if analytics_result is None:
            now = datetime.now(timezone.utc)
            end = end_date or now
            if end.tzinfo is None:
                end = end.replace(tzinfo=timezone.utc)
            start = start_date or (end - timedelta(days=30))
            if start.tzinfo is None:
                start = start.replace(tzinfo=timezone.utc)
            prev_start = start - timedelta(days=30)
            prev_end = start

            analytics_result = self.analytics_service.run_analytics(
                platform=platform,
                account_id=account_id,
                start_date=start,
                end_date=end,
                previous_period_start=prev_start,
                previous_period_end=prev_end,
                api_key=platform_api_key,
            )

        # 3. Persist content items and performance snapshot in local DB
        try:
            self.analytics_service.persist_analytics_items(
                brand_id=brand.brand_id,
                analytics=analytics_result,
            )
        except Exception as e:
            logger.warning(f"Non-fatal error persisting analytics items to DB: {e}")

        # 4. Build Grounded Context (Evidence + Hindsight Memory Recall)
        grounded_context = self.context_builder.build_context(
            brand=brand,
            objective=objective,
            platform=platform,
            analytics=analytics_result,
            memory_bank_id=brand.brand_id,
        )

        # 5. LLM Reasoning & Strategy Generation (uses custom API key if provided)
        if llm_api_key:
            generator = StrategyGenerator(llm_provider=get_llm_provider(api_key=llm_api_key))
            strategy = generator.generate(context=grounded_context)
        else:
            strategy = self.strategy_generator.generate(context=grounded_context)

        # 6. Database Persistence of Generated Strategy
        self._persist_strategy(strategy)

        logger.info(f"Successfully generated and persisted strategy '{strategy.strategy_id}'")
        return strategy, analytics_result, grounded_context

    def _resolve_brand_profile(
        self,
        brand_id: str,
        custom: Optional[BrandProfile] = None,
    ) -> BrandProfile:
        if custom:
            # Sync to DB
            self.brand_repo.create(
                BrandRecord(
                    id=custom.brand_id,
                    name=custom.name,
                    identity=custom.identity,
                    target_audience=custom.target_audience,
                    voice_tone=custom.voice_preferences.tone,
                    communication_style=custom.voice_preferences.communication_style,
                )
            )
            return custom

        db_brand = self.brand_repo.get_by_id(brand_id)
        if db_brand:
            return BrandProfile(
                brand_id=db_brand.id,
                name=db_brand.name,
                identity=db_brand.identity,
                target_audience=db_brand.target_audience,
                voice_preferences=BrandVoicePreferences(
                    tone=db_brand.voice_tone,
                    communication_style=db_brand.communication_style,
                ),
            )

        # Dynamic brand profile derived from brand_id
        brand_name = brand_id.replace("_", " ").title()
        default_brand = BrandProfile(
            brand_id=brand_id,
            name=brand_name,
            identity=f"Official digital media channel and brand presence for {brand_name}",
            target_audience=f"Core audience, customers, and community for {brand_name}",
            voice_preferences=BrandVoicePreferences(
                tone="Authoritative, authentic, and engaging",
                communication_style="Insightful, high-value, and audience-focused",
                preferred_topics=[],
            ),
        )
        self.brand_repo.create(
            BrandRecord(
                id=default_brand.brand_id,
                name=default_brand.name,
                identity=default_brand.identity,
                target_audience=default_brand.target_audience,
                voice_tone=default_brand.voice_preferences.tone,
                communication_style=default_brand.voice_preferences.communication_style,
            )
        )
        return default_brand

    def _persist_strategy(self, strategy: ContentStrategy) -> None:
        record = StrategyRecord(
            id=strategy.strategy_id,
            brand_id=strategy.brand_id,
            objective=strategy.objective,
            target_audience=strategy.target_audience,
            recommended_platforms_json=json.dumps(strategy.recommended_platforms),
            content_themes_json=json.dumps([t.model_dump() for t in strategy.content_themes]),
            recommended_formats_json=json.dumps([f.model_dump() for f in strategy.recommended_formats]),
            posting_recommendations_json=json.dumps(strategy.posting_recommendations.model_dump()),
            rationale=strategy.rationale,
            supporting_evidence_json=json.dumps(strategy.supporting_analytics),
            recalled_memories_json=json.dumps([m.model_dump() for m in strategy.recalled_experiences]),
            confidence_notes="\n".join(strategy.confidence_and_limitations),
            experiments_json=json.dumps(strategy.suggested_experiments),
            created_at=strategy.created_at,
        )
        self.strategy_repo.create(record)
