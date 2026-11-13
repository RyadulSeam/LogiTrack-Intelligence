"""
Data Quality & Integrity Test Suite (Phase 1)
LogiTrack Intelligence

Validates schema, nullity, primary keys, referential integrity, and business logic
across raw source datasets in data/source/.
"""

import pytest
import pandas as pd
from pathlib import Path

SOURCE_DIR = Path("data/source")


@pytest.fixture(scope="module")
def datasets():
    return {
        "hubs": pd.read_csv(SOURCE_DIR / "Hubs.csv"),
        "drivers": pd.read_csv(SOURCE_DIR / "Drivers.csv"),
        "vehicles": pd.read_csv(SOURCE_DIR / "Vehicles.csv"),
        "orders": pd.read_csv(SOURCE_DIR / "Orders.csv"),
    }


# -------------------------------------------------------------
# DQ-001: Primary Key Uniqueness
# -------------------------------------------------------------
def test_primary_key_uniqueness(datasets):
    assert datasets["hubs"]["Hub ID"].is_unique, "Duplicate Hub ID found"
    assert datasets["drivers"]["DriverID"].is_unique, "Duplicate DriverID found"
    assert datasets["vehicles"]["Vehicle ID"].is_unique, "Duplicate Vehicle ID found"
    assert datasets["orders"]["Order ID"].is_unique, "Duplicate Order ID found"


# -------------------------------------------------------------
# DQ-002: Referential Integrity - Hubs
# -------------------------------------------------------------
def test_orders_hub_reference_validity(datasets):
    valid_hubs = set(datasets["hubs"]["HubName"])
    order_hubs = set(datasets["orders"]["Hub Name"].unique())
    orphans = order_hubs - valid_hubs
    assert len(orphans) == 0, f"Found orphaned hubs in Orders: {orphans}"


# -------------------------------------------------------------
# DQ-003: Referential Integrity - Drivers
# -------------------------------------------------------------
def test_orders_driver_id_reference_validity(datasets):
    valid_driver_ids = set(datasets["drivers"]["DriverID"])
    order_driver_ids = set(datasets["orders"]["Driver ID"].unique())
    orphans = order_driver_ids - valid_driver_ids
    assert len(orphans) == 0, f"Found orphaned Driver IDs in Orders: {orphans}"


# -------------------------------------------------------------
# DQ-004: Referential Integrity - Vehicles
# -------------------------------------------------------------
def test_orders_vehicle_code_reference_validity(datasets):
    valid_vehicle_codes = set(datasets["vehicles"]["Vehicle Code"])
    order_vehicle_codes = set(datasets["orders"]["Vehicle Name"].unique())
    orphans = order_vehicle_codes - valid_vehicle_codes
    assert len(orphans) == 0, f"Found orphaned Vehicle Codes in Orders: {orphans}"


# -------------------------------------------------------------
# DQ-005: Order Cancellation Consistency
# -------------------------------------------------------------
def test_cancelled_orders_consistency(datasets):
    orders = datasets["orders"]
    cancelled = orders[orders["Order Status"] == "Cancelled"]
    assert len(cancelled) > 0, "No cancelled orders found"
    # All cancelled orders should have null Actual Delivery Date & Delivery Time Hours
    assert cancelled["Actual Delivery Date"].isnull().all(), "Cancelled orders must have null Actual Delivery Date"
    assert cancelled["Delivery Time Hours"].isnull().all(), "Cancelled orders must have null Delivery Time Hours"


# -------------------------------------------------------------
# DQ-006: Delay Consistency
# -------------------------------------------------------------
def test_delay_flag_and_reason_consistency(datasets):
    orders = datasets["orders"]
    delayed = orders[orders["Is Delayed"] == True]
    not_delayed = orders[orders["Is Delayed"] == False]
    
    # Delayed orders must have a reason
    assert delayed["Delay Reason"].notnull().all(), "Every delayed order must have a Delay Reason"
    # Non-delayed orders must not have a reason
    assert not_delayed["Delay Reason"].isnull().all(), "Non-delayed orders must have null Delay Reason"


# -------------------------------------------------------------
# DQ-007: Valid Rating & Score Ranges
# -------------------------------------------------------------
def test_score_ranges(datasets):
    drivers = datasets["drivers"]
    orders = datasets["orders"]
    
    assert drivers["Performance Rating"].between(1, 5).all(), "Driver rating out of bounds [1, 5]"
    assert orders["Customer Satisfaction Score"].between(1, 5).all(), "CSAT score out of bounds [1, 5]"
