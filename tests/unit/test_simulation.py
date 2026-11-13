"""
Simulation Engine Unit Tests
LogiTrack Intelligence — Phase 2

Tests seed determinism, referential integrity, event timestamp monotonicity,
and geospatial sanity across synthetic generation modules.
"""

import pytest
from datetime import datetime, timedelta
from logitrack.simulation.geo_routes import TEXAS_HUBS, haversine_distance_km, get_road_distance_km
from logitrack.simulation.order_generator import OrderGenerator
from logitrack.simulation.event_generator import EventGenerator
from logitrack.simulation.telemetry_generator import TelemetryGenerator


def test_haversine_distance_accuracy():
    # Distance Dallas (32.7767, -96.7970) to Fort Worth (32.7555, -97.3308) is ~50 km
    dallas = TEXAS_HUBS["Dallas Main Hub"]
    ft_worth = TEXAS_HUBS["Fort Worth Hub"]
    dist = haversine_distance_km(dallas, ft_worth)
    assert 45 < dist < 55, f"Expected ~50km, got {dist}"


def test_order_generator_seed_determinism():
    gen1 = OrderGenerator(seed=42)
    gen2 = OrderGenerator(seed=42)
    start = datetime(2024, 1, 1)
    end = datetime(2024, 1, 10)
    
    orders1 = gen1.generate_orders(10, start, end, [1, 2], ["FT-001", "FT-002"])
    orders2 = gen2.generate_orders(10, start, end, [1, 2], ["FT-001", "FT-002"])
    
    assert orders1[0]["order_id"] == orders2[0]["order_id"]
    assert orders1[0]["route_distance_km"] == orders2[0]["route_distance_km"]
    assert orders1[0]["order_timestamp"] == orders2[0]["order_timestamp"]
    assert orders1[0]["origin_hub"] == orders2[0]["origin_hub"]
    assert orders1[0]["destination_hub"] == orders2[0]["destination_hub"]


def test_order_generator_provenance():
    gen = OrderGenerator(seed=42)
    orders = gen.generate_orders(5, datetime(2024, 1, 1), datetime(2024, 1, 5), [1], ["FT-001"])
    for o in orders:
        assert o["data_origin"] == "source: synthetic"
        assert o["generation_version"] == "1.0"
        assert o["origin_hub"] in TEXAS_HUBS
        assert o["destination_hub"] in TEXAS_HUBS


def test_event_generator_chronology():
    gen = OrderGenerator(seed=42)
    orders = gen.generate_orders(1, datetime(2024, 1, 1), datetime(2024, 1, 2), [1], ["FT-001"])
    deliv_order = orders[0]
    deliv_order["order_status"] = "Delivered"

    event_gen = EventGenerator(seed=42)
    events = event_gen.generate_order_events(deliv_order)
    
    assert len(events) >= 6
    # Verify timestamp ordering
    timestamps = [datetime.strptime(e["event_timestamp"], "%Y-%m-%d %H:%M:%S") for e in events]
    for i in range(len(timestamps) - 1):
        assert timestamps[i] <= timestamps[i + 1], f"Event {events[i]['event_type']} ({timestamps[i]}) after {events[i+1]['event_type']} ({timestamps[i+1]})"


def test_telemetry_texas_bounding_box():
    telem_gen = TelemetryGenerator(seed=42)
    pings = telem_gen.generate_trip_telemetry(
        vehicle_code="FT-001",
        origin_hub="Dallas Main Hub",
        dest_hub="Houston Hub",
        start_time=datetime(2024, 1, 1, 8, 0, 0),
        trip_duration_hours=4.0
    )
    assert len(pings) > 0
    for p in pings:
        assert 25.0 <= p["latitude"] <= 37.0
        assert -107.0 <= p["longitude"] <= -93.0
        assert 0.0 <= p["fuel_level_pct"] <= 100.0
