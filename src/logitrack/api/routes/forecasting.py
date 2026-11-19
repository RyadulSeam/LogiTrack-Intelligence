"""
Forecasting APIs Router
LogiTrack Intelligence — Phase 10: API & Application Layer
"""

from typing import Optional
import duckdb
from fastapi import APIRouter, Query, status
from logitrack.api.schemas import (
    DemandForecastResponse,
    DemandForecastItem,
    HubWorkloadForecastResponse,
    HubWorkloadForecastItem,
    FleetRequirementForecastResponse,
    FleetRequirementForecastItem
)

router = APIRouter(prefix="/api/v1/forecasting", tags=["Time-Series Forecasting"])


@router.get("/demand", response_model=DemandForecastResponse, status_code=status.HTTP_200_OK)
def get_demand_forecast(
    hub_name: Optional[str] = Query(None, description="Optional Hub Filter"),
    horizon_days: int = Query(30, ge=1, le=30, description="Forecast Horizon in Days (e.g. 7 or 30)"),
    db_path: str = "data/lake/logitrack.duckdb"
):
    """
    Returns 7-day or 30-day forecasted order volume per regional hub with 95% Confidence Intervals.
    All outputs explicitly carry is_synthetic_simulated provenance tags.
    """
    conn = duckdb.connect(db_path, read_only=True)
    where_sql = "WHERE horizon_step <= ?"
    params = [horizon_days]
    if hub_name:
        where_sql += " AND hub_name = ?"
        params.append(hub_name)

    query = f"""
        SELECT 
            CAST(forecast_date AS VARCHAR) as forecast_date,
            horizon_step,
            hub_id,
            hub_name,
            daily_capacity,
            forecast_order_volume,
            lower_bound_95,
            upper_bound_95,
            is_synthetic_simulated
        FROM forecasting.demand_forecasts
        {where_sql}
        ORDER BY hub_name, horizon_step;
    """
    df = conn.execute(query, params).fetchdf()
    conn.close()

    items = [DemandForecastItem(**r) for r in df.to_dict(orient="records")]
    return DemandForecastResponse(horizon_days=horizon_days, forecasts=items)


@router.get("/workload", response_model=HubWorkloadForecastResponse, status_code=status.HTTP_200_OK)
def get_hub_workload_forecast(
    horizon_days: int = Query(30, ge=1, le=30),
    db_path: str = "data/lake/logitrack.duckdb"
):
    """
    Returns daily capacity utilization %, dispatched volume, and bottleneck alert flags per hub.
    """
    conn = duckdb.connect(db_path, read_only=True)
    df = conn.execute("""
        SELECT 
            CAST(forecast_date AS VARCHAR) as forecast_date,
            horizon_step,
            hub_id,
            hub_name,
            forecast_order_volume,
            forecast_dispatched_volume,
            projected_daily_backlog,
            capacity_utilization_pct,
            is_bottleneck_risk,
            risk_level
        FROM forecasting.hub_workload_forecasts
        WHERE horizon_step <= ?
        ORDER BY hub_name, horizon_step;
    """, [horizon_days]).fetchdf()
    conn.close()

    items = [HubWorkloadForecastItem(**r) for r in df.to_dict(orient="records")]
    return HubWorkloadForecastResponse(horizon_days=horizon_days, workload_forecasts=items)


@router.get("/fleet", response_model=FleetRequirementForecastResponse, status_code=status.HTTP_200_OK)
def get_fleet_requirement_forecast(
    horizon_days: int = Query(30, ge=1, le=30),
    db_path: str = "data/lake/logitrack.duckdb"
):
    """
    Returns daily required vehicle counts across 4 vehicle classes and fleet deficit/surplus gaps.
    """
    conn = duckdb.connect(db_path, read_only=True)
    df = conn.execute("""
        SELECT 
            CAST(forecast_date AS VARCHAR) as forecast_date,
            hub_name,
            vehicle_type,
            projected_parcels,
            vehicles_required,
            active_fleet_baseline,
            surplus_or_deficit,
            is_fleet_deficit,
            utilization_rate_pct
        FROM forecasting.fleet_requirement_forecasts
        ORDER BY forecast_date, hub_name, vehicle_type;
    """).fetchdf()
    conn.close()

    items = [FleetRequirementForecastItem(**r) for r in df.to_dict(orient="records")]
    return FleetRequirementForecastResponse(horizon_days=horizon_days, fleet_forecasts=items)
