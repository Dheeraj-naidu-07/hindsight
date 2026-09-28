"""
Common shared schemas across API and agent layers.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    error: str = Field(..., description="Error code or category")
    detail: str = Field(..., description="Human-readable explanation")
    details: Optional[Dict[str, Any]] = None


class HealthCheckResponse(BaseModel):
    status: str = "ok"
    version: str = "1.0.0"
    database: str = "connected"
    hindsight: str = "configured"
