"""
Ollama Local LLM Provider.
Integrates with local Ollama instances (e.g. Qwen2.5:8B, Llama3) with structured JSON output enforcement.
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


class OllamaProvider(BaseLLMProvider):
    def __init__(
        self,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        timeout: float = 60.0,
    ):
        self.base_url = (base_url or os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")).rstrip("/")
        self.model = model or os.environ.get("OLLAMA_MODEL", "qwen2.5:8b")
        self.timeout = timeout

    def generate_strategy(
        self,
        prompt: str,
        system_prompt: str,
    ) -> LLMStrategyOutput:
        endpoint = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": 0.2,
            },
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(endpoint, json=payload)
                response.raise_for_status()
                data = response.json()
                response_text = data.get("response", "{}")
                parsed_json = json.loads(response_text)
                return LLMStrategyOutput.model_validate(parsed_json)
        except Exception as e:
            logger.error(f"Ollama generation failed ({e}) for model {self.model}")
            raise RuntimeError(f"Ollama provider failed: {e}") from e
