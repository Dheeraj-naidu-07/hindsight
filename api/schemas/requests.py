"""
API Request Schemas.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional
from pydantic import BaseModel, Field
from models.brand import BrandProfile
from social_analytics.models.output import AnalyticsResult


class GenerateStrategyRequest(BaseModel):
    brand_id: str = Field(..., description="Unique brand identifier")
    platform: Literal["youtube", "instagram", "reddit"] = Field(..., description="Target social platform")
    account_id: str = Field(..., description="Platform handle or account ID")
    objective: str = Field(
        "Maximize authority, qualified developer engagement, and content durability",
        description="Core campaign/quarterly objective",
    )
    start_date: Optional[datetime] = Field(
        None,
        description="Start timestamp of analysis window (e.g. 2026-09-01T00:00:00Z)",
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End timestamp of analysis window (e.g. 2026-09-30T00:00:00Z)",
    )
    custom_brand_profile: Optional[BrandProfile] = None
    analytics_result: Optional[AnalyticsResult] = Field(
        None, description="Optional pre-computed analytics deliverable"
    )
    platform_api_key: Optional[str] = Field(
        None, description="Social platform API key (e.g. YouTube Data API key, Instagram token). If omitted, read from environment."
    )
    llm_api_key: Optional[str] = Field(
        None, description="LLM provider API key (e.g. Gemini or OpenAI API key). If omitted, read from environment."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "brand_id": "my_brand",
                "platform": "youtube",
                "account_id": "your_channel_or_handle",
                "objective": "Grow high-intent audience and improve content retention",
                "start_date": "2026-09-01T00:00:00Z",
                "end_date": "2026-09-30T00:00:00Z",
                "platform_api_key": "YOUR_YOUTUBE_API_KEY",
                "llm_api_key": "YOUR_GEMINI_OR_OPENAI_API_KEY",
            }
        }
    }


class RecordOutcomeRequest(BaseModel):
    strategy_id: str = Field(..., description="ID of the previously generated strategy being evaluated")
    platform: Optional[Literal["youtube", "instagram", "reddit"]] = Field(
        None, description="Platform identifier (optional if re-running analytics)"
    )
    account_id: Optional[str] = Field(
        None, description="Platform account handle (optional if re-running analytics)"
    )
    analytics_result: Optional[AnalyticsResult] = Field(
        None, description="Subsequent empirical AnalyticsResult payload (optional, will re-run analytics if omitted)"
    )
    platform_api_key: Optional[str] = Field(
        None, description="Optional platform API key for re-running analytics"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "strategy_id": "strat_abc12345",
                "platform": "youtube",
                "account_id": "your_channel_or_handle",
                "platform_api_key": "YOUR_YOUTUBE_API_KEY",
            }
        }
    }


class MemoryQueryRequest(BaseModel):
    query: str = Field(..., description="Query for Hindsight recall")
    tags: Optional[List[str]] = None
    max_tokens: int = Field(2048, description="Max token budget for recall")
