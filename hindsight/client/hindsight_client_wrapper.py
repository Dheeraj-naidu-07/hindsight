"""
Hindsight Client Integration Wrapper.
Provides a resilient bridge to the official Hindsight client with fallback capability
for offline testing and development environments.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional
import uuid

logger = logging.getLogger(__name__)

# Try importing the official Hindsight client package
try:
    from hindsight_client import Hindsight as OfficialHindsightClient
    _HAS_OFFICIAL_CLIENT = True
except ImportError:
    _HAS_OFFICIAL_CLIENT = False


class InMemoryMemoryBank:
    """In-memory bank used for offline testing or fallback when Hindsight server is not reachable."""

    def __init__(self):
        # bank_id -> list of memory dicts
        self._banks: Dict[str, List[Dict[str, Any]]] = {}

    def retain(
        self,
        bank_id: str,
        content: str,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        if bank_id not in self._banks:
            self._banks[bank_id] = []

        mem_id = f"mem_{uuid.uuid4().hex[:12]}"
        entry = {
            "id": mem_id,
            "content": content,
            "context": context,
            "metadata": metadata or {},
            "tags": tags or [],
        }
        self._banks[bank_id].append(entry)
        return mem_id

    def recall(
        self,
        bank_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        max_results: int = 5,
    ) -> List[Dict[str, Any]]:
        if bank_id not in self._banks:
            return []

        candidates = self._banks[bank_id]
        if tags:
            tag_set = set(t.lower() for t in tags)
            candidates = [
                c for c in candidates
                if any(t.lower() in tag_set for t in c.get("tags", []))
            ] or candidates

        query_terms = set(query.lower().split())
        scored: List[tuple[int, Dict[str, Any]]] = []
        for c in candidates:
            text = (c["content"] + " " + (c.get("context") or "")).lower()
            overlap = sum(1 for term in query_terms if term in text)
            scored.append((overlap, c))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [item for _, item in scored[:max_results]]


_global_fallback_bank = InMemoryMemoryBank()


def reset_global_fallback_bank() -> None:
    global _global_fallback_bank
    _global_fallback_bank = InMemoryMemoryBank()


class HindsightClientWrapper:
    """
    High-level wrapper around the Hindsight system.
    Connects to the official Hindsight server when available; otherwise transparently
    maintains an isolated in-memory memory bank for deterministic offline operation.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        force_mock: bool = False,
        fallback_bank: Optional[InMemoryMemoryBank] = None,
    ):
        self.base_url = base_url or os.environ.get("HINDSIGHT_API_URL", "http://localhost:8888")
        self.api_key = api_key or os.environ.get("HINDSIGHT_API_KEY")
        self.force_mock = force_mock or os.environ.get("HINDSIGHT_MOCK_MODE", "false").lower() == "true"
        self._official_client: Optional[Any] = None
        self._fallback_bank = fallback_bank or _global_fallback_bank
        self._is_server_available = False

        if not self.force_mock and _HAS_OFFICIAL_CLIENT:
            try:
                self._official_client = OfficialHindsightClient(
                    base_url=self.base_url,
                    api_key=self.api_key,
                    timeout=3.0,
                )
                # Verify connection health
                self._official_client.get_version()
                self._is_server_available = True
                logger.info(f"Connected successfully to Hindsight server at {self.base_url}")
            except Exception as e:
                logger.warning(
                    f"Hindsight server at {self.base_url} is unreachable ({e}). "
                    f"Operating in resilient offline memory mode."
                )
                self._is_server_available = False

    @property
    def is_connected_to_server(self) -> bool:
        return self._is_server_available

    def retain(
        self,
        bank_id: str,
        content: str,
        context: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Store memory in Hindsight bank."""
        if self._is_server_available and self._official_client:
            try:
                resp = self._official_client.retain(
                    bank_id=bank_id,
                    content=content,
                    context=context,
                    metadata=metadata,
                    tags=tags,
                )
                return str(resp)
            except Exception as e:
                logger.warning(f"Error calling live Hindsight retain ({e}); persisting to fallback bank.")

        return self._fallback_bank.retain(
            bank_id=bank_id,
            content=content,
            context=context,
            metadata=metadata,
            tags=tags,
        )

    def recall(
        self,
        bank_id: str,
        query: str,
        tags: Optional[List[str]] = None,
        max_tokens: int = 2048,
    ) -> List[Dict[str, Any]]:
        """Recall relevant memories from Hindsight bank."""
        if self._is_server_available and self._official_client:
            try:
                resp = self._official_client.recall(
                    bank_id=bank_id,
                    query=query,
                    tags=tags,
                    max_tokens=max_tokens,
                )
                results = []
                for r in resp.results:
                    results.append({
                        "id": getattr(r, "id", str(uuid.uuid4())),
                        "content": getattr(r, "text", str(r)),
                        "context": getattr(r, "context", None),
                        "metadata": getattr(r, "metadata", {}),
                    })
                return results
            except Exception as e:
                logger.warning(f"Error calling live Hindsight recall ({e}); reading from fallback bank.")

        return self._fallback_bank.recall(
            bank_id=bank_id,
            query=query,
            tags=tags,
        )
