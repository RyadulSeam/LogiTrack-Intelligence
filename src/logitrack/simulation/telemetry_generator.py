"""
Vehicle Telematics (GPS & Sensor) Simulation Engine
LogiTrack Intelligence — Phase 2

Generates realistic periodic IoT sensor pings for fleet vehicles
traversing Texas freight corridors.
"""

import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any

from logitrack.simulation.geo_routes import TEXAS_HUBS, interpolate_waypoints, calculate_bearing


class TelemetryGenerator:
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.hubs = list(TEXAS_HUBS.keys())

    def generate_trip_telemetry(
        self,
        vehicle_code: str,
        origin_hub: str,
        dest_hub: str,
        start_time: datetime,
        trip_duration_hours: float
    ) -> List[Dict[str, Any]]:
        coord1 = TEXAS_HUBS[origin_hub]
        coord2 = TEXAS_HUBS[dest_hub]

        # Waypoint count proportional to duration (e.g. 1 ping every 10-15 mins)
        steps = max(5, int(trip_duration_hours * 4))
        waypoints = interpolate_waypoints(coord1, coord2, num_steps=steps)
        bearing = calculate_bearing(coord1, coord2)

        telemetry_records = []
        fuel_level = random.uniform(75.0, 100.0)
        time_step = timedelta(seconds=int((trip_duration_hours * 3600) / steps))
        current_time = start_time

        for i, (lat, lon) in enumerate(waypoints):
            # Speed variations: highway cruising with small random fluctuations
            if i == 0 or i == len(waypoints) - 1:
                speed = random.uniform(15.0, 35.0)  # Near hub
                engine_status = "IDLE" if speed < 20 else "ON"
            else:
                speed = random.uniform(60.0, 95.0)  # Highway transit
                engine_status = "ON"

            fuel_consumption_rate = (speed / 70.0) * random.uniform(0.4, 0.8)
            fuel_level = max(5.0, fuel_level - fuel_consumption_rate)
            engine_temp = round(random.uniform(85.0, 98.0), 1)

            ping = {
                "telemetry_id": f"tel-{uuid.uuid4().hex[:12]}",
                "vehicle_code": vehicle_code,
                "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
                "latitude": lat,
                "longitude": lon,
                "speed_kmh": round(speed, 1),
                "heading_deg": bearing,
                "fuel_level_pct": round(fuel_level, 1),
                "engine_temp_c": engine_temp,
                "engine_status": engine_status,
                "data_origin": "source: synthetic",
                "generation_version": "1.0"
            }
            telemetry_records.append(ping)
            current_time += time_step

        return telemetry_records
