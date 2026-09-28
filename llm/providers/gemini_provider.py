"""
Google Gemini LLM Provider.
Integrates with Google Gemini API via official endpoint.
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


class GeminiProvider(BaseLLMProvider):
    """Provider for Google Gemini models via Gemini OpenAI-compatible API."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.api_key = api_key or os.environ.get("GEMINI_API_KEY", "")
        self.model = model or os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
        self.base_url = (
            base_url
            or os.environ.get(
                "GEMINI_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai",
            )
        ).rstrip("/")
        self.timeout = timeout

    def generate_strategy(
        self,
        prompt: str,
        system_prompt: str,
    ) -> LLMStrategyOutput:
        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not configured. Please supply an API key in the request or set GEMINI_API_KEY in .env"
            )

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
            logger.error(f"Gemini API generation failed: {e}")
            raise RuntimeError(f"Gemini LLM error: {e}") from e
