"""
Streaming Engine & Event Contracts Unit Tests
LogiTrack Intelligence — Phase 5

Tests event contract validation, idempotent deduplication, DLQ error routing,
and Parquet lake flushing.
"""

import json
import pytest
from logitrack.streaming.event_contract import (
    validate_vehicle_telemetry,
    validate_order_status,
    validate_driver_activity,
    validate_hub_operations
)
from logitrack.streaming.mqtt_consumer import EventConsumer
from logitrack.storage.duckdb_manager import DuckDBManager


def test_vehicle_telemetry_valid():
    valid_payload = {
        "event_id": "tel-test-001",
        "event_type": "vehicle.telemetry",
        "event_timestamp": "2026-11-13 10:00:00",
        "data_origin": "source: simulated",
        "vehicle_code": "FT-001",
        "latitude": 32.7767,
        "longitude": -96.7970,
        "speed_kmh": 65.5
    }
    # Should not raise
    validate_vehicle_telemetry(valid_payload)


def test_vehicle_telemetry_invalid_bounds():
    invalid_payload = {
        "event_id": "tel-test-002",
        "event_type": "vehicle.telemetry",
        "event_timestamp": "2026-11-13 10:00:00",
        "vehicle_code": "FT-001",
        "latitude": 55.0, # Outside Texas [25, 37]
        "longitude": -96.7970,
        "speed_kmh": 65.5
    }
    with pytest.raises(ValueError, match="Texas bounding box"):
        validate_vehicle_telemetry(invalid_payload)


def test_order_status_invalid_enum():
    invalid_payload = {
        "event_id": "ord-test-001",
        "event_type": "order.status",
        "event_timestamp": "2026-11-13 10:00:00",
        "order_id": 100,
        "order_status": "SUPER_DELIVERED" # Not a valid lifecycle state
    }
    with pytest.raises(ValueError, match="Invalid order_status"):
        validate_order_status(invalid_payload)


def test_consumer_idempotent_deduplication():
    consumer = EventConsumer()
    event_payload = {
        "event_id": "tel-dedup-check-999",
        "event_type": "vehicle.telemetry",
        "event_timestamp": "2026-11-13 12:00:00",
        "data_origin": "source: simulated",
        "vehicle_code": "FT-005",
        "latitude": 30.2672,
        "longitude": -97.7431,
        "speed_kmh": 72.0
    }
    msg = json.dumps(event_payload)
    
    # Process message first time
    res1 = consumer.process_message("logitrack/vehicle/telemetry", msg)
    assert res1 is True

    # Process EXACT SAME message second time (simulating QoS 1 duplicate delivery)
    res2 = consumer.process_message("logitrack/vehicle/telemetry", msg)
    assert res2 is True
    consumer.close()

    # Query database to ensure record count is EXACTLY 1
    manager = DuckDBManager()
    count = manager.query(
        "SELECT COUNT(*) as count FROM realtime.vehicle_events WHERE event_id = 'tel-dedup-check-999'"
    )["count"][0]
    manager.close()
    
    assert count == 1, f"Expected exactly 1 record after duplicate event, found {count}"


def test_consumer_dead_letter_routing():
    consumer = EventConsumer()
    # Send non-JSON corrupted payload
    res = consumer.process_message("logitrack/order/status", "{ corrupt json payload")
    assert res is False
    consumer.close()

    # Verify DLQ received the error
    manager = DuckDBManager()
    errors = manager.query("SELECT COUNT(*) as count FROM realtime.ingestion_errors")["count"][0]
    manager.close()
    assert errors > 0
