"""
Strategy Output Validator.
Ensures that the LLM response is factually grounded, properly structured,
and does not cite non-existent Hindsight memories.
"""

from __future__ import annotations

import logging
from typing import List, Set
from agent.context.grounded_context import GroundedStrategyContext
from llm.schemas.llm_output import LLMStrategyOutput

logger = logging.getLogger(__name__)


class StrategyValidationError(Exception):
    """Raised when generated strategy violates grounding or contract rules."""
    pass


class StrategyValidator:
    """Validates LLM-generated strategies against the provided grounded context."""

    @staticmethod
    def validate(
        output: LLMStrategyOutput,
        context: GroundedStrategyContext,
    ) -> List[str]:
        """
        Validates structure and grounding.
        Returns a list of warnings, or raises StrategyValidationError on critical failure.
        """
        warnings: List[str] = []

        # 1. Non-empty themes and formats
        if not output.content_themes:
            raise StrategyValidationError("Generated strategy must contain at least one content theme.")
        if not output.recommended_formats:
            raise StrategyValidationError("Generated strategy must contain at least one recommended format.")

        # 2. Check memory citations against actual recalled memories
        actual_memory_ids: Set[str] = {m.id for m in context.recalled_experiences}
        for citation in output.recalled_experience_citations:
            if citation.memory_id and citation.memory_id not in actual_memory_ids:
                warnings.append(
                    f"Citation referenced memory_id '{citation.memory_id}' which was not in recalled context."
                )

        # 3. Check format alignment with platform
        for fmt in output.recommended_formats:
            if fmt.platform.lower() != context.target_platform.lower():
                warnings.append(
                    f"Format '{fmt.format_name}' targets platform '{fmt.platform}', differing from target '{context.target_platform}'."
                )

        # 4. Posting frequency sanity check
        if output.posting_recommendations.frequency_per_week <= 0:
            raise StrategyValidationError("Posting frequency must be greater than 0.")

        return warnings
