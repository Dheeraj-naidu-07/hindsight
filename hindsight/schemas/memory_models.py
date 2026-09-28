"""
Data schemas for structured memory items, queries, and recall results in Hindsight.
Preserves high-signal experiences rather than raw metric dumps.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReusableExperience(BaseModel):
    """
    A high-signal, synthesized strategic learning item to be stored in Hindsight.
    Stores reusable lessons, empirical evidence, and operational context.
    """
    bank_id: str = Field(..., description="Target Hindsight memory bank (e.g. brand ID)")
    lesson: str = Field(..., description="Synthesized strategic rule or takeaway")
    strategy_used: str = Field(..., description="The planned approach that was tested")
    platform: str = Field(..., description="Social platform (youtube, instagram, reddit)")
    content_type: str = Field(..., description="Format (short, video, reel, post, etc.)")
    topic: Optional[str] = Field(None, description="Primary subject or content pillar")
    audience_context: Optional[str] = Field(None, description="Audience demographic or response")
    observed_outcome: str = Field(..., description="Empirical result observed (e.g. +38% above baseline)")
    supporting_evidence: Dict[str, Any] = Field(
        default_factory=dict, description="Numerical proofs, sample sizes, and baselines"
    )
    tags: List[str] = Field(default_factory=list, description="Categorization tags for targeted recall")
    timestamp: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(),
        description="Event UTC timestamp"
    )

    def generate_fingerprint(self) -> str:
        """Deterministic fingerprint to prevent duplicate memories for identical experiences."""
        raw_key = f"{self.platform}:{self.content_type}:{self.topic or ''}:{self.lesson.strip().lower()}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()[:16]

    def to_hindsight_content(self) -> str:
        """
        Formats memory content into a clean, human- and LLM-friendly paragraph.
        Avoids huge raw payloads while preserving deep strategic value.
        """
        topic_clause = f" on '{self.topic}'" if self.topic else ""
        return (
            f"Strategy Lesson [{self.platform.upper()} - {self.content_type}{topic_clause}]: "
            f"{self.lesson} "
            f"Context: Tested '{self.strategy_used}'. "
            f"Observed Result: {self.observed_outcome}."
        )

    def to_hindsight_metadata(self) -> Dict[str, str]:
        """Convert attributes to string key-values accepted by Hindsight metadata API."""
        return {
            "platform": self.platform,
            "content_type": self.content_type,
            "topic": self.topic or "general",
            "fingerprint": self.generate_fingerprint(),
            "evidence": json.dumps(self.supporting_evidence),
        }


class MemoryRecallQuery(BaseModel):
    """Query specification for retrieving relevant memories from Hindsight."""
    bank_id: str
    query: str
    platform: Optional[str] = None
    topic: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None
    max_tokens: int = Field(2048, description="Budget cap for recalled memories")


class MemoryRecallResult(BaseModel):
    """A bounded, grounded recall item returned from Hindsight."""
    id: str
    text: str
    type: str = "experience"
    context: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    relevance_score: Optional[float] = None
