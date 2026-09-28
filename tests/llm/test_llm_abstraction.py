"""
Tests for Layer 6: Provider-Agnostic LLM Layer.
"""

from __future__ import annotations

import json
from llm.providers.factory import get_llm_provider
from llm.providers.mock_provider import MockLLMProvider
from llm.schemas.llm_output import LLMStrategyOutput


def test_provider_factory_defaults_to_mock():
    provider = get_llm_provider()
    assert isinstance(provider, MockLLMProvider)


def test_mock_llm_generates_valid_schema():
    provider = MockLLMProvider()
    prompt = (
        "GROUNDED CONTEXT:\n"
        '{"platform": "youtube", "objective": "Brand Awareness", '
        '"recalled_hindsight_experiences": []}\n\n'
        "OUTPUT FORMAT REQUIREMENTS:"
    )
    result = provider.generate_strategy(prompt, "System prompt")
    assert isinstance(result, LLMStrategyOutput)
    assert len(result.content_themes) > 0
    assert len(result.recommended_formats) > 0
    assert result.posting_recommendations.frequency_per_week > 0


def test_mock_llm_responds_to_recalled_memory():
    provider = MockLLMProvider()
    memory_lesson = "Short educational debugging tutorials outperform promotional videos by 100%"
    prompt = (
        "GROUNDED CONTEXT:\n"
        + json.dumps({
            "platform": "youtube",
            "objective": "Lead Generation",
            "recalled_hindsight_experiences": [
                {
                    "memory_id": "mem_debug_1",
                    "lesson": memory_lesson,
                    "context": "Tested on 15 shorts",
                }
            ],
        })
        + "\n\nOUTPUT FORMAT REQUIREMENTS:"
    )

    result = provider.generate_strategy(prompt, "System prompt")
    # Verify the memory influenced the output
    assert len(result.recalled_experience_citations) > 0
    citation = result.recalled_experience_citations[0]
    assert citation.memory_id == "mem_debug_1"
    assert memory_lesson in citation.lesson
    assert "Hindsight learning" in result.rationale
