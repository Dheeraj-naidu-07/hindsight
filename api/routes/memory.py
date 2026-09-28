"""
Hindsight Memory Endpoints.
Allows frontend and developers to query and inspect persistent memories.
"""

from __future__ import annotations

from typing import Optional
from fastapi import APIRouter, Depends, Query, status
from api.dependencies.deps import get_experience_retriever
from api.schemas.requests import MemoryQueryRequest
from api.schemas.responses import MemoryListResponse
from hindsight.recall.experience_retriever import ExperienceRetriever
from hindsight.schemas.memory_models import MemoryRecallQuery

router = APIRouter(prefix="/api/v1/memory", tags=["Hindsight Memory"])


@router.get("/{bank_id}", response_model=MemoryListResponse)
def query_memory_bank(
    bank_id: str,
    query: str = Query("content strategy performance lessons", description="Recall search query"),
    platform: Optional[str] = Query(None, description="Optional platform tag filter"),
    retriever: ExperienceRetriever = Depends(get_experience_retriever),
) -> MemoryListResponse:
    mem_query = MemoryRecallQuery(
        bank_id=bank_id,
        query=query,
        platform=platform,
    )
    results = retriever.recall_experiences(mem_query, max_items=10)

    memories_payload = [
        {
            "id": r.id,
            "text": r.text,
            "context": r.context,
            "metadata": r.metadata,
        }
        for r in results
    ]

    return MemoryListResponse(
        bank_id=bank_id,
        count=len(memories_payload),
        memories=memories_payload,
    )
