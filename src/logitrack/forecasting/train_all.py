"""
End-to-End Forecasting Training & DuckDB Registry Orchestration
LogiTrack Intelligence — Phase 9: Forecasting Engineering

Trains all 3 forecasting models:
1. Regional Demand Forecaster (Point + 95% Confidence Intervals)
2. Hub Workload & Capacity Forecaster
3. Fleet Requirement & Vehicle Allocation Forecaster

Evaluates performance with non-leaking chronological backtesting,
saves artifacts to models/artifacts/, and registers results into DuckDB schema 'forecasting'.
"""

from typing import Dict, Any
import os
import json
import uuid
from datetime import datetime
import duckdb
import pandas as pd
from loguru import logger

from logitrack.forecasting.features import (
    extract_daily_demand_series,
    build_time_series_features,
    split_chronological
)
from logitrack.forecasting.demand_forecaster import RegionalDemandForecaster
from logitrack.forecasting.hub_workload_forecaster import HubWorkloadForecaster
from logitrack.forecasting.fleet_requirement_forecaster import FleetRequirementForecaster


def init_forecasting_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """
    Creates the 'forecasting' schema and tracking tables in DuckDB lakehouse.
    """
    logger.info("Initializing DuckDB 'forecasting' schema and tables")
    conn.execute("CREATE SCHEMA IF NOT EXISTS forecasting;")

    conn.execute("""
    CREATE TABLE IF NOT EXISTS forecasting.model_registry (
        model_id VARCHAR PRIMARY KEY,
        model_name VARCHAR NOT NULL,
        version VARCHAR NOT NULL,
        algorithm VARCHAR NOT NULL,
        forecast_horizon VARCHAR NOT NULL,
        training_records INTEGER NOT NULL,
        hyperparameters JSON,
        artifact_path VARCHAR NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS forecasting.model_evaluations (
        evaluation_id VARCHAR PRIMARY KEY,
        model_id VARCHAR NOT NULL,
        metric_name VARCHAR NOT NULL,
        metric_value DOUBLE NOT NULL,
        evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS forecasting.demand_forecasts (
        forecast_id VARCHAR PRIMARY KEY,
        model_id VARCHAR NOT NULL,
        forecast_date DATE NOT NULL,
        horizon_step INTEGER NOT NULL,
        hub_id VARCHAR NOT NULL,
        hub_name VARCHAR NOT NULL,
        daily_capacity INTEGER NOT NULL,
        forecast_order_volume DOUBLE NOT NULL,
        lower_bound_95 DOUBLE NOT NULL,
        upper_bound_95 DOUBLE NOT NULL,
        is_synthetic_simulated BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS forecasting.hub_workload_forecasts (
        workload_id VARCHAR PRIMARY KEY,
        forecast_date DATE NOT NULL,
        horizon_step INTEGER NOT NULL,
        hub_id VARCHAR NOT NULL,
        hub_name VARCHAR NOT NULL,
        forecast_order_volume DOUBLE NOT NULL,
        forecast_dispatched_volume DOUBLE NOT NULL,
        projected_daily_backlog DOUBLE NOT NULL,
        capacity_utilization_pct DOUBLE NOT NULL,
        is_bottleneck_risk BOOLEAN NOT NULL,
        risk_level VARCHAR NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS forecasting.fleet_requirement_forecasts (
        fleet_req_id VARCHAR PRIMARY KEY,
        forecast_date DATE NOT NULL,
        hub_name VARCHAR NOT NULL,
        vehicle_type VARCHAR NOT NULL,
        projected_parcels DOUBLE NOT NULL,
        vehicles_required INTEGER NOT NULL,
        active_fleet_baseline INTEGER NOT NULL,
        surplus_or_deficit INTEGER NOT NULL,
        is_fleet_deficit BOOLEAN NOT NULL,
        utilization_rate_pct DOUBLE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)
    logger.info("DuckDB forecasting tables verified.")


def run_forecasting_pipeline(db_path: str = "data/lake/logitrack.duckdb") -> Dict[str, Any]:
    """
    Executes the end-to-end Phase 9 forecasting pipeline.
    """
    logger.info("==================================================")
    logger.info("Starting Phase 9 Forecasting Engineering Pipeline")
    logger.info("==================================================")

    os.makedirs("models/artifacts", exist_ok=True)
    conn = duckdb.connect(db_path)
    init_forecasting_schema(conn)

    # 1. Feature Extraction & Engineering
    raw_daily_df = extract_daily_demand_series(db_path=db_path, conn=conn)
    features_df = build_time_series_features(raw_daily_df, target_col="order_volume")
    train_df, test_df = split_chronological(features_df, test_days=92)

    # ----------------------------------------------------
    # Model 1: Regional Demand Forecaster
    # ----------------------------------------------------
    logger.info("--- [1/3] Training Regional Demand Forecaster (Point + 95% CI) ---")
    demand_forecaster = RegionalDemandForecaster(n_estimators=150, max_depth=4, learning_rate=0.05)
    train_metrics = demand_forecaster.train(train_df, target_col="order_volume")
    test_metrics, eval_df = demand_forecaster.evaluate(test_df, target_col="order_volume")
    demand_artifact = demand_forecaster.save("models/artifacts/demand_forecaster.joblib")

    # Generate 30-day forward forecast (includes 7-day subset)
    forward_forecast_df = demand_forecaster.forecast_future(raw_daily_df, horizon_days=30)
    logger.info(f"Generated 30-day forward demand forecast: {len(forward_forecast_df)} predictions")

    # Register Model 1 in DuckDB
    mod1_id = f"mod-fore-demand-{uuid.uuid4().hex[:8]}"
    conn.execute("""
        INSERT INTO forecasting.model_registry (
            model_id, model_name, version, algorithm, forecast_horizon,
            training_records, hyperparameters, artifact_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        mod1_id,
        "regional_demand_forecaster",
        "1.0.0",
        "GradientBoostingRegressor-QuantileIntervals",
        "7-day & 30-day",
        len(train_df),
        json.dumps(demand_forecaster.params),
        demand_artifact,
        True
    ])

    for metric_name, metric_val in test_metrics.items():
        conn.execute("""
            INSERT INTO forecasting.model_evaluations (evaluation_id, model_id, metric_name, metric_value)
            VALUES (?, ?, ?, ?);
        """, [f"eval-{uuid.uuid4().hex[:8]}", mod1_id, metric_name.upper(), round(metric_val, 4)])

    # Store 30-day demand forecast in DuckDB
    conn.execute("DELETE FROM forecasting.demand_forecasts;")
    for _, row in forward_forecast_df.iterrows():
        conn.execute("""
            INSERT INTO forecasting.demand_forecasts (
                forecast_id, model_id, forecast_date, horizon_step, hub_id, hub_name,
                daily_capacity, forecast_order_volume, lower_bound_95, upper_bound_95, is_synthetic_simulated
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            f"fdem-{uuid.uuid4().hex[:8]}",
            mod1_id,
            row["forecast_date"],
            row["horizon_step"],
            row["hub_id"],
            row["hub_name"],
            int(row["daily_capacity"]),
            float(row["forecast_order_volume"]),
            float(row["lower_bound_95"]),
            float(row["upper_bound_95"]),
            True
        ])

    # ----------------------------------------------------
    # Model 2: Hub Workload & Capacity Forecaster
    # ----------------------------------------------------
    logger.info("--- [2/3] Executing Hub Workload & Bottleneck Forecaster ---")
    workload_forecaster = HubWorkloadForecaster(bottleneck_threshold_pct=85.0)
    workload_df = workload_forecaster.forecast_workload(forward_forecast_df)
    workload_artifact = workload_forecaster.save("models/artifacts/hub_workload_forecaster.joblib")

    mod2_id = f"mod-fore-workload-{uuid.uuid4().hex[:8]}"
    conn.execute("""
        INSERT INTO forecasting.model_registry (
            model_id, model_name, version, algorithm, forecast_horizon,
            training_records, hyperparameters, artifact_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        mod2_id,
        "hub_workload_forecaster",
        "1.0.0",
        "DeterministicCapacityFlowModel",
        "30-day",
        len(forward_forecast_df),
        json.dumps({"bottleneck_threshold_pct": 85.0}),
        workload_artifact,
        True
    ])

    conn.execute("DELETE FROM forecasting.hub_workload_forecasts;")
    for _, row in workload_df.iterrows():
        conn.execute("""
            INSERT INTO forecasting.hub_workload_forecasts (
                workload_id, forecast_date, horizon_step, hub_id, hub_name,
                forecast_order_volume, forecast_dispatched_volume, projected_daily_backlog,
                capacity_utilization_pct, is_bottleneck_risk, risk_level
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            f"fwk-{uuid.uuid4().hex[:8]}",
            row["forecast_date"],
            row["horizon_step"],
            row["hub_id"],
            row["hub_name"],
            float(row["forecast_order_volume"]),
            float(row["forecast_dispatched_volume"]),
            float(row["projected_daily_backlog"]),
            float(row["capacity_utilization_pct"]),
            bool(row["is_bottleneck_risk"]),
            row["risk_level"]
        ])

    # ----------------------------------------------------
    # Model 3: Fleet Requirement Forecaster
    # ----------------------------------------------------
    logger.info("--- [3/3] Executing Fleet Requirement & Vehicle Allocation Forecaster ---")
    fleet_forecaster = FleetRequirementForecaster()
    fleet_df = fleet_forecaster.forecast_fleet_needs(forward_forecast_df)
    fleet_artifact = fleet_forecaster.save("models/artifacts/fleet_requirement_forecaster.joblib")

    mod3_id = f"mod-fore-fleet-{uuid.uuid4().hex[:8]}"
    conn.execute("""
        INSERT INTO forecasting.model_registry (
            model_id, model_name, version, algorithm, forecast_horizon,
            training_records, hyperparameters, artifact_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        mod3_id,
        "fleet_requirement_forecaster",
        "1.0.0",
        "PayloadDemandConstraintModel",
        "30-day",
        len(fleet_df),
        json.dumps({"active_fleet_baseline": 33}),
        fleet_artifact,
        True
    ])

    conn.execute("DELETE FROM forecasting.fleet_requirement_forecasts;")
    for _, row in fleet_df.iterrows():
        conn.execute("""
            INSERT INTO forecasting.fleet_requirement_forecasts (
                fleet_req_id, forecast_date, hub_name, vehicle_type,
                projected_parcels, vehicles_required, active_fleet_baseline,
                surplus_or_deficit, is_fleet_deficit, utilization_rate_pct
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
        """, [
            f"fflt-{uuid.uuid4().hex[:8]}",
            row["forecast_date"],
            row["hub_name"],
            row["vehicle_type"],
            float(row["projected_parcels"]),
            int(row["vehicles_required"]),
            int(row["active_fleet_baseline"]),
            int(row["surplus_or_deficit"]),
            bool(row["is_fleet_deficit"]),
            float(row["utilization_rate_pct"])
        ])

    conn.close()

    summary = {
        "status": "SUCCESS",
        "models_trained": 3,
        "demand_test_metrics": test_metrics,
        "forward_horizons": ["7-day", "30-day"],
        "forecast_records_generated": {
            "demand_forecasts": len(forward_forecast_df),
            "hub_workload_forecasts": len(workload_df),
            "fleet_requirement_forecasts": len(fleet_df)
        },
        "artifacts": [demand_artifact, workload_artifact, fleet_artifact]
    }
    logger.info("Phase 9 Forecasting Engineering Pipeline completed successfully.")
    return summary


if __name__ == "__main__":
    result = run_forecasting_pipeline()
    print(json.dumps(result, indent=2))
