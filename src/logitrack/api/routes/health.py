"""
Health Check & System Diagnostics Router
LogiTrack Intelligence — Phase 10: API & Application Layer
"""

from fastapi import APIRouter, status
from logitrack.api.schemas import HealthCheckResponse
import duckdb

router = APIRouter(prefix="", tags=["System"])


@router.get("/health", response_model=HealthCheckResponse, status_code=status.HTTP_200_OK)
def get_health_status(db_path: str = "data/lake/logitrack.duckdb"):
    """Validates service health and DuckDB lakehouse connectivity."""
    db_status = "CONNECTED"
    try:
        conn = duckdb.connect(db_path, read_only=True)
        conn.execute("SELECT 1").fetchall()
        conn.close()
    except Exception as e:
        db_status = f"ERROR: {str(e)}"

    return HealthCheckResponse(
        status="HEALTHY" if db_status == "CONNECTED" else "DEGRADED",
        version="1.0.0",
        database=db_status,
        environment="production-ready"
    )
