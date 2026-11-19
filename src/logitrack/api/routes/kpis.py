"""
Executive & Operational KPIs Router
LogiTrack Intelligence — Phase 10: API & Application Layer
"""

from typing import Optional
from fastapi import APIRouter, Query, status
from logitrack.api.schemas import ExecutiveKPIsResponse
from logitrack.analytics.metrics import get_executive_kpis

router = APIRouter(prefix="/api/v1/kpis", tags=["Executive KPIs"])


@router.get("/executive", response_model=ExecutiveKPIsResponse, status_code=status.HTTP_200_OK)
def get_control_tower_kpis(
    hub_name: Optional[str] = Query(None, description="Filter by Texas Hub Name (e.g. 'Dallas Main Hub')"),
    db_path: str = "data/lake/logitrack.duckdb"
):
    """
    Returns high-level Executive Control Tower KPIs including:
    Total Orders, Fulfilled, SLA On-Time Delivery Rate %, Delay %, Avg Duration, and Fleet Utilization.
    """
    kpis = get_executive_kpis(db_path=db_path, hub_filter=hub_name)
    return ExecutiveKPIsResponse(**kpis)
