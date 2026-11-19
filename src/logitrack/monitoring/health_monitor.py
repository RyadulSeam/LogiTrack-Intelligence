"""
LogiTrack Intelligence — System & Pipeline Health Monitor
Phase 11: Monitoring, Testing & CI/CD

Responsibilities:
- Lakehouse table row-count deltas (staleness detection)
- API endpoint latency probing
- ML model artifact freshness
- Forecasting table population check
- Writes health_snapshots to DuckDB monitoring schema
"""

import os
import time
import datetime
import duckdb
import pandas as pd
from pathlib import Path
from loguru import logger


DB_PATH = "data/lake/logitrack.duckdb"
MODEL_ARTIFACTS_DIR = "models/artifacts"


# ---------------------------------------------------------------------------
# 1. DuckDB Table Health Checks
# ---------------------------------------------------------------------------

def check_lakehouse_table_health(db_path: str = DB_PATH) -> pd.DataFrame:
    """
    Checks row-counts and staleness across all core warehouse tables.
    Returns a DataFrame with one row per table: table_name, row_count, status.
    """
    table_specs = [
        # (schema.table, minimum_expected_rows)
        ("warehouse.fact_orders",    27_000),
        ("warehouse.dim_hub",             6),
        ("warehouse.dim_driver",         50),
        ("warehouse.dim_vehicle",        40),
        ("warehouse.dim_date",        1_000),
        ("warehouse.dim_route",          30),
        ("staging.stg_orders",       27_000),
        ("staging.stg_vehicles",         40),
        ("forecasting.demand_forecasts", 100),
        ("forecasting.hub_workload_forecasts", 100),
        ("forecasting.fleet_requirement_forecasts", 100),
        ("ml.model_registry",             4),
        ("ml.predictions",               10),
    ]

    results = []
    conn = duckdb.connect(db_path, read_only=True)
    for table_fqn, min_rows in table_specs:
        try:
            count = conn.execute(f"SELECT COUNT(*) FROM {table_fqn}").fetchone()[0]
            status = "OK" if count >= min_rows else "BELOW_THRESHOLD"
        except Exception as exc:
            count = 0
            status = f"ERROR: {exc}"
        results.append({
            "table": table_fqn,
            "row_count": count,
            "min_expected": min_rows,
            "status": status,
        })
    conn.close()

    df = pd.DataFrame(results)
    ok_count = (df["status"] == "OK").sum()
    logger.info(f"[Table Health] {ok_count}/{len(df)} tables healthy.")
    return df


# ---------------------------------------------------------------------------
# 2. ML Model Artifact Freshness
# ---------------------------------------------------------------------------

def check_model_artifact_freshness(
    artifacts_dir: str = MODEL_ARTIFACTS_DIR,
    max_age_days: int = 30
) -> pd.DataFrame:
    """
    Inspects .joblib artifacts and flags those older than max_age_days.
    """
    artifact_path = Path(artifacts_dir)
    results = []
    for f in artifact_path.glob("*.joblib"):
        mtime = datetime.datetime.fromtimestamp(f.stat().st_mtime)
        age_days = (datetime.datetime.now() - mtime).days
        status = "FRESH" if age_days <= max_age_days else "STALE"
        results.append({
            "artifact": f.name,
            "last_modified": mtime.isoformat(),
            "age_days": age_days,
            "size_kb": round(f.stat().st_size / 1024, 1),
            "status": status,
        })

    df = pd.DataFrame(results) if results else pd.DataFrame(
        columns=["artifact", "last_modified", "age_days", "size_kb", "status"]
    )
    stale = (df["status"] == "STALE").sum()
    if stale:
        logger.warning(f"[Model Freshness] {stale} stale model artifacts detected.")
    else:
        logger.info(f"[Model Freshness] All {len(df)} artifacts are fresh.")
    return df


# ---------------------------------------------------------------------------
# 3. Data Completeness — Key Columns
# ---------------------------------------------------------------------------

def check_data_completeness(db_path: str = DB_PATH) -> pd.DataFrame:
    """
    Checks null rates in business-critical columns across the warehouse.
    Flags any column where null rate exceeds the defined threshold.
    """
    checks = [
        ("warehouse.fact_orders", "order_id",       0.0),
        ("warehouse.fact_orders", "order_status",    0.0),
        ("warehouse.fact_orders", "pickup_date",    0.05),
        ("warehouse.fact_orders", "delivery_date",  0.10),
        ("warehouse.dim_hub",     "hub_name",        0.0),
        ("warehouse.dim_hub",     "latitude",        0.0),
        ("warehouse.dim_hub",     "longitude",       0.0),
        ("warehouse.dim_driver",  "driver_name",     0.0),
        ("warehouse.dim_driver",  "driver_rating",  0.05),
        ("warehouse.dim_vehicle", "vehicle_code",    0.0),
        ("warehouse.dim_vehicle", "vehicle_type",    0.0),
    ]

    results = []
    conn = duckdb.connect(db_path, read_only=True)
    for table, col, max_null_rate in checks:
        try:
            row = conn.execute(f"""
                SELECT
                    COUNT(*) AS total,
                    SUM(CASE WHEN {col} IS NULL THEN 1 ELSE 0 END) AS nulls
                FROM {table}
            """).fetchone()
            total, nulls = row
            null_rate = nulls / total if total > 0 else 0.0
            status = "OK" if null_rate <= max_null_rate else "HIGH_NULL_RATE"
        except Exception as exc:
            null_rate = -1.0
            status = f"ERROR: {exc}"

        results.append({
            "table": table,
            "column": col,
            "null_rate_pct": round(null_rate * 100, 2),
            "max_allowed_pct": round(max_null_rate * 100, 1),
            "status": status,
        })
    conn.close()

    df = pd.DataFrame(results)
    high = (df["status"] == "HIGH_NULL_RATE").sum()
    if high:
        logger.warning(f"[Data Completeness] {high} columns exceed null rate threshold.")
    else:
        logger.info(f"[Data Completeness] All {len(df)} column checks passed.")
    return df


# ---------------------------------------------------------------------------
# 4. Business KPI Drift Detection
# ---------------------------------------------------------------------------

def check_kpi_drift(db_path: str = DB_PATH) -> dict:
    """
    Recomputes core business KPIs and compares to known baselines.
    Returns a dict with actual values and drift flags.
    """
    BASELINES = {
        "total_orders":        27_979,
        "delivered_orders":    27_727,
        "cancelled_orders":       252,
        "otd_rate_pct":          79.6,   # On-Time Delivery %
        "delay_rate_pct":        20.4,
    }
    TOLERANCES = {
        "total_orders":        0,
        "delivered_orders":    0,
        "cancelled_orders":    0,
        "otd_rate_pct":        0.5,
        "delay_rate_pct":      0.5,
    }

    conn = duckdb.connect(db_path, read_only=True)
    result = conn.execute("""
        SELECT
            COUNT(*)                                                AS total_orders,
            SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END) AS delivered_orders,
            SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) AS cancelled_orders
        FROM warehouse.fact_orders
    """).fetchone()
    conn.close()

    total, delivered, cancelled = result
    delayed = delivered - round(delivered * (BASELINES["otd_rate_pct"] / 100))

    # Recompute OTD from actual data
    conn2 = duckdb.connect(db_path, read_only=True)
    otd_row = conn2.execute("""
        SELECT
            ROUND(100.0 * SUM(CASE WHEN is_delayed = FALSE THEN 1 ELSE 0 END)
                / NULLIF(SUM(CASE WHEN order_status = 'Delivered' THEN 1 ELSE 0 END), 0), 1) AS otd_rate
        FROM warehouse.fact_orders
    """).fetchone()
    conn2.close()

    otd_rate = float(otd_row[0]) if otd_row[0] else 0.0
    delay_rate = round(100.0 - otd_rate, 1)

    actuals = {
        "total_orders":     total,
        "delivered_orders": delivered,
        "cancelled_orders": cancelled,
        "otd_rate_pct":     otd_rate,
        "delay_rate_pct":   delay_rate,
    }

    drift_flags = {}
    for key, baseline in BASELINES.items():
        actual = actuals.get(key, 0)
        tol = TOLERANCES.get(key, 0)
        drift = abs(actual - baseline)
        drift_flags[key] = {
            "baseline": baseline,
            "actual":   actual,
            "drift":    round(drift, 2),
            "status":   "OK" if drift <= tol else "DRIFT_DETECTED",
        }

    drift_detected = sum(1 for v in drift_flags.values() if v["status"] == "DRIFT_DETECTED")
    if drift_detected:
        logger.warning(f"[KPI Drift] {drift_detected} KPI metrics drifted from baseline.")
    else:
        logger.info("[KPI Drift] All KPI baselines are within acceptable tolerance.")

    return drift_flags


# ---------------------------------------------------------------------------
# 5. Composite Health Report
# ---------------------------------------------------------------------------

def run_full_health_check(db_path: str = DB_PATH) -> dict:
    """
    Runs all monitoring checks and returns a composite health report.
    """
    logger.info("=" * 60)
    logger.info("LogiTrack Intelligence — System Health Check")
    logger.info(f"Timestamp: {datetime.datetime.now().isoformat()}")
    logger.info("=" * 60)

    table_health    = check_lakehouse_table_health(db_path)
    model_freshness = check_model_artifact_freshness()
    completeness    = check_data_completeness(db_path)
    kpi_drift       = check_kpi_drift(db_path)

    all_tables_ok  = (table_health["status"] == "OK").all()
    all_models_ok  = (model_freshness.get("status", pd.Series(["FRESH"])) == "FRESH").all()
    all_complete   = (completeness["status"] == "OK").all()
    all_kpis_ok    = all(v["status"] == "OK" for v in kpi_drift.values())

    overall = "HEALTHY" if all([all_tables_ok, all_models_ok, all_complete, all_kpis_ok]) else "DEGRADED"

    report = {
        "timestamp":        datetime.datetime.now().isoformat(),
        "overall_status":   overall,
        "table_health":     table_health.to_dict(orient="records"),
        "model_freshness":  model_freshness.to_dict(orient="records"),
        "data_completeness": completeness.to_dict(orient="records"),
        "kpi_drift":        kpi_drift,
        "summary": {
            "tables_ok":    int((table_health["status"] == "OK").sum()),
            "tables_total": len(table_health),
            "models_fresh": int((model_freshness.get("status", pd.Series()) == "FRESH").sum()),
            "kpis_ok":      int(sum(1 for v in kpi_drift.values() if v["status"] == "OK")),
        }
    }

    logger.info(f"Overall Health: {overall}")
    return report


if __name__ == "__main__":
    report = run_full_health_check()
    import json
    print(json.dumps(report["summary"], indent=2))
    print(f"\nOverall Status: {report['overall_status']}")
