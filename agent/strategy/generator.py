"""
Strategy Generator.
Coordinates prompt creation, LLM provider invocation, output validation,
and compilation into a domain ContentStrategy object.
"""

from __future__ import annotations

import logging
import uuid
from typing import Optional
from agent.context.grounded_context import GroundedStrategyContext
from agent.strategy.validator import StrategyValidator
from llm.interface.base import BaseLLMProvider
from llm.prompts.strategy_prompts import SYSTEM_STRATEGY_PROMPT, build_user_strategy_prompt
from llm.providers.factory import get_llm_provider
from models.strategy import (
    ContentStrategy,
    ContentTheme,
    PostingRecommendations,
    RecommendedFormat,
    RecalledExperienceCitation,
)

logger = logging.getLogger(__name__)


class StrategyGenerator:
    def __init__(self, llm_provider: Optional[BaseLLMProvider] = None):
        self.llm_provider = llm_provider or get_llm_provider()

    def generate(
        self,
        context: GroundedStrategyContext,
        strategy_id: Optional[str] = None,
    ) -> ContentStrategy:
        strategy_id = strategy_id or f"strat_{uuid.uuid4().hex[:12]}"
        user_prompt = build_user_strategy_prompt(context)

        # Generate structured output from provider
        llm_output = self.llm_provider.generate_strategy(
            prompt=user_prompt,
            system_prompt=SYSTEM_STRATEGY_PROMPT,
        )

        # Validate against grounded context
        warnings = StrategyValidator.validate(llm_output, context)
        all_limitations = list(llm_output.limitations) + warnings + context.limitations

        # Convert to ContentStrategy domain model
        themes = [
            ContentTheme(
                topic=t.topic,
                priority=t.priority,
                rationale=t.rationale,
                angle=t.angle,
                is_gap_fill=t.is_gap_fill,
            )
            for t in llm_output.content_themes
        ]

        formats = [
            RecommendedFormat(
                format_name=f.format_name,
                platform=f.platform,
                recommended_cadence=f.recommended_cadence,
                rationale=f.rationale,
            )
            for f in llm_output.recommended_formats
        ]

        posting = PostingRecommendations(
            frequency_per_week=llm_output.posting_recommendations.frequency_per_week,
            optimal_cadence_notes=llm_output.posting_recommendations.optimal_cadence_notes,
            platform_allocation=llm_output.posting_recommendations.platform_allocation,
        )

        citations = [
            RecalledExperienceCitation(
                memory_id=c.memory_id,
                lesson=c.lesson,
                influence_on_strategy=c.influence_on_strategy,
            )
            for c in llm_output.recalled_experience_citations
        ]

        supporting_analytics = [
            {"observation": obs} for obs in context.current_evidence.key_observations
        ]

        return ContentStrategy(
            strategy_id=strategy_id,
            brand_id=context.brand.brand_id,
            objective=context.objective,
            target_audience=context.brand.target_audience,
            recommended_platforms=[context.target_platform],
            content_themes=themes,
            recommended_formats=formats,
            posting_recommendations=posting,
            rationale=llm_output.rationale,
            supporting_analytics=supporting_analytics,
            recalled_experiences=citations,
            confidence_and_limitations=all_limitations,
            suggested_experiments=llm_output.suggested_experiments,
        )
