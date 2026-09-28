"""
Brand identity, tone of voice, audience preferences, and communication guidelines.
"""

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, Field


class BrandVoicePreferences(BaseModel):
    tone: str = Field("professional, authoritative yet accessible", description="Primary tone of communication")
    communication_style: str = Field("educational, insight-driven, non-promotional", description="Writing and structuring style")
    preferred_topics: List[str] = Field(default_factory=list, description="Core priority topics/pillars")
    prohibited_claims: List[str] = Field(default_factory=list, description="Styles or claims to avoid")


class BrandProfile(BaseModel):
    brand_id: str = Field(..., description="Unique identifier for the brand")
    name: str = Field(..., description="Brand or creator name")
    identity: str = Field(..., description="Company mission, domain, and purpose")
    target_audience: str = Field(..., description="Target demographic, skill level, and goals")
    voice_preferences: BrandVoicePreferences = Field(default_factory=BrandVoicePreferences)
