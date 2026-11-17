"""
Core Logistics Business Metrics & KPI Engine
LogiTrack Intelligence — Phase 7

Computes operational SLAs, fleet utilization, hub congestion, and root-cause metrics
from the Gold warehouse layer and live streaming tables.
"""

from typing import Dict, Any, Optional
import pandas as pd
from logitrack.storage.duckdb_manager import DuckDBManager


def calculate_otd_rate(on_time_count: int, eligible_count: int) -> float:
    """Computes On-Time Delivery Rate: (On-Time / Eligible) * 100."""
    if not eligible_count or eligible_count <= 0:
        return 0.0
    return round((on_time_count / eligible_count) * 100.0, 2)


def calculate_delay_rate(delayed_count: int, eligible_count: int) -> float:
    """Computes Delay Rate: (Delayed / Eligible) * 100."""
    if not eligible_count or eligible_count <= 0:
        return 0.0
    return round((delayed_count / eligible_count) * 100.0, 2)


def get_executive_kpis(db_path: str = "data/lake/logitrack.duckdb", hub_filter: Optional[str] = None) -> Dict[str, Any]:
    """Retrieves high-level Executive Control Tower KPIs from warehouse.fact_orders."""
    manager = DuckDBManager(db_path=db_path)
    
    where_clause = ""
    params = []
    if hub_filter and hub_filter != "All Hubs":
        where_clause = "WHERE h.hub_name = ?"
        params.append(hub_filter)

    query = f"""
    SELECT
        COUNT(*) AS total_orders,
        SUM(CASE WHEN f.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
        SUM(CASE WHEN f.order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders,
        SUM(CASE WHEN f.is_on_time = TRUE AND f.order_status = 'Delivered' THEN 1 ELSE 0 END) AS on_time_orders,
        SUM(CASE WHEN f.is_delayed = TRUE AND f.order_status = 'Delivered' THEN 1 ELSE 0 END) AS delayed_orders,
        ROUND(AVG(CASE WHEN f.order_status = 'Delivered' THEN f.delivery_time_hours ELSE NULL END), 2) AS avg_delivery_time_hours,
        ROUND(AVG(f.hub_processing_time_hours), 2) AS avg_hub_processing_hours,
        ROUND(AVG(CASE WHEN f.order_status = 'Delivered' THEN f.csat_score ELSE NULL END), 2) AS avg_csat_score
    FROM warehouse.fact_orders f
    JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
    {where_clause};
    """
    df = manager.conn.execute(query, params).df()

    # Fleet metrics
    fleet_df = manager.query("""
        SELECT
            COUNT(*) AS total_vehicles,
            SUM(CASE WHEN current_status = 'Active' THEN 1 ELSE 0 END) AS active_vehicles,
            SUM(CASE WHEN current_status = 'Maintenance' THEN 1 ELSE 0 END) AS maintenance_vehicles,
            SUM(CASE WHEN is_maintenance_alert = TRUE THEN 1 ELSE 0 END) AS maintenance_alerts
        FROM warehouse.dim_vehicle;
    """)
    manager.close()

    total_orders = int(df["total_orders"][0])
    delivered = int(df["delivered_orders"][0])
    on_time = int(df["on_time_orders"][0])
    delayed = int(df["delayed_orders"][0])

    otd_pct = calculate_otd_rate(on_time, delivered)
    delay_pct = calculate_delay_rate(delayed, delivered)

    total_fleet = int(fleet_df["total_vehicles"][0])
    active_fleet = int(fleet_df["active_vehicles"][0])
    fleet_utilization = round((active_fleet / total_fleet * 100), 1) if total_fleet > 0 else 0.0

    return {
        "total_orders": total_orders,
        "delivered_orders": delivered,
        "cancelled_orders": int(df["cancelled_orders"][0]),
        "on_time_delivery_rate_pct": otd_pct,
        "delay_rate_pct": delay_pct,
        "avg_delivery_time_hours": float(df["avg_delivery_time_hours"][0] or 0.0),
        "avg_hub_processing_hours": float(df["avg_hub_processing_hours"][0] or 0.0),
        "avg_csat_score": float(df["avg_csat_score"][0] or 0.0),
        "total_fleet": total_fleet,
        "active_fleet": active_fleet,
        "fleet_utilization_pct": fleet_utilization,
        "maintenance_alerts": int(fleet_df["maintenance_alerts"][0]),
    }


def get_hub_performance_summary(db_path: str = "data/lake/logitrack.duckdb") -> pd.DataFrame:
    """Returns aggregated hub operational statistics with coordinates and capacity utilization."""
    manager = DuckDBManager(db_path=db_path)
    df = manager.query("""
        SELECT
            h.hub_name,
            h.city,
            h.daily_capacity,
            h.latitude,
            h.longitude,
            COUNT(f.order_id) AS total_orders,
            SUM(CASE WHEN f.is_delayed = TRUE THEN 1 ELSE 0 END) AS delayed_orders,
            ROUND(AVG(CASE WHEN f.order_status = 'Delivered' THEN f.delivery_time_hours ELSE NULL END), 2) AS avg_delivery_hours,
            ROUND(AVG(f.hub_processing_time_hours), 2) AS avg_processing_hours,
            ROUND(AVG(f.csat_score), 2) AS avg_csat,
            ROUND((COUNT(f.order_id)::DECIMAL / NULLIF(SUM(h.daily_capacity), 0)) * 100, 2) AS workload_ratio
        FROM warehouse.dim_hub h
        LEFT JOIN warehouse.fact_orders f ON h.hub_key = f.hub_key
        GROUP BY h.hub_name, h.city, h.daily_capacity, h.latitude, h.longitude
        ORDER BY total_orders DESC;
    """)
    manager.close()
    return df


def get_live_fleet_positions(db_path: str = "data/lake/logitrack.duckdb") -> pd.DataFrame:
    """Returns the most recent GPS location and status for each tracked vehicle."""
    manager = DuckDBManager(db_path=db_path)
    df = manager.query("""
        WITH ranked_telemetry AS (
            SELECT
                v.vehicle_code,
                v.vehicle_model,
                v.vehicle_type,
                v.current_status,
                t.latitude,
                t.longitude,
                t.speed_kmh,
                t.heading_deg,
                t.fuel_level_pct,
                t.engine_temp_c,
                t.engine_status,
                t.ping_timestamp,
                ROW_NUMBER() OVER(PARTITION BY v.vehicle_code ORDER BY t.ping_timestamp DESC) as rn
            FROM warehouse.dim_vehicle v
            JOIN warehouse.fact_vehicle_telemetry t ON v.vehicle_key = t.vehicle_key
        )
        SELECT * EXCLUDE (rn)
        FROM ranked_telemetry
        WHERE rn = 1;
    """)
    manager.close()
    return df


def get_delay_root_causes(db_path: str = "data/lake/logitrack.duckdb") -> pd.DataFrame:
    """Returns breakdown of delay root causes for delayed shipments."""
    manager = DuckDBManager(db_path=db_path)
    df = manager.query("""
        SELECT
            delay_reason,
            COUNT(*) AS incident_count,
            ROUND(AVG(delivery_time_hours), 2) AS avg_delivery_hours,
            ROUND(AVG(csat_score), 2) AS avg_csat
        FROM warehouse.fact_orders
        WHERE is_delayed = TRUE AND delay_reason IS NOT NULL
        GROUP BY delay_reason
        ORDER BY incident_count DESC;
    """)
    manager.close()
    return df
