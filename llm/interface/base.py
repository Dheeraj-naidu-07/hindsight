"""
Provider-Agnostic LLM Interface.
Decouples agent orchestration from specific model providers.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict
from llm.schemas.llm_output import LLMStrategyOutput


class BaseLLMProvider(ABC):
    """Abstract interface for LLM strategy generation."""

    @abstractmethod
    def generate_strategy(
        self,
        prompt: str,
        system_prompt: str,
    ) -> LLMStrategyOutput:
        """
        Generate and validate structured strategy output.
        Must raise an exception or handle fallback if output cannot be validated.
        """
        pass
