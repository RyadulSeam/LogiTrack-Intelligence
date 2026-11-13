"""
Batch ETL Master Pipeline Orchestrator
LogiTrack Intelligence — Phase 4

Coordinates end-to-end extraction, cleaning, transformation, data quality gates,
quarantine routing, and idempotent loading into Bronze and Silver layers.
"""

import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from loguru import logger

from logitrack.ingestion.extract import extract_source_data
from logitrack.ingestion.clean import clean_hubs, clean_drivers, clean_vehicles, clean_orders
from logitrack.ingestion.transform import (
    transform_hubs_to_staging,
    transform_drivers_to_staging,
    transform_vehicles_to_staging,
    transform_orders_to_staging
)
from logitrack.ingestion.quality_gate import DataQualityGate
from logitrack.ingestion.load import load_to_duckdb, load_to_postgres
from logitrack.ingestion.audit import record_pipeline_audit

load_dotenv()


def run_batch_pipeline() -> dict:
    run_id = f"run-{uuid.uuid4().hex[:8]}"
    start_time = datetime.now()
    logger.info(f"=== Starting LogiTrack Batch Pipeline [{run_id}] ===")
    
    total_source_rows = 0
    total_loaded_rows = 0
    total_quarantined_rows = 0

    try:
        # 1. Extraction & Checksums
        extracted = extract_source_data()
        
        # Prepare Bronze (Raw) DataFrames with lineage metadata
        raw_tables = {}
        for entity, (df, meta) in extracted.items():
            total_source_rows += len(df)
            raw_df = df.copy()
            raw_df["ingestion_batch_id"] = run_id
            raw_df["source_file"] = meta["source_file"]
            raw_df["data_origin"] = "source: original"
            raw_df["loaded_at"] = start_time
            raw_tables[entity] = raw_df

        # 2. Cleaning & Standardization
        logger.info("Cleaning and standardizing dates and strings...")
        cleaned_hubs = clean_hubs(extracted["hubs"][0])
        cleaned_drivers = clean_drivers(extracted["drivers"][0])
        cleaned_vehicles = clean_vehicles(extracted["vehicles"][0])
        cleaned_orders = clean_orders(extracted["orders"][0])

        # 3. Transformation to Canonical Staging Schemas
        logger.info("Transforming datasets to canonical Silver staging schemas...")
        stg_hubs = transform_hubs_to_staging(cleaned_hubs, run_id)
        stg_drivers = transform_drivers_to_staging(cleaned_drivers, run_id)
        stg_vehicles = transform_vehicles_to_staging(cleaned_vehicles, run_id)
        stg_orders = transform_orders_to_staging(cleaned_orders, run_id)

        # 4. Data Quality Gate & Quarantine Filtering
        logger.info("Enforcing Data Quality Gates (DQ-001 through DQ-010)...")
        gate = DataQualityGate(batch_id=run_id)
        
        valid_hubs, rej_hubs = gate.validate_and_filter("hubs", stg_hubs, "hub_id")
        valid_drivers, rej_drivers = gate.validate_and_filter("drivers", stg_drivers, "driver_id")
        valid_vehicles, rej_vehicles = gate.validate_and_filter("vehicles", stg_vehicles, "vehicle_id")
        
        fk_checks = {
            "driver_id": set(valid_drivers["driver_id"]),
            "hub_name": set(valid_hubs["hub_name"]),
            "vehicle_code": set(valid_vehicles["vehicle_code"])
        }
        valid_orders, rej_orders = gate.validate_and_filter("orders", stg_orders, "order_id", fk_checks)

        staging_tables = {
            "hubs": valid_hubs,
            "drivers": valid_drivers,
            "vehicles": valid_vehicles,
            "orders": valid_orders
        }

        total_loaded_rows = sum(len(df) for df in staging_tables.values())
        total_quarantined_rows = len(rej_hubs) + len(rej_drivers) + len(rej_vehicles) + len(rej_orders)

        # 5. Idempotent Loading
        logger.info("Loading into local DuckDB lakehouse...")
        load_to_duckdb(raw_tables, staging_tables)

        db_url = os.getenv("DATABASE_URL")
        if db_url and "user:password" not in db_url:
            logger.info("Active Neon DATABASE_URL found. Loading into cloud PostgreSQL...")
            try:
                load_to_postgres(raw_tables, staging_tables, db_url)
            except Exception as e:
                logger.error(f"PostgreSQL load encountered error: {e}")

        # 6. Pipeline Audit Log
        end_time = datetime.now()
        duration_sec = round((end_time - start_time).total_seconds(), 2)
        
        audit_entry = {
            "run_id": run_id,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": duration_sec,
            "source_rows": total_source_rows,
            "loaded_rows": total_loaded_rows,
            "quarantined_rows": total_quarantined_rows,
            "status": "SUCCESS"
        }
        record_pipeline_audit(audit_entry)
        
        logger.success(f"Batch Pipeline [{run_id}] completed in {duration_sec}s! (Loaded: {total_loaded_rows:,} rows)")
        return audit_entry

    except Exception as e:
        end_time = datetime.now()
        audit_entry = {
            "run_id": run_id,
            "start_time": start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": end_time.strftime("%Y-%m-%d %H:%M:%S"),
            "duration_seconds": round((end_time - start_time).total_seconds(), 2),
            "source_rows": total_source_rows,
            "loaded_rows": 0,
            "quarantined_rows": 0,
            "status": f"FAILED: {str(e)}"
        }
        record_pipeline_audit(audit_entry)
        logger.error(f"Batch pipeline failed: {e}")
        raise


if __name__ == "__main__":
    run_batch_pipeline()
