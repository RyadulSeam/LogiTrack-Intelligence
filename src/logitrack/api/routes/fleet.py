"""
Fleet Telematics & Vehicle Tracking Router
LogiTrack Intelligence — Phase 10: API & Application Layer
"""

from fastapi import APIRouter, status
from logitrack.api.schemas import FleetResponse, FleetVehicleItem
from logitrack.analytics.metrics import get_live_fleet_positions

router = APIRouter(prefix="/api/v1/fleet", tags=["Fleet & Telematics"])


@router.get("", response_model=FleetResponse, status_code=status.HTTP_200_OK)
def get_fleet_telematics(db_path: str = "data/lake/logitrack.duckdb"):
    """
    Returns latest GPS positions, telemetry signals, and maintenance statuses across the fleet assets.
    """
    df = get_live_fleet_positions(db_path=db_path)
    vehicles = []
    active_count = 0
    for _, r in df.iterrows():
        status_val = r["current_status"]
        if status_val == "Active":
            active_count += 1
        vehicles.append(
            FleetVehicleItem(
                vehicle_code=r["vehicle_code"],
                vehicle_model=r["vehicle_model"],
                vehicle_type=r["vehicle_type"],
                current_status=status_val,
                latitude=float(r["latitude"]) if pd_not_na(r["latitude"]) else None,
                longitude=float(r["longitude"]) if pd_not_na(r["longitude"]) else None,
                speed_kmh=float(r["speed_kmh"]) if pd_not_na(r["speed_kmh"]) else None,
                fuel_level_pct=float(r["fuel_level_pct"]) if pd_not_na(r["fuel_level_pct"]) else None,
                engine_temp_c=float(r["engine_temp_c"]) if pd_not_na(r["engine_temp_c"]) else None,
                engine_status=str(r["engine_status"]) if pd_not_na(r["engine_status"]) else None
            )
        )
    return FleetResponse(total_fleet=len(vehicles), active_fleet=active_count, vehicles=vehicles)


def pd_not_na(val):
    import pandas as pd
    return pd.notna(val)
