"""
Grounded Strategy Context Model.
Rigidly separates:
- CURRENT ANALYTICS (from AnalyticsResult)
- DETERMINISTIC OBSERVATIONS (from AnalyticsResult)
- RECALLED MEMORIES (from Hindsight)
- BRAND CONTEXT (from BrandProfile)
- DATA QUALITY & LIMITATIONS
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from hindsight.schemas.memory_models import MemoryRecallResult
from models.brand import BrandProfile
from services.analytics_service.evidence_extractor import ContentGapSignal, FormattedEvidence


class GroundedStrategyContext(BaseModel):
    brand: BrandProfile
    objective: str
    target_platform: str
    current_evidence: FormattedEvidence
    recalled_experiences: List[MemoryRecallResult] = Field(default_factory=list)
    content_gaps: List[ContentGapSignal] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)

    def to_prompt_context_dict(self) -> Dict[str, Any]:
        """Formats into strict, segregated sections for LLM reasoning without math leakage."""
        return {
            "brand": {
                "name": self.brand.name,
                "identity": self.brand.identity,
                "target_audience": self.brand.target_audience,
                "tone": self.brand.voice_preferences.tone,
                "communication_style": self.brand.voice_preferences.communication_style,
            },
            "objective": self.objective,
            "platform": self.target_platform,
            "current_analytics_facts": {
                "sample_size": self.current_evidence.sample_size,
                "total_posts": self.current_evidence.total_posts,
                "median_engagement_rate": self.current_evidence.median_engagement_rate,
                "engagement_rate_basis": self.current_evidence.engagement_rate_basis,
                "top_formats": self.current_evidence.top_content_formats,
                "bottom_formats": self.current_evidence.bottom_content_formats,
                "top_performing_topics": self.current_evidence.top_performing_topics,
                "underperforming_topics": self.current_evidence.underperforming_topics,
            },
            "deterministic_observations": self.current_evidence.key_observations,
            "recalled_hindsight_experiences": [
                {
                    "memory_id": mem.id,
                    "lesson": mem.text,
                    "context": mem.context,
                }
                for mem in self.recalled_experiences
            ],
            "identified_content_gaps": [
                {
                    "topic": gap.topic,
                    "status": gap.status,
                    "rationale": gap.rationale,
                }
                for gap in self.content_gaps
            ],
            "data_quality_and_limitations": self.limitations + self.current_evidence.data_quality_warnings,
        }
