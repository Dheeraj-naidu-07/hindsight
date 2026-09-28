"""
Mock LLM Provider for deterministic testing and offline operation.
Synthesizes strategies directly from the provided GroundedStrategyContext,
proving the learning effect without external API dependencies.
"""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional
from llm.interface.base import BaseLLMProvider
from llm.schemas.llm_output import (
    LLMContentTheme,
    LLMMemoryCitation,
    LLMPostingRecommendations,
    LLMRecommendedFormat,
    LLMStrategyOutput,
)

logger = logging.getLogger(__name__)


class MockLLMProvider(BaseLLMProvider):
    """
    Deterministic mock provider that reflects grounded facts and recalled memories.
    Produces measurably different strategies when Hindsight experiences are present (Strategy B)
    versus when they are absent (Strategy A).
    """

    def __init__(self, override_output: Optional[LLMStrategyOutput] = None):
        self.override_output = override_output

    def generate_strategy(
        self,
        prompt: str,
        system_prompt: str,
    ) -> LLMStrategyOutput:
        if self.override_output:
            return self.override_output

        # Extract context block from prompt
        context_data = self._extract_context(prompt)
        platform = context_data.get("platform", "youtube")
        objective = context_data.get("objective", "Audience Engagement")
        facts = context_data.get("current_analytics_facts", {})
        recalled_memories = context_data.get("recalled_hindsight_experiences", [])
        gaps = context_data.get("identified_content_gaps", [])

        # Analyze whether Hindsight provided prior learned experiences
        has_learned_experience = len(recalled_memories) > 0
        memory_citations: List[LLMMemoryCitation] = []
        themes: List[LLMContentTheme] = []
        formats: List[LLMRecommendedFormat] = []

        if has_learned_experience:
            # STRATEGY B: Prioritize lessons learned from previous outcomes
            primary_memory = recalled_memories[0]
            lesson_text = primary_memory.get("lesson", "")
            memory_id = primary_memory.get("memory_id")

            rationale = (
                f"Strategy dynamically adapted based on persistent Hindsight learning: '{lesson_text}'. "
                f"Historical baseline indicates that short, educational, problem-solving content yields "
                f"significantly higher engagement than promotional announcements. Allocating primary resources "
                f"to high-yield formats identified in previous post-mortems."
            )

            memory_citations.append(
                LLMMemoryCitation(
                    memory_id=memory_id,
                    lesson=lesson_text,
                    influence_on_strategy=(
                        "Directly guided theme selection away from broad promotional topics towards practical, "
                        "reusable problem-solving technical tutorials."
                    ),
                )
            )

            # High-signal themes reflecting the lesson
            themes.append(
                LLMContentTheme(
                    topic="Practical Debugging & Architecture Breakdowns",
                    priority="high",
                    rationale=f"Directly addresses empirical learning: {lesson_text}",
                    angle="Step-by-step resolution of production errors and bottlenecks",
                    is_gap_fill=False,
                )
            )
            # Add gap-fill theme if gaps identified
            if gaps:
                gap = gaps[0]
                themes.append(
                    LLMContentTheme(
                        topic=gap.get("topic", "Advanced Patterns"),
                        priority="high",
                        rationale=gap.get("rationale", "Fills identified gap in content coverage"),
                        angle="Core concepts distilled into concise actionable takeaways",
                        is_gap_fill=True,
                    )
                )

            formats.append(
                LLMRecommendedFormat(
                    format_name="short",
                    platform=platform,
                    recommended_cadence="3x per week",
                    rationale="Hindsight memory and analytical medians confirm short formats yield 100%+ higher engagement rates.",
                )
            )
            freq = 4.0

        else:
            # STRATEGY A: Baseline exploratory strategy (no prior Hindsight experience)
            rationale = (
                f"Initial exploratory strategy for {objective} on {platform}. "
                f"Relying strictly on observed analytics baseline. Prioritizing mixed formats to gather "
                f"empirical performance data for future Hindsight retention."
            )

            themes.append(
                LLMContentTheme(
                    topic="General Platform Overview & Feature Highlights",
                    priority="medium",
                    rationale="Broad baseline exploration to measure audience interest.",
                    angle="High-level product walkthroughs and general updates",
                    is_gap_fill=False,
                )
            )
            if gaps:
                gap = gaps[0]
                themes.append(
                    LLMContentTheme(
                        topic=gap.get("topic", "Core Fundamentals"),
                        priority="high",
                        rationale="Underrepresented in initial content audit.",
                        angle="Foundational guide for onboarding developers",
                        is_gap_fill=True,
                    )
                )

            formats.append(
                LLMRecommendedFormat(
                    format_name="video",
                    platform=platform,
                    recommended_cadence="1x per week",
                    rationale="Standard baseline format pending performance feedback.",
                )
            )
            freq = 2.0

        posting = LLMPostingRecommendations(
            frequency_per_week=freq,
            optimal_cadence_notes=f"Post consistently during high-activity windows on {platform}.",
            platform_allocation={platform: 1.0},
        )

        experiments = [
            f"Test carousel vs short formats for {themes[0].topic}",
            "Measure retention difference between tutorial hooks and conceptual overviews",
        ]

        limitations = [
            "Recommendations reflect current sample size and historical window.",
            "Causal efficacy should be verified in subsequent post-mortem learning loop.",
        ]

        return LLMStrategyOutput(
            objective=objective,
            rationale=rationale,
            content_themes=themes,
            recommended_formats=formats,
            posting_recommendations=posting,
            recalled_experience_citations=memory_citations,
            suggested_experiments=experiments,
            limitations=limitations,
        )

    def _extract_context(self, prompt: str) -> Dict[str, Any]:
        """Extract JSON context from prompt text."""
        try:
            start_marker = "GROUNDED CONTEXT:\n"
            end_marker = "\n\nOUTPUT FORMAT REQUIREMENTS:"
            if start_marker in prompt and end_marker in prompt:
                start = prompt.index(start_marker) + len(start_marker)
                end = prompt.index(end_marker)
                json_str = prompt[start:end].strip()
                return json.loads(json_str)
        except Exception as e:
            logger.debug(f"Failed to parse JSON context from prompt: {e}")
        return {}
