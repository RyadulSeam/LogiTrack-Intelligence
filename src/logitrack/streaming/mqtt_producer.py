"""
Real-Time MQTT Streaming Producer
LogiTrack Intelligence — Phase 5

Publishes simulated telematics and state transition events to Mosquitto MQTT broker
(QoS 1) across Texas freight corridors.
"""

import json
import random
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Generator
from loguru import logger
import paho.mqtt.client as mqtt

from logitrack.simulation.geo_routes import TEXAS_HUBS


class EventProducer:
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id="logitrack-producer")
        self.hubs = list(TEXAS_HUBS.keys())

    def connect(self):
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            logger.info(f"Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        except Exception as e:
            logger.warning(f"Could not connect to MQTT broker ({e}). Offline mode active.")

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()

    def generate_telemetry_event(self, vehicle_code: str = "FT-001") -> Dict[str, Any]:
        hub = random.choice(self.hubs)
        base_lat, base_lon = TEXAS_HUBS[hub]
        
        # Subtle GPS jitter simulating driving around hub or highway
        lat = round(base_lat + random.uniform(-0.15, 0.15), 6)
        lon = round(base_lon + random.uniform(-0.15, 0.15), 6)
        speed = round(random.uniform(45.0, 95.0), 1)

        return {
            "event_id": f"tel-{uuid.uuid4().hex[:12]}",
            "event_type": "vehicle.telemetry",
            "event_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_origin": "source: simulated",
            "vehicle_code": vehicle_code,
            "latitude": lat,
            "longitude": lon,
            "speed_kmh": speed,
            "heading_deg": round(random.uniform(0.0, 359.0), 1),
            "fuel_level_pct": round(random.uniform(25.0, 98.0), 1),
            "engine_temp_c": round(random.uniform(82.0, 96.0), 1),
            "engine_status": "ON"
        }

    def generate_order_event(self, order_id: int = 100001) -> Dict[str, Any]:
        status = random.choice([
            "ORDER_CREATED", "HUB_RECEIVED", "PROCESSING_STARTED",
            "DISPATCHED", "IN_TRANSIT", "OUT_FOR_DELIVERY", "DELIVERED"
        ])
        return {
            "event_id": f"ord-{uuid.uuid4().hex[:12]}",
            "event_type": "order.status",
            "event_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "data_origin": "source: simulated",
            "order_id": order_id,
            "order_status": status,
            "hub_name": random.choice(self.hubs),
            "driver_id": random.randint(1, 55),
            "vehicle_code": f"FT-{random.randint(1, 45):03d}"
        }

    def publish_event(self, topic: str, payload: Dict[str, Any], qos: int = 1):
        message = json.dumps(payload)
        self.client.publish(topic, message, qos=qos)
        logger.debug(f"Published to {topic} [QoS {qos}]: {payload.get('event_id')}")
