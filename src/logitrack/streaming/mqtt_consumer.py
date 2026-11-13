"""
Real-Time MQTT Streaming Consumer Engine
LogiTrack Intelligence — Phase 5

Subscribes to operational MQTT topics, validates event contracts, handles duplicates
idempotently (QoS 1), persists to realtime.* tables, and archives telemetry to Parquet.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import pandas as pd

from logitrack.storage.duckdb_manager import DuckDBManager
from logitrack.streaming.event_contract import (
    validate_vehicle_telemetry,
    validate_order_status,
    validate_driver_activity,
    validate_hub_operations
)
from logitrack.streaming.dead_letter_handler import DeadLetterHandler


class EventConsumer:
    def __init__(self, db_path: str = "data/lake/logitrack.duckdb"):
        self.db_path = db_path
        self.dlq = DeadLetterHandler(db_path=db_path)
        self.manager = DuckDBManager(db_path=db_path)
        self.telemetry_buffer = []
        self.buffer_flush_size = 50

    def close(self):
        self.manager.close()

    def process_message(self, topic: str, payload_str: str) -> bool:
        """
        Processes a single incoming message from MQTT topic.
        Returns True if processed successfully, False if dropped or sent to DLQ.
        """
        # 1. Parse JSON
        try:
            payload = json.loads(payload_str)
        except Exception as e:
            self.dlq.route_to_dead_letter(topic, payload_str, f"Malformed JSON: {e}")
            return False

        event_id = payload.get("event_id")
        if not event_id:
            self.dlq.route_to_dead_letter(topic, payload_str, "Missing 'event_id' attribute")
            return False

        # 2. Schema Validation
        try:
            if topic == "logitrack/vehicle/telemetry":
                validate_vehicle_telemetry(payload)
                return self._handle_vehicle_telemetry(payload)
            elif topic == "logitrack/order/status":
                validate_order_status(payload)
                return self._handle_order_status(payload)
            elif topic == "logitrack/driver/activity":
                validate_driver_activity(payload)
                return self._handle_driver_activity(payload)
            elif topic == "logitrack/hub/operations":
                validate_hub_operations(payload)
                return self._handle_hub_operations(payload)
            else:
                self.dlq.route_to_dead_letter(topic, payload_str, f"Unknown topic: {topic}")
                return False
        except ValueError as ve:
            self.dlq.route_to_dead_letter(topic, payload_str, f"Contract violation: {ve}")
            return False
        except Exception as e:
            self.dlq.route_to_dead_letter(topic, payload_str, f"Unhandled exception: {e}")
            return False

    def _is_duplicate(self, table: str, event_id: str) -> bool:
        cnt = self.manager.conn.execute(
            f"SELECT COUNT(*) FROM {table} WHERE event_id = ?", [event_id]
        ).fetchone()[0]
        return cnt > 0

    def _handle_vehicle_telemetry(self, p: Dict[str, Any]) -> bool:
        table = "realtime.vehicle_events"
        if self._is_duplicate(table, p["event_id"]):
            logger.debug(f"Duplicate vehicle event '{p['event_id']}' detected. Skipping.")
            return True

        self.manager.conn.execute(
            f"""
            INSERT INTO {table} (
                event_id, vehicle_code, event_timestamp, latitude, longitude,
                speed_kmh, heading_deg, fuel_level_pct, engine_temp_c, engine_status, data_origin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                p["event_id"], p["vehicle_code"], p["event_timestamp"],
                float(p["latitude"]), float(p["longitude"]), float(p["speed_kmh"]),
                p.get("heading_deg"), p.get("fuel_level_pct"), p.get("engine_temp_c"),
                p.get("engine_status"), p.get("data_origin", "source: simulated")
            ]
        )

        # Buffer for Parquet lake export
        self.telemetry_buffer.append(p)
        if len(self.telemetry_buffer) >= self.buffer_flush_size:
            self._flush_telemetry_to_parquet()

        return True

    def _handle_order_status(self, p: Dict[str, Any]) -> bool:
        table = "realtime.order_events"
        if self._is_duplicate(table, p["event_id"]):
            logger.debug(f"Duplicate order event '{p['event_id']}' detected. Skipping.")
            return True

        self.manager.conn.execute(
            f"""
            INSERT INTO {table} (
                event_id, order_id, event_type, event_timestamp,
                hub_name, driver_id, vehicle_code, data_origin
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
            """,
            [
                p["event_id"], int(p["order_id"]), p["order_status"],
                p["event_timestamp"], p.get("hub_name"), p.get("driver_id"),
                p.get("vehicle_code"), p.get("data_origin", "source: simulated")
            ]
        )
        return True

    def _handle_driver_activity(self, p: Dict[str, Any]) -> bool:
        table = "realtime.driver_events"
        if self._is_duplicate(table, p["event_id"]):
            return True

        self.manager.conn.execute(
            f"""
            INSERT INTO {table} (
                event_id, driver_id, activity_type, event_timestamp, vehicle_code
            ) VALUES (?, ?, ?, ?, ?);
            """,
            [
                p["event_id"], int(p["driver_id"]), p["activity_type"],
                p["event_timestamp"], p.get("vehicle_code")
            ]
        )
        return True

    def _handle_hub_operations(self, p: Dict[str, Any]) -> bool:
        table = "realtime.hub_events"
        if self._is_duplicate(table, p["event_id"]):
            return True

        self.manager.conn.execute(
            f"""
            INSERT INTO {table} (
                event_id, hub_name, event_timestamp, active_backlog,
                throughput_rate_per_hr, congestion_alert
            ) VALUES (?, ?, ?, ?, ?, ?);
            """,
            [
                p["event_id"], p["hub_name"], p["event_timestamp"],
                int(p["active_backlog"]), float(p.get("throughput_rate_per_hr", 0.0)),
                bool(p.get("congestion_alert", False))
            ]
        )
        return True

    def _flush_telemetry_to_parquet(self):
        """Flushes buffered telemetry events to local Parquet partitions."""
        if not self.telemetry_buffer:
            return

        df = pd.DataFrame(self.telemetry_buffer)
        now = datetime.now()
        year = now.strftime("%Y")
        month = now.strftime("%m")

        lake_dir = Path(f"data/lake/telemetry/year={year}/month={month}")
        lake_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = lake_dir / f"telemetry_{now.strftime('%Y%m%d_%H%M%S')}.parquet"
        df.to_parquet(file_path, index=False)
        logger.info(f"Flushed {len(df)} telemetry pings to Parquet: {file_path.name}")
        self.telemetry_buffer.clear()
