# Database Design & Storage Architecture
# LogiTrack Intelligence — Phase 3

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-08 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-13 |

---

## 1. Storage Architecture Overview

LogiTrack Intelligence implements a hybrid Lakehouse & Cloud Relational architecture optimized for zero cloud cost and low memory overhead (16 GB RAM boundary):

```
┌────────────────────────────────────────────────────────────────────────┐
│                        NEON POSTGRESQL (Cloud)                         │
│                                                                        │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────────────────┐  │
│  │     raw      │ ──► │   staging    │ ──► │       warehouse        │  │
│  │   (Bronze)   │     │   (Silver)   │     │         (Gold)         │  │
│  └──────────────┘     └──────────────┘     └────────────────────────┘  │
│                                                        │               │
│  ┌──────────────┐     ┌──────────────┐                 │               │
│  │   realtime   │     │      ml      │ ◄───────────────┘               │
│  │(Live Streams)│     │(Predictions) │                                 │
│  └──────────────┘     └──────────────┘                                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │ Archive & Analytics
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                       LOCAL LAKEHOUSE (DuckDB + Parquet)               │
│                                                                        │
│  DuckDB: Memory limited to 2 GB, 2 worker threads                      │
│  Parquet: Columnar telemetry & historical event archives               │
│  Path: data/lake/telemetry/, data/lake/events/                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Logical Schemas

| Schema | Role | Mutability | Retention Policy |
|---|---|---|---|
| `raw` | Bronze layer: verbatim CSV ingest + audit lineage | Append-only | Truncate & reload or append batch |
| `staging` | Silver layer: standardized snake_case, typed, deduplicated | Overwritten/Merged | Latest clean snapshot |
| `warehouse` | Gold layer: Dimensional star schema (Facts & Dimensions) | SCD / Fact append | Permanent business history |
| `realtime` | Live operational state & Dead Letter Queue (DLQ) | Rolling window | Rolling 30 days (older archived to Parquet) |
| `ml` | Machine Learning registry, metrics, & live predictions | Append-only | Model lifetime |

---

## 3. Warehouse Star Schema (Gold Layer)

### 3.1 Dimension Tables
1. **`warehouse.dim_date`**
   * Primary Key: `date_key` (e.g. `20241025`)
   * Attributes: `full_date`, `day_of_week`, `day_name`, `month_number`, `quarter`, `year`, `is_weekend`
2. **`warehouse.dim_hub`**
   * Primary Key: `hub_key`
   * Natural Key: `hub_id`
   * Attributes: `hub_name`, `city`, `state`, `daily_capacity`, `latitude`, `longitude`, `data_origin`
3. **`warehouse.dim_driver`**
   * Primary Key: `driver_key`
   * Natural Key: `driver_id`
   * Attributes: `driver_name`, `employment_type`, `hire_date`, `experience_years`, `performance_rating`, `data_origin`
4. **`warehouse.dim_vehicle`**
   * Primary Key: `vehicle_key`
   * Natural Key: `vehicle_code` (e.g., `FT-001`)
   * Attributes: `vehicle_id`, `vehicle_model`, `vehicle_type`, `current_status`, `lifetime_breakdowns`, `is_maintenance_alert`, `purchase_date`, `data_origin`
5. **`warehouse.dim_route`**
   * Primary Key: `route_key`
   * Attributes: `origin_hub_id`, `destination_hub_id`, `distance_km`, `typical_duration_hours`, `corridor_name`

### 3.2 Fact Tables
1. **`warehouse.fact_orders`**
   * Grain: 1 row per order
   * Foreign Keys: `order_date_key`, `delivery_date_key`, `hub_key`, `driver_key`, `vehicle_key`
   * Metrics: `package_weight_kg`, `delivery_time_hours`, `hub_processing_time_hours`, `csat_score`
   * Flags: `is_delayed`, `is_on_time`, `order_status`, `data_origin`
2. **`warehouse.fact_order_events`**
   * Grain: 1 row per order lifecycle state transition
   * Keys: `event_id`, `order_id`, `event_type`, `event_timestamp`, `hub_key`, `driver_key`, `vehicle_key`
3. **`warehouse.fact_vehicle_telemetry`**
   * Grain: 1 row per GPS/IoT telemetry ping
   * Keys: `telemetry_id`, `vehicle_key`, `ping_timestamp`
   * Telematics Metrics: `latitude`, `longitude`, `speed_kmh`, `heading_deg`, `fuel_level_pct`, `engine_temp_c`, `engine_status`
4. **`warehouse.fact_maintenance`**
   * Grain: 1 row per vehicle maintenance/breakdown incident
   * Keys: `maintenance_id`, `vehicle_key`, `service_type`, `scheduled_timestamp`, `completed_timestamp`, `downtime_hours`, `cost_usd`
5. **`warehouse.fact_hub_hourly`**
   * Grain: 1 row per hub per hour
   * Metrics: `orders_received`, `orders_dispatched`, `avg_processing_time_hours`, `backlog_volume`, `capacity_utilization_pct`

---

## 4. SQL Migration Scripts

All DDL definitions are version-controlled in `database/migrations/`:

| File | Purpose |
|---|---|
| `001_create_schemas.sql` | Initializes `raw`, `staging`, `warehouse`, `realtime`, `ml` |
| `002_create_raw_tables.sql` | DDL for raw Bronze staging with lineage tracking |
| `003_create_staging_tables.sql` | DDL for typed Silver tables with primary keys & check constraints |
| `004_create_warehouse_tables.sql` | DDL for star schema Dimensions and Fact tables |
| `005_create_realtime_tables.sql` | DDL for streaming event tables & Dead Letter Queue (DLQ) |
| `006_create_ml_tables.sql` | DDL for model registry, evaluations, predictions, and feature snapshots |

---

## 5. Local Lakehouse & Parquet Partitioning

To avoid overflowing cloud database free-tier storage limits, high-volume sensor telemetry and event logs are archived into local Parquet partitions:

```
data/lake/
├── logitrack.duckdb               # Local in-process DuckDB analytical catalog
├── telemetry/
│   └── year=YYYY/
│       └── month=MM/
│           └── telemetry_part_*.parquet
└── events/
    └── year=YYYY/
        └── month=MM/
            └── events_part_*.parquet
```

DuckDB executes analytical queries across millions of partitioned Parquet rows using:
```sql
SELECT vehicle_key, AVG(speed_kmh) as avg_speed, MAX(engine_temp_c) as max_temp
FROM 'data/lake/telemetry/**/*.parquet'
GROUP BY vehicle_key;
```
