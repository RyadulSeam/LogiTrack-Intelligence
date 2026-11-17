"""
ML Feature Engineering & Dataset Extraction
LogiTrack Intelligence — Phase 8

Extracts training features from warehouse Gold tables and synthetic logs
using time-aware ordering to prevent future data leakage.
"""

from typing import Tuple, Dict, Any
import os
import pandas as pd
from loguru import logger
from logitrack.storage.duckdb_manager import DuckDBManager


def extract_delay_features(db_path: str = "data/lake/logitrack.duckdb") -> pd.DataFrame:
    """
    Extracts features for Order Delay Risk Prediction.
    
    Target: is_delayed (0 or 1)
    Temporal Ordering: full_date ASC
    """
    manager = DuckDBManager(db_path=db_path)
    df = manager.query("""
        SELECT
            f.order_id,
            d.full_date AS order_date,
            d.day_of_week,
            d.month_number,
            h.hub_name,
            h.daily_capacity AS hub_capacity,
            dr.experience_years AS driver_experience,
            dr.performance_rating AS driver_rating,
            dr.employment_type,
            v.vehicle_type,
            v.lifetime_breakdowns,
            f.hub_processing_time_hours,
            CASE WHEN f.is_delayed = TRUE THEN 1 ELSE 0 END AS is_delayed
        FROM warehouse.fact_orders f
        JOIN warehouse.dim_date d ON f.order_date_key = d.date_key
        JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
        JOIN warehouse.dim_driver dr ON f.driver_key = dr.driver_key
        JOIN warehouse.dim_vehicle v ON f.vehicle_key = v.vehicle_key
        WHERE f.order_status = 'Delivered'
        ORDER BY d.full_date ASC;
    """)
    manager.close()
    logger.info(f"Extracted {len(df):,} records for Delay Risk modeling")
    return df


def extract_eta_features(db_path: str = "data/lake/logitrack.duckdb") -> pd.DataFrame:
    """
    Extracts features for Delivery ETA Regression.
    
    Target: delivery_time_hours
    Temporal Ordering: full_date ASC
    """
    manager = DuckDBManager(db_path=db_path)
    df = manager.query("""
        SELECT
            f.order_id,
            d.full_date AS order_date,
            d.day_of_week,
            d.month_number,
            h.hub_name,
            h.daily_capacity AS hub_capacity,
            dr.experience_years AS driver_experience,
            dr.performance_rating AS driver_rating,
            v.vehicle_type,
            f.hub_processing_time_hours,
            f.delivery_time_hours
        FROM warehouse.fact_orders f
        JOIN warehouse.dim_date d ON f.order_date_key = d.date_key
        JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
        JOIN warehouse.dim_driver dr ON f.driver_key = dr.driver_key
        JOIN warehouse.dim_vehicle v ON f.vehicle_key = v.vehicle_key
        WHERE f.order_status = 'Delivered' AND f.delivery_time_hours IS NOT NULL
        ORDER BY d.full_date ASC;
    """)
    manager.close()
    logger.info(f"Extracted {len(df):,} records for ETA regression modeling")
    return df


def extract_hub_congestion_features(db_path: str = "data/lake/logitrack.duckdb") -> pd.DataFrame:
    """
    Extracts hourly metrics for Regional Hub Congestion Classification.
    
    Target: is_congested (1 if backlog_volume > 0 or capacity_utilization_pct >= 6.0, else 0)
    Temporal Ordering: full_date ASC, hour_of_day ASC
    """
    manager = DuckDBManager(db_path=db_path)
    df = manager.query("""
        SELECT
            f.hub_hourly_id,
            d.full_date AS observation_date,
            d.day_of_week,
            f.hour_of_day,
            h.hub_name,
            h.daily_capacity,
            f.orders_received,
            f.orders_dispatched,
            COALESCE(f.avg_processing_time_hours, 0.0) AS avg_processing_time_hours,
            COALESCE(f.capacity_utilization_pct, 0.0) AS capacity_utilization_pct,
            f.backlog_volume,
            CASE 
                WHEN f.backlog_volume > 0 OR f.capacity_utilization_pct >= 6.0 THEN 1 
                ELSE 0 
            END AS is_congested
        FROM warehouse.fact_hub_hourly f
        JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
        JOIN warehouse.dim_date d ON f.date_key = d.date_key
        ORDER BY d.full_date ASC, f.hour_of_day ASC;
    """)
    manager.close()
    logger.info(f"Extracted {len(df):,} hourly records for Hub Congestion modeling")
    return df


def extract_maintenance_features(
    db_path: str = "data/lake/logitrack.duckdb",
    maintenance_csv: str = "data/synthetic/synthetic_maintenance.csv"
) -> pd.DataFrame:
    """
    Extracts fleet health metrics for Predictive Fleet Maintenance.
    
    Target: maintenance_risk (1 if maintenance alert is flagged or lifetime breakdowns >= 3, else 0)
    """
    manager = DuckDBManager(db_path=db_path)
    vehicles = manager.query("""
        SELECT
            vehicle_id,
            vehicle_code,
            vehicle_model,
            vehicle_type,
            lifetime_breakdowns,
            DATEDIFF('day', purchase_date, DATE '2026-11-17') AS fleet_age_days,
            CASE 
                WHEN is_maintenance_alert = TRUE OR lifetime_breakdowns >= 3 THEN 1 
                ELSE 0 
            END AS maintenance_target
        FROM warehouse.dim_vehicle;
    """)
    manager.close()

    # Join with synthetic maintenance history if available
    if os.path.exists(maintenance_csv):
        maint_df = pd.read_csv(maintenance_csv)
        summary = maint_df.groupby("vehicle_code").agg(
            total_maint_events=("maintenance_id", "count"),
            avg_downtime_hours=("downtime_hours", "mean"),
            total_maint_cost=("cost_usd", "sum")
        ).reset_index()
        summary["avg_downtime_hours"] = summary["avg_downtime_hours"].fillna(0.0)
        merged = pd.merge(vehicles, summary, on="vehicle_code", how="left")
        merged["total_maint_events"] = merged["total_maint_events"].fillna(0)
        merged["avg_downtime_hours"] = merged["avg_downtime_hours"].fillna(0.0)
        merged["total_maint_cost"] = merged["total_maint_cost"].fillna(0.0)
    else:
        merged = vehicles
        merged["total_maint_events"] = 0
        merged["avg_downtime_hours"] = 0.0
        merged["total_maint_cost"] = 0.0

    logger.info(f"Extracted {len(merged):,} vehicle fleet records for Predictive Maintenance")
    return merged
