"""
OpenAI-Compatible Generic LLM Provider.
Supports OpenAI, Gemini via OpenAI endpoint, vLLM, OpenRouter, and Groq.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Optional
import httpx
from llm.interface.base import BaseLLMProvider
from llm.schemas.llm_output import LLMStrategyOutput

logger = logging.getLogger(__name__)


class OpenAICompatibleProvider(BaseLLMProvider):
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        self.base_url = (base_url or os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")).rstrip("/")
        self.model = model or os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
        self.timeout = timeout

    def generate_strategy(
        self,
        prompt: str,
        system_prompt: str,
    ) -> LLMStrategyOutput:
        endpoint = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2,
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(endpoint, headers=headers, json=payload)
                response.raise_for_status()
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                parsed = json.loads(content)
                return LLMStrategyOutput.model_validate(parsed)
        except Exception as e:
            logger.error(f"OpenAI-compatible generation failed: {e}")
            raise RuntimeError(f"OpenAI-compatible LLM error: {e}") from e
