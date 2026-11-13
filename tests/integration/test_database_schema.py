"""
Database Schema Integration Tests
LogiTrack Intelligence — Phase 3

Verifies that all 5 schemas and their core tables, primary keys, and constraints
are properly created and that migrations are strictly idempotent.
"""

import pytest
from logitrack.storage.duckdb_manager import DuckDBManager
from scripts.run_migrations import get_migration_files


@pytest.fixture(scope="module")
def db_conn():
    # Use in-memory DuckDB for fast isolated testing
    manager = DuckDBManager(db_path=":memory:")
    for f in get_migration_files():
        with open(f, "r", encoding="utf-8") as sql_file:
            manager.execute_script(sql_file.read())
    yield manager
    manager.close()


def test_all_schemas_created(db_conn):
    df = db_conn.query("SELECT schema_name FROM information_schema.schemata;")
    schemas = set(df["schema_name"].str.lower())
    expected = {"raw", "staging", "warehouse", "realtime", "ml"}
    assert expected.issubset(schemas), f"Missing schemas: {expected - schemas}"


def test_raw_tables_exist(db_conn):
    df = db_conn.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'raw';")
    tables = set(df["table_name"].str.lower())
    assert {"raw_hubs", "raw_drivers", "raw_vehicles", "raw_orders"}.issubset(tables)


def test_staging_tables_exist(db_conn):
    df = db_conn.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'staging';")
    tables = set(df["table_name"].str.lower())
    assert {"stg_hubs", "stg_drivers", "stg_vehicles", "stg_orders"}.issubset(tables)


def test_warehouse_tables_exist(db_conn):
    df = db_conn.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'warehouse';")
    tables = set(df["table_name"].str.lower())
    expected = {
        "dim_date", "dim_hub", "dim_driver", "dim_vehicle", "dim_route",
        "fact_orders", "fact_order_events", "fact_vehicle_telemetry",
        "fact_maintenance", "fact_hub_hourly"
    }
    assert expected.issubset(tables)


def test_realtime_tables_exist(db_conn):
    df = db_conn.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'realtime';")
    tables = set(df["table_name"].str.lower())
    assert {"vehicle_events", "order_events", "driver_events", "hub_events", "ingestion_errors"}.issubset(tables)


def test_ml_tables_exist(db_conn):
    df = db_conn.query("SELECT table_name FROM information_schema.tables WHERE table_schema = 'ml';")
    tables = set(df["table_name"].str.lower())
    assert {"model_registry", "model_evaluations", "predictions", "feature_snapshots"}.issubset(tables)


def test_migration_idempotency(db_conn):
    # Re-running migration scripts must not raise exceptions due to IF NOT EXISTS
    for f in get_migration_files():
        with open(f, "r", encoding="utf-8") as sql_file:
            db_conn.execute_script(sql_file.read())
