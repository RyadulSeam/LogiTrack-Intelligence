"""
Streaming Event Contract Validators
LogiTrack Intelligence — Phase 5

Validates incoming MQTT event payloads against the authoritative event schemas
specified in docs/09_event_contracts.md.
"""

from typing import Dict, Any


def validate_vehicle_telemetry(payload: Dict[str, Any]):
    required = ["event_id", "event_type", "event_timestamp", "vehicle_code", "latitude", "longitude", "speed_kmh"]
    for field in required:
        if field not in payload or payload[field] is None:
            raise ValueError(f"Missing required field '{field}' in vehicle.telemetry event")
            
    lat = float(payload["latitude"])
    lon = float(payload["longitude"])
    if not (25.0 <= lat <= 37.0):
        raise ValueError(f"Latitude {lat} out of Texas bounding box [25.0, 37.0]")
    if not (-107.0 <= lon <= -93.0):
        raise ValueError(f"Longitude {lon} out of Texas bounding box [-107.0, -93.0]")


def validate_order_status(payload: Dict[str, Any]):
    required = ["event_id", "event_type", "event_timestamp", "order_id", "order_status"]
    for field in required:
        if field not in payload or payload[field] is None:
            raise ValueError(f"Missing required field '{field}' in order.status event")
            
    valid_statuses = {
        "ORDER_CREATED", "HUB_RECEIVED", "PROCESSING_STARTED",
        "PROCESSING_COMPLETED", "DISPATCHED", "IN_TRANSIT",
        "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"
    }
    status = payload["order_status"]
    if status not in valid_statuses:
        raise ValueError(f"Invalid order_status '{status}'. Must be one of {valid_statuses}")


def validate_driver_activity(payload: Dict[str, Any]):
    required = ["event_id", "event_type", "event_timestamp", "driver_id", "activity_type"]
    for field in required:
        if field not in payload or payload[field] is None:
            raise ValueError(f"Missing required field '{field}' in driver.activity event")
            
    valid_activities = {"Shift Start", "Break", "Active Assignment", "Shift End"}
    act = payload["activity_type"]
    if act not in valid_activities:
        raise ValueError(f"Invalid activity_type '{act}'. Must be one of {valid_activities}")


def validate_hub_operations(payload: Dict[str, Any]):
    required = ["event_id", "event_type", "event_timestamp", "hub_name", "active_backlog"]
    for field in required:
        if field not in payload or payload[field] is None:
            raise ValueError(f"Missing required field '{field}' in hub.operations event")
            
    if int(payload["active_backlog"]) < 0:
        raise ValueError("active_backlog cannot be negative")
