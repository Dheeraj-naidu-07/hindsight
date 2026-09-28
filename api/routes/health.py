"""
Health Check Route.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from api.dependencies.deps import get_database_connection, get_hindsight_wrapper
from database.connection import DatabaseConnection
from hindsight.client.hindsight_client_wrapper import HindsightClientWrapper
from schemas.common import HealthCheckResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthCheckResponse)
def health_check(
    db: DatabaseConnection = Depends(get_database_connection),
    hindsight: HindsightClientWrapper = Depends(get_hindsight_wrapper),
) -> HealthCheckResponse:
    # Verify DB connection
    with db.get_connection() as conn:
        conn.execute("SELECT 1")

    hindsight_status = "connected_server" if hindsight.is_connected_to_server else "resilient_offline_mode"

    return HealthCheckResponse(
        status="ok",
        version="1.0.0",
        database="connected",
        hindsight=hindsight_status,
    )
