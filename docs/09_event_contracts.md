# Event Contracts & Streaming Specification
# LogiTrack Intelligence — Phase 5

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-09 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-13 |

---

## 1. Streaming Architecture & Protocols

LogiTrack Intelligence uses **MQTT (Message Queuing Telemetry Transport)** via the Eclipse Mosquitto broker to model real-world IoT vehicular telematics and logistics event streaming.

```
┌─────────────────────────────────┐
│     SIMULATED EVENT PRODUCER    │
│  Vehicles · Orders · Drivers    │
└────────────────┬────────────────┘
                 │ MQTT Publish (QoS 1)
                 ▼
┌─────────────────────────────────┐
│     ECLIPSE MOSQUITTO BROKER    │
│     Port 1883 · Topics          │
└────────────────┬────────────────┘
                 │ MQTT Subscribe
                 ▼
┌─────────────────────────────────┐
│     PYTHON STREAMING CONSUMER   │
│  - JSON Schema Validation       │
│  - Idempotent Deduplication     │
│  - Dead Letter Queue Routing    │
└────────┬───────────────┬────────┘
         │               │
         ▼               ▼
┌─────────────────┐  ┌────────────────────────────────────┐
│ Neon / DuckDB   │  │ Local Parquet Lake                 │
│ realtime.*      │  │ data/lake/telemetry/year=YYYY/MM/  │
└─────────────────┘  └────────────────────────────────────┘
```

---

## 2. Topic Taxonomy

| Topic Pattern | Description | Frequency |
|---|---|---|
| `logitrack/vehicle/telemetry` | Periodic IoT GPS & vehicle sensor pings | 10–30s per active vehicle |
| `logitrack/order/status` | Granular order lifecycle state transitions | Event-driven (state change) |
| `logitrack/driver/activity` | Shift status, assignments, and rest breaks | Event-driven |
| `logitrack/hub/operations` | Hourly throughput, backlog volume, congestion | Periodic (hourly / 5-min sample) |

---

## 3. Event Contracts (JSON Schemas)

### 3.1 Topic: `logitrack/vehicle/telemetry`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "VehicleTelemetryEvent",
  "type": "object",
  "required": [
    "event_id", "event_type", "event_timestamp", "data_origin",
    "vehicle_code", "latitude", "longitude", "speed_kmh"
  ],
  "properties": {
    "event_id": { "type": "string", "description": "Unique UUID for deduplication" },
    "event_type": { "type": "string", "enum": ["vehicle.telemetry"] },
    "event_timestamp": { "type": "string", "format": "date-time" },
    "data_origin": { "type": "string", "enum": ["source: simulated"] },
    "vehicle_code": { "type": "string", "example": "FT-001" },
    "latitude": { "type": "number", "minimum": 25.0, "maximum": 37.0 },
    "longitude": { "type": "number", "minimum": -107.0, "maximum": -93.0 },
    "speed_kmh": { "type": "number", "minimum": 0.0, "maximum": 150.0 },
    "heading_deg": { "type": "number", "minimum": 0.0, "maximum": 360.0 },
    "fuel_level_pct": { "type": "number", "minimum": 0.0, "maximum": 100.0 },
    "engine_temp_c": { "type": "number", "minimum": 40.0, "maximum": 130.0 },
    "engine_status": { "type": "string", "enum": ["ON", "IDLE", "OFF"] }
  }
}
```

### 3.2 Topic: `logitrack/order/status`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "OrderStatusEvent",
  "type": "object",
  "required": [
    "event_id", "event_type", "event_timestamp", "data_origin",
    "order_id", "order_status"
  ],
  "properties": {
    "event_id": { "type": "string" },
    "event_type": { "type": "string", "enum": ["order.status"] },
    "event_timestamp": { "type": "string", "format": "date-time" },
    "data_origin": { "type": "string", "enum": ["source: simulated"] },
    "order_id": { "type": "integer" },
    "order_status": {
      "type": "string",
      "enum": [
        "ORDER_CREATED", "HUB_RECEIVED", "PROCESSING_STARTED",
        "PROCESSING_COMPLETED", "DISPATCHED", "IN_TRANSIT",
        "OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"
      ]
    },
    "hub_name": { "type": "string" },
    "driver_id": { "type": "integer" },
    "vehicle_code": { "type": "string" }
  }
}
```

### 3.3 Topic: `logitrack/driver/activity`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "DriverActivityEvent",
  "type": "object",
  "required": [
    "event_id", "event_type", "event_timestamp", "data_origin",
    "driver_id", "activity_type"
  ],
  "properties": {
    "event_id": { "type": "string" },
    "event_type": { "type": "string", "enum": ["driver.activity"] },
    "event_timestamp": { "type": "string", "format": "date-time" },
    "data_origin": { "type": "string", "enum": ["source: simulated"] },
    "driver_id": { "type": "integer" },
    "activity_type": {
      "type": "string",
      "enum": ["Shift Start", "Break", "Active Assignment", "Shift End"]
    },
    "vehicle_code": { "type": ["string", "null"] }
  }
}
```

### 3.4 Topic: `logitrack/hub/operations`
```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "title": "HubOperationsEvent",
  "type": "object",
  "required": [
    "event_id", "event_type", "event_timestamp", "data_origin",
    "hub_name", "active_backlog"
  ],
  "properties": {
    "event_id": { "type": "string" },
    "event_type": { "type": "string", "enum": ["hub.operations"] },
    "event_timestamp": { "type": "string", "format": "date-time" },
    "data_origin": { "type": "string", "enum": ["source: simulated"] },
    "hub_name": { "type": "string" },
    "active_backlog": { "type": "integer", "minimum": 0 },
    "throughput_rate_per_hr": { "type": "number", "minimum": 0.0 },
    "congestion_alert": { "type": "boolean" }
  }
}
```

---

## 4. QoS & Idempotent Deduplication Strategy

* **Quality of Service (QoS):** Level 1 (At-least-once delivery). Guarantees messages arrive even during network drops, but duplicate delivery can occur.
* **Consumer Deduplication Mechanism:**
  1. Every event carries a globally unique `event_id` (UUIDv4).
  2. The consumer queries the target `realtime.*` table:
     ```sql
     SELECT COUNT(*) FROM realtime.vehicle_events WHERE event_id = ?
     ```
  3. If already present, the duplicate event is silently acknowledged and skipped without duplicate insert.
  4. If new, the event is atomically inserted.
