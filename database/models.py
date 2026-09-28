"""
Application data models reflecting database records.
Separate from Hindsight memory models and API transport schemas.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
import json


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class BrandRecord:
    id: str
    name: str
    identity: str
    target_audience: str
    voice_tone: str
    communication_style: str
    created_at: str = field(default_factory=utc_now_iso)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentItemRecord:
    id: str
    brand_id: str
    platform: str
    content_id: str
    topic: Optional[str]
    content_type: str
    title: Optional[str]
    url: Optional[str]
    published_at: str
    metadata_json: str = "{}"

    @property
    def metadata(self) -> Dict[str, Any]:
        try:
            return json.loads(self.metadata_json)
        except Exception:
            return {}

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class ContentPerformanceRecord:
    id: str
    content_item_id: str
    views: Optional[int]
    engagements: int
    engagement_rate: Optional[float]
    likes: Optional[int]
    comments: Optional[int]
    shares: Optional[int]
    saves: Optional[int]
    measured_at: str
    source: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StrategyRecord:
    id: str
    brand_id: str
    objective: str
    target_audience: str
    recommended_platforms_json: str
    content_themes_json: str
    recommended_formats_json: str
    posting_recommendations_json: str
    rationale: str
    supporting_evidence_json: str
    recalled_memories_json: str
    confidence_notes: Optional[str] = None
    experiments_json: str = "[]"
    created_at: str = field(default_factory=utc_now_iso)

    @property
    def recommended_platforms(self) -> List[str]:
        return json.loads(self.recommended_platforms_json)

    @property
    def content_themes(self) -> List[Dict[str, Any]]:
        return json.loads(self.content_themes_json)

    @property
    def recommended_formats(self) -> List[Dict[str, Any]]:
        return json.loads(self.recommended_formats_json)

    @property
    def posting_recommendations(self) -> Dict[str, Any]:
        return json.loads(self.posting_recommendations_json)

    @property
    def supporting_evidence(self) -> Dict[str, Any]:
        return json.loads(self.supporting_evidence_json)

    @property
    def recalled_memories(self) -> List[Dict[str, Any]]:
        return json.loads(self.recalled_memories_json)

    @property
    def experiments(self) -> List[str]:
        return json.loads(self.experiments_json)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class StrategyOutcomeRecord:
    id: str
    strategy_id: str
    actual_metrics_json: str
    expected_metrics_json: str
    observed_difference: str
    reusable_lesson: str
    hindsight_memory_id: Optional[str] = None
    created_at: str = field(default_factory=utc_now_iso)

    @property
    def actual_metrics(self) -> Dict[str, Any]:
        return json.loads(self.actual_metrics_json)

    @property
    def expected_metrics(self) -> Dict[str, Any]:
        return json.loads(self.expected_metrics_json)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
