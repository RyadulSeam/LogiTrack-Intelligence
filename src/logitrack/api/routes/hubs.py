"""
Regional Hub Operations & Throughput Router
LogiTrack Intelligence — Phase 10: API & Application Layer
"""

from fastapi import APIRouter, status
from logitrack.api.schemas import HubsResponse, HubSummaryItem
from logitrack.analytics.metrics import get_hub_performance_summary

router = APIRouter(prefix="/api/v1/hubs", tags=["Regional Hubs"])


@router.get("", response_model=HubsResponse, status_code=status.HTTP_200_OK)
def get_all_hubs(db_path: str = "data/lake/logitrack.duckdb"):
    """
    Returns performance metrics, throughput, coordinates, and workload ratio for all 6 Texas Regional Hubs.
    """
    df = get_hub_performance_summary(db_path=db_path)
    hub_items = []
    for _, r in df.iterrows():
        hub_items.append(
            HubSummaryItem(
                hub_name=r["hub_name"],
                city=r["city"],
                daily_capacity=int(r["daily_capacity"]),
                latitude=float(r["latitude"]),
                longitude=float(r["longitude"]),
                total_orders=int(r["total_orders"]),
                delayed_orders=int(r["delayed_orders"]),
                avg_delivery_hours=float(r["avg_delivery_hours"] or 0.0),
                avg_processing_hours=float(r["avg_processing_hours"] or 0.0),
                avg_csat=float(r["avg_csat"] or 0.0),
                workload_ratio=float(r["workload_ratio"] or 0.0)
            )
        )
    return HubsResponse(total_hubs=len(hub_items), hubs=hub_items)
