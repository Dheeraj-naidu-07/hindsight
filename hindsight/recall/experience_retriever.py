"""
Hindsight Experience Retriever.
Performs bounded, relevance-filtered memory recall across memory banks.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from hindsight.client.hindsight_client_wrapper import HindsightClientWrapper
from hindsight.schemas.memory_models import MemoryRecallQuery, MemoryRecallResult

logger = logging.getLogger(__name__)


class ExperienceRetriever:
    """Retrieves bounded, deduplicated memories from Hindsight."""

    def __init__(self, client: Optional[HindsightClientWrapper] = None):
        self.client = client or HindsightClientWrapper()

    def recall_experiences(
        self,
        query: MemoryRecallQuery,
        max_items: int = 5,
    ) -> List[MemoryRecallResult]:
        """
        Recall up to max_items relevant memories from Hindsight.
        Guarantees bounded token budget and prevents dumping unfiltered banks.
        """
        tags = query.tags or []
        if query.platform and query.platform not in tags:
            tags.append(query.platform)
        if query.content_type and query.content_type not in tags:
            tags.append(query.content_type)
        if query.topic and query.topic not in tags:
            tags.append(query.topic)

        raw_results = self.client.recall(
            bank_id=query.bank_id,
            query=query.query,
            tags=tags if tags else None,
            max_tokens=query.max_tokens,
        )

        results: List[MemoryRecallResult] = []
        seen_texts = set()

        for item in raw_results:
            text = item.get("content", "").strip()
            if not text or text in seen_texts:
                continue
            seen_texts.add(text)

            results.append(
                MemoryRecallResult(
                    id=item.get("id", "mem_unknown"),
                    text=text,
                    type="experience",
                    context=item.get("context"),
                    metadata=item.get("metadata", {}),
                )
            )
            if len(results) >= max_items:
                break

        return results
