"""
Batch ETL Pipeline Unit & Idempotency Tests
LogiTrack Intelligence — Phase 4

Tests extraction hashing, date standardization, data quality quarantine routing,
and idempotent database loading.
"""

import pytest
import pandas as pd
from datetime import datetime
from logitrack.ingestion.clean import standardize_date_series
from logitrack.ingestion.extract import extract_source_data
from logitrack.ingestion.quality_gate import DataQualityGate
from logitrack.ingestion.pipeline import run_batch_pipeline
from logitrack.storage.duckdb_manager import DuckDBManager


def test_source_data_extraction():
    extracted = extract_source_data()
    assert set(extracted.keys()) == {"hubs", "drivers", "vehicles", "orders"}
    for name, (df, meta) in extracted.items():
        assert len(df) > 0
        assert "file_hash_sha256" in meta
        assert len(meta["file_hash_sha256"]) == 64  # Valid SHA256 length


def test_standardize_mixed_date_formats():
    sample_dates = pd.Series(["25-10-2024", "5/7/2024", "1-2-2023", None])
    standardized = standardize_date_series(sample_dates)
    assert standardized[0] == "2024-10-25"
    assert standardized[1] == "2024-07-05"
    assert standardized[2] == "2023-02-01"
    assert pd.isnull(standardized[3])


def test_data_quality_gate_quarantine_routing(tmp_path):
    gate = DataQualityGate(batch_id="test-run")
    
    # Create test orders with 1 valid and 2 invalid records
    mock_orders = pd.DataFrame([
        {"order_id": 1, "customer_satisfaction_score": 4, "hub_name": "Dallas Main Hub"},
        {"order_id": None, "customer_satisfaction_score": 5, "hub_name": "Dallas Main Hub"}, # Invalid PK
        {"order_id": 3, "customer_satisfaction_score": 9, "hub_name": "Dallas Main Hub"},    # Out of bounds score
    ])
    
    valid, rejected = gate.validate_and_filter("orders", mock_orders, "order_id")
    assert len(valid) == 1
    assert len(rejected) == 2
    assert "DQ-001" in rejected.iloc[0]["rejection_reason"]
    assert "DQ-009" in rejected.iloc[1]["rejection_reason"]


def test_batch_pipeline_idempotency():
    # Run pipeline first time
    audit1 = run_batch_pipeline()
    assert audit1["status"] == "SUCCESS"
    assert audit1["loaded_rows"] == 28085
    
    # Run pipeline second time (must not duplicate records in staging)
    audit2 = run_batch_pipeline()
    assert audit2["status"] == "SUCCESS"
    assert audit2["loaded_rows"] == 28085
    
    manager = DuckDBManager()
    orders_cnt = manager.query("SELECT COUNT(*) as count FROM staging.stg_orders")["count"][0]
    manager.close()
    
    assert orders_cnt == 27979, f"Expected 27,979 orders after multiple runs, found {orders_cnt}"
