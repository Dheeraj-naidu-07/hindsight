"""
LLM Provider Factory.
Instantiates provider based on environment configuration.
"""

from __future__ import annotations

import os
from typing import Optional
from llm.interface.base import BaseLLMProvider
from llm.providers.gemini_provider import GeminiProvider
from llm.providers.mock_provider import MockLLMProvider
from llm.providers.ollama_provider import OllamaProvider
from llm.providers.openai_provider import OpenAICompatibleProvider


def get_llm_provider(
    provider_type: Optional[str] = None,
    api_key: Optional[str] = None,
) -> BaseLLMProvider:
    resolved_type = (provider_type or os.environ.get("LLM_PROVIDER", "")).lower()

    gemini_key = api_key or os.environ.get("GEMINI_API_KEY", "").strip()
    openai_key = api_key or os.environ.get("OPENAI_API_KEY", "").strip()

    if resolved_type == "gemini":
        if gemini_key:
            return GeminiProvider(api_key=gemini_key)
        return MockLLMProvider()
    elif resolved_type == "ollama":
        return OllamaProvider()
    elif resolved_type in ("openai", "generic"):
        if openai_key:
            return OpenAICompatibleProvider(api_key=openai_key)
        return MockLLMProvider()
    elif resolved_type == "mock":
        return MockLLMProvider()

    # Automatic selection based on available API key
    if gemini_key:
        return GeminiProvider(api_key=gemini_key)
    elif openai_key:
        return OpenAICompatibleProvider(api_key=openai_key)
    else:
        return MockLLMProvider()
