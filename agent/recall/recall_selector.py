"""
Recall Selector for Hindsight memory queries.
Constructs targeted, bounded search queries based on platform and topics,
preventing unbounded memory dumping into LLM prompts.
"""

from __future__ import annotations

import logging
from typing import List, Optional
from hindsight.recall.experience_retriever import ExperienceRetriever
from hindsight.schemas.memory_models import MemoryRecallQuery, MemoryRecallResult
from services.analytics_service.evidence_extractor import FormattedEvidence

logger = logging.getLogger(__name__)


class RecallSelector:
    """Orchestrates bounded, high-relevance recall queries to Hindsight."""

    def __init__(self, retriever: Optional[ExperienceRetriever] = None):
        self.retriever = retriever or ExperienceRetriever()

    def select_relevant_memories(
        self,
        bank_id: str,
        platform: str,
        objective: str,
        evidence: FormattedEvidence,
        max_total_memories: int = 5,
    ) -> List[MemoryRecallResult]:
        """
        Formulate targeted queries based on current empirical observations
        and retrieve bounded relevant experiences from Hindsight.
        """
        recalled: List[MemoryRecallResult] = []
        seen_ids = set()

        # Query 1: Platform and format performance lessons
        platform_query = MemoryRecallQuery(
            bank_id=bank_id,
            query=f"{platform} content format performance and audience reception for {objective}",
            platform=platform,
            max_tokens=1024,
        )
        for res in self.retriever.recall_experiences(platform_query, max_items=3):
            if res.id not in seen_ids:
                seen_ids.add(res.id)
                recalled.append(res)

        # Query 2: Topic-specific lessons for identified top topics or gaps
        topics_to_query = [t.split(":")[-1].strip() for t in evidence.top_performing_topics[:2]]
        for gap in evidence.content_gaps[:2]:
            topics_to_query.append(gap.topic)

        if topics_to_query and len(recalled) < max_total_memories:
            topic_str = " ".join(topics_to_query)
            topic_query = MemoryRecallQuery(
                bank_id=bank_id,
                query=f"topic engagement lessons and past experiments for {topic_str}",
                platform=platform,
                max_tokens=1024,
            )
            for res in self.retriever.recall_experiences(topic_query, max_items=2):
                if res.id not in seen_ids and len(recalled) < max_total_memories:
                    seen_ids.add(res.id)
                    recalled.append(res)

        return recalled
