"""
Warehouse Star Schema & Marts Test Suite
LogiTrack Intelligence — Phase 6

Validates grain, key constraints, referential integrity, and business logic
across the Gold warehouse layer.
"""

import pytest
from logitrack.storage.duckdb_manager import DuckDBManager
from src.logitrack.transformation.warehouse_builder import build_warehouse_tables


@pytest.fixture(scope="module")
def populated_warehouse():
    build_warehouse_tables()
    manager = DuckDBManager()
    yield manager
    manager.close()


def test_fact_orders_grain_and_rowcount(populated_warehouse):
    df = populated_warehouse.query("SELECT COUNT(*) as count FROM warehouse.fact_orders;")
    assert df["count"][0] == 27979, f"Expected 27,979 orders in fact_orders, got {df['count'][0]}"


def test_fact_orders_referential_integrity(populated_warehouse):
    # Ensure no orphan foreign keys
    df = populated_warehouse.query("""
        SELECT
            SUM(CASE WHEN hub_key IS NULL THEN 1 ELSE 0 END) as null_hubs,
            SUM(CASE WHEN driver_key IS NULL THEN 1 ELSE 0 END) as null_drivers,
            SUM(CASE WHEN vehicle_key IS NULL THEN 1 ELSE 0 END) as null_vehicles
        FROM warehouse.fact_orders;
    """)
    assert df["null_hubs"][0] == 0, "Found null hub_keys in fact_orders"
    assert df["null_drivers"][0] == 0, "Found null driver_keys in fact_orders"
    assert df["null_vehicles"][0] == 0, "Found null vehicle_keys in fact_orders"


def test_dim_date_coverage(populated_warehouse):
    df = populated_warehouse.query("""
        SELECT MIN(full_date) as min_date, MAX(full_date) as max_date, COUNT(*) as count
        FROM warehouse.dim_date;
    """)
    assert str(df["min_date"][0]).startswith("2023-01-01")
    assert str(df["max_date"][0]).startswith("2026-12-31")
    assert df["count"][0] == 1461  # 365 + 366 (leap year 2024) + 365 + 365


def test_dim_hub_texas_coordinates(populated_warehouse):
    df = populated_warehouse.query("SELECT hub_name, latitude, longitude FROM warehouse.dim_hub;")
    assert len(df) == 6
    assert df["latitude"].notnull().all()
    assert df["longitude"].notnull().all()
    assert (df["latitude"] > 25.0).all() and (df["latitude"] < 37.0).all()


def test_dim_route_connectivity(populated_warehouse):
    df = populated_warehouse.query("SELECT COUNT(*) as count, MIN(distance_km) as min_dist FROM warehouse.dim_route;")
    assert df["count"][0] == 36  # 6 x 6 hub combinations
    assert df["min_dist"][0] > 0
