# LogiTrack Intelligence — Power BI Project
# Stage 1: Project Inspection Report
**Document Reference:** `docs/pbi/stage1_inspection_report.md`  
**Phase:** Phase 7 (Specialized) — Enterprise Power BI Analytics  
**Inspection Date:** 2026-11-18  
**Inspector:** Data & BI Architecture Team

---

## 1. Data Inventory

### 1.1 Database Architecture

| Schema | Purpose | Table Count |
|---|---|---|
| `raw` | Bronze — Raw CSV ingestion (VARCHAR-only) | 4 tables |
| `staging` | Silver — Cleaned, typed, deduplicated | 4 tables |
| `warehouse` | Gold — Star Schema (Facts + Dimensions) | 9 tables |
| `realtime` | Live streaming event store | 5 tables |
| `ml` | Model registry, evaluations, predictions | 4 tables |

### 1.2 Warehouse Gold Tables (Primary Power BI Source)

| Table | Type | Rows | Grain | Primary Key |
|---|---|---|---|---|
| `warehouse.dim_date` | Dimension | 1,461 | 1 row per calendar day (2023-01-01 → 2026-12-31) | `date_key` (INT, YYYYMMDD) |
| `warehouse.dim_hub` | Dimension | 6 | 1 row per distribution hub | `hub_key` |
| `warehouse.dim_driver` | Dimension | 55 | 1 row per driver | `driver_key` |
| `warehouse.dim_vehicle` | Dimension | 45 | 1 row per fleet vehicle | `vehicle_key` |
| `warehouse.dim_route` | Dimension | 36 | 1 row per hub-to-hub route pair | `route_key` |
| `warehouse.fact_orders` | Fact | 27,979 | 1 row per distinct order | `order_id` (BIGINT) |
| `warehouse.fact_order_events` | Fact | 50 | 1 row per order lifecycle event | `event_id` |
| `warehouse.fact_hub_hourly` | Fact | 4,296 | 1 row per hub per date per hour | `hub_hourly_id` (MD5 hash) |
| `warehouse.fact_vehicle_telemetry` | Fact | 121 | 1 row per vehicle GPS ping | `telemetry_id` |
| `warehouse.fact_maintenance` | Fact | **0 (EMPTY)** | 1 row per maintenance event | `maintenance_id` |

---

## 2. Table & Column Assessment

### 2.1 warehouse.fact_orders (27,979 rows) — PRIMARY FACT TABLE

| Column | Type | Nullable | Business Role | Data Quality |
|---|---|---|---|---|
| `order_id` | BIGINT | NO (PK) | Unique order identifier | ✅ 27,979 unique values |
| `order_date_key` | INTEGER | YES (FK→dim_date) | Order placement date | ✅ 0 nulls |
| `delivery_date_key` | INTEGER | YES (FK→dim_date) | Actual delivery date | ⚠️ 252 nulls (cancelled orders) |
| `hub_key` | INTEGER | YES (FK→dim_hub) | Origin hub | ✅ 0 nulls |
| `driver_key` | INTEGER | YES (FK→dim_driver) | Assigned driver | ✅ 0 nulls |
| `vehicle_key` | INTEGER | YES (FK→dim_vehicle) | Assigned vehicle | ✅ 0 nulls |
| `order_status` | VARCHAR | NO | Delivered / Cancelled | ✅ 27,727 Delivered (99.1%), 252 Cancelled (0.9%) |
| `is_delayed` | BOOLEAN | NO | Was delivery late? | ✅ 5,908 True (21.1%), 22,071 False (78.9%) |
| `is_on_time` | BOOLEAN | NO | Was delivery on-time? | ✅ Inverse of is_delayed |
| `delay_reason` | VARCHAR | YES | Root cause of delay | ✅ 5,908 non-null values, 10 distinct categories |
| `package_weight_kg` | DECIMAL(8,2) | YES | Package weight | ❌ **ALL 27,979 are NULL** |
| `delivery_priority` | VARCHAR | YES | Priority tier | ⚠️ **ALL 27,979 are "Standard"** (single value — no variance) |
| `csat_score` | SMALLINT | YES | Customer Satisfaction (1-5) | ✅ 27,979 non-null; distribution: 1→252, 2→1,411, 3→2,701, 4→12,617, 5→10,998 |
| `delivery_time_hours` | DECIMAL(8,2) | YES | Total transit duration | ✅ 27,727 valid; 252 null (cancelled); range: 2.27–143.14h, mean: 35.78h |
| `hub_processing_time_hours` | DECIMAL(6,2) | NO | Hub sorting/staging time | ✅ 27,979 valid; range: 0.43–4.19h, mean: 1.97h |
| `data_origin` | VARCHAR | NO | Data provenance | ✅ All "source: original" |
| `created_at` | TIMESTAMP | YES | Record creation timestamp | ✅ System-generated |

### 2.2 warehouse.dim_hub (6 rows)

| Column | Type | Nullable | Data Quality |
|---|---|---|---|
| `hub_key` | INTEGER | NO (PK) | ✅ 1–6 |
| `hub_id` | INTEGER | NO (UNI) | ✅ 1–6 |
| `hub_name` | VARCHAR | NO | ✅ Dallas Main Hub, Houston Hub, Austin Hub, San Antonio Hub, Fort Worth Hub, El Paso Hub |
| `city` | VARCHAR | NO | ✅ 6 Texas cities |
| `state` | VARCHAR | YES | ✅ All "TX" |
| `daily_capacity` | INTEGER | NO | ✅ Range: 150–380 orders/day |
| `latitude` | DECIMAL(9,6) | YES | ✅ All 6 populated with valid Texas coords |
| `longitude` | DECIMAL(9,6) | YES | ✅ All 6 populated |
| `data_origin` | VARCHAR | YES | ✅ All "source: original" |

### 2.3 warehouse.dim_driver (55 rows)

| Column | Type | Nullable | Data Quality |
|---|---|---|---|
| `driver_key` | INTEGER | NO (PK) | ✅ |
| `driver_id` | INTEGER | NO (UNI) | ✅ 1–55 |
| `driver_name` | VARCHAR | NO | ✅ 55 distinct names |
| `employment_type` | VARCHAR | NO | ✅ Full-time (47), Part-time (6), Contract (2) |
| `hire_date` | DATE | NO | ✅ Valid dates |
| `experience_years` | INTEGER | NO | ✅ Available |
| `performance_rating` | INTEGER | YES | ✅ Scale 1–5; distribution: 1→2, 2→2, 3→21, 4→22, 5→8 |
| `data_origin` | VARCHAR | YES | ✅ All "source: original" |

### 2.4 warehouse.dim_vehicle (45 rows)

| Column | Type | Nullable | Data Quality |
|---|---|---|---|
| `vehicle_key` | INTEGER | NO (PK) | ✅ |
| `vehicle_id` | INTEGER | NO (UNI) | ✅ 1–45 |
| `vehicle_code` | VARCHAR | NO (UNI) | ✅ FT-001 to FT-045 |
| `vehicle_model` | VARCHAR | NO | ✅ Mercedes Sprinter, Freightliner M2, etc. |
| `vehicle_type` | VARCHAR | NO | ✅ Van (30), Truck (9), Pickup (3), Box Truck (3) |
| `current_status` | VARCHAR | NO | ✅ Active (33), Maintenance (12) |
| `lifetime_breakdowns` | INTEGER | YES | ✅ Range: 0–28, mean: 11.9 |
| `is_maintenance_alert` | BOOLEAN | NO | ✅ True (12), False (33) |
| `purchase_date` | DATE | NO | ✅ 2018-03-24 to 2023-09-28 |
| `data_origin` | VARCHAR | YES | ✅ |

### 2.5 warehouse.dim_route (36 rows)

| Column | Type | Nullable | Data Quality |
|---|---|---|---|
| `route_key` | INTEGER | NO (PK) | ✅ |
| `origin_hub_id` | INTEGER | NO | ✅ |
| `destination_hub_id` | INTEGER | NO | ✅ |
| `distance_km` | DECIMAL(8,2) | NO | ✅ 28.5–1,279.8 km |
| `typical_duration_hours` | DECIMAL(6,2) | YES | ✅ |
| `corridor_name` | VARCHAR | YES | ✅ Named corridors |

### 2.6 warehouse.fact_hub_hourly (4,296 rows)

| Column | Type | Nullable | Data Quality |
|---|---|---|---|
| `hub_hourly_id` | VARCHAR | NO (PK) | ✅ MD5 hash composite key |
| `hub_key` | INTEGER | YES (FK) | ✅ |
| `date_key` | INTEGER | YES (FK) | ✅ |
| `hour_of_day` | SMALLINT | NO | ✅ 0–23 |
| `orders_received` | INTEGER | YES | ✅ Avg: 6.51/hr |
| `orders_dispatched` | INTEGER | YES | ✅ Avg: 6.45/hr |
| `avg_processing_time_hours` | DECIMAL(6,2) | YES | ✅ |
| `backlog_volume` | INTEGER | YES | ✅ Range: 0–2 (very low backlog) |
| `capacity_utilization_pct` | DECIMAL(5,2) | YES | ✅ Avg: 2.81% (low utilization) |

### 2.7 ML Schema Tables

| Table | Rows | Purpose |
|---|---|---|
| `ml.model_registry` | 4 | 4 registered models (delay, ETA, hub congestion, maintenance) |
| `ml.model_evaluations` | 19 | Performance metrics per model |
| `ml.predictions` | 10 | Sample batch predictions (delay risk for 10 orders) |
| `ml.feature_snapshots` | 0 | Empty |

### 2.8 Synthetic Maintenance CSV (NOT in Warehouse)

| Field | Description | Quality |
|---|---|---|
| `maintenance_id` | Unique ID | ✅ 500 records |
| `vehicle_code` | FK to dim_vehicle | ✅ |
| `service_type` | 8 categories | ✅ |
| `status` | Completed (437), Scheduled (35), In Progress (28) | ✅ |
| `downtime_hours` | Range: 2.6–35.5h | ✅ 437 non-null |
| `cost_usd` | Range: \$128.96–\$1,848.94 | ✅ |
| `data_origin` | All "source: synthetic" | ✅ |

---

## 3. Existing Model Assessment

The existing warehouse follows a **Star Schema** with:
- **5 Dimension Tables**: `dim_date`, `dim_hub`, `dim_driver`, `dim_vehicle`, `dim_route`
- **4 Fact Tables**: `fact_orders` (primary), `fact_hub_hourly`, `fact_order_events`, `fact_vehicle_telemetry`
- **1 Empty Fact Table**: `fact_maintenance` (schema exists but no data loaded)

**Relationship Integrity:**
- `fact_orders` → `dim_date` (via `order_date_key`, `delivery_date_key`) — dual date role
- `fact_orders` → `dim_hub` (via `hub_key`) — ✅ 0 null FKs
- `fact_orders` → `dim_driver` (via `driver_key`) — ✅ 0 null FKs
- `fact_orders` → `dim_vehicle` (via `vehicle_key`) — ✅ 0 null FKs
- `fact_hub_hourly` → `dim_hub`, `dim_date` — ✅ valid
- `fact_orders` ↛ `dim_route` — **No direct FK relationship exists** (route is not assigned to individual orders)

---

## 4. Data Quality Summary

### ✅ Strengths
1. **Primary fact table (`fact_orders`)** has 27,979 clean records with zero null foreign keys on hub/driver/vehicle.
2. **Delay reasons** exist with 10 distinct categories and 5,908 delayed orders — Pareto analysis is **fully supported**.
3. **CSAT Score** is populated for all 27,979 orders (scale 1–5) — usable KPI.
4. **Hub geo-coordinates** (latitude/longitude) exist for all 6 hubs — Texas map is **fully supported**.
5. **Driver experience and performance rating** exist — driver analysis is **fully supported**.
6. **Vehicle purchase date** enables fleet age calculation — age-based analysis is **supported**.
7. **ML model registry** has 4 registered models with 19 evaluation metrics — predictive integration is **supported**.

### ⚠️ Limitations
1. **`package_weight_kg`** — ALL 27,979 values are NULL. Cannot be used for any KPI.
2. **`delivery_priority`** — ALL records are "Standard". No priority segmentation possible.
3. **`fact_maintenance`** — Table schema exists but contains 0 rows. Maintenance analysis in Page 4 must use `data/synthetic/synthetic_maintenance.csv` (500 records) or `dim_vehicle` flags only.
4. **`fact_order_events`** — Only 50 rows (simulated events). Very sparse for lifecycle analysis.
5. **`fact_vehicle_telemetry`** — Only 121 rows (simulated pings). Minimal for fleet telemetry dashboards.
6. **No "Promised Delivery Timestamp"** exists anywhere. OTD Rate must use the existing `is_on_time` boolean flag.
7. **No "Shipping Method" or "Route Assignment"** column exists in `fact_orders`. Route-level delivery analysis is NOT directly supported.
8. **`capacity_utilization_pct`** averages 2.81% — values are very low, limiting congestion visual impact.
9. **`backlog_volume`** range is only 0–2 — operational congestion is minimal in historical data.

---

## 5. Data Gap Report

| Gap ID | Missing Field / Data | Impact | Affected Dashboard Page | Mitigation |
|---|---|---|---|---|
| GAP-01 | `package_weight_kg` (all NULL) | Cannot display package weight KPIs | Page 1 | **Exclude** from all visuals. Document as unavailable. |
| GAP-02 | `delivery_priority` (all "Standard") | No priority-based segmentation | Page 1, Page 3 | **Exclude** from slicers and comparisons. Document as single-value. |
| GAP-03 | `warehouse.fact_maintenance` (0 rows) | No warehouse-level maintenance fact | Page 4 | **Load synthetic maintenance CSV** into Power BI as a separate table with clear "source: synthetic" labeling. |
| GAP-04 | Promised Delivery Timestamp | Cannot calculate OTD from timestamp difference | Page 1, Page 3 | **Use existing `is_on_time` boolean** as the authoritative OTD indicator. Document that OTD is source-defined, not calculated. |
| GAP-05 | Shipping Method | No delivery method segmentation | Page 3 | **Exclude** shipping method analysis. Document as unavailable. |
| GAP-06 | Route Assignment per Order | Cannot link orders to specific routes | Page 3 | **Exclude** route-level delivery analysis. Use hub-level comparisons instead. |
| GAP-07 | `fact_order_events` (50 rows) | Insufficient for lifecycle funnel | All | **Exclude** order event funnel visuals. Use `fact_orders` status distribution instead. |
| GAP-08 | `fact_vehicle_telemetry` (121 rows) | Very sparse for real-time fleet view | Page 4 | Use as supplementary reference only. Primary fleet analysis from `dim_vehicle`. |

---

## 6. KPI Supportability Assessment

### ✅ Fully Supported KPIs (can be reliably calculated from existing data)

| KPI | Source Table | Calculation Basis |
|---|---|---|
| Total Orders | `fact_orders` | COUNT DISTINCT `order_id` |
| Delivered Orders | `fact_orders` | COUNT WHERE `order_status` = 'Delivered' |
| Cancelled Orders | `fact_orders` | COUNT WHERE `order_status` = 'Cancelled' |
| On-Time Delivery Rate % | `fact_orders` | COUNT(`is_on_time` = TRUE AND status = 'Delivered') / Delivered Orders |
| Late Delivery Rate % | `fact_orders` | COUNT(`is_delayed` = TRUE AND status = 'Delivered') / Delivered Orders |
| Average Delivery Duration | `fact_orders` | AVG(`delivery_time_hours`) WHERE Delivered |
| Average Hub Processing Time | `fact_orders` | AVG(`hub_processing_time_hours`) |
| Average CSAT Score | `fact_orders` | AVG(`csat_score`) WHERE Delivered |
| Total Hubs | `dim_hub` | COUNT |
| Total Vehicles | `dim_vehicle` | COUNT |
| Active Vehicles | `dim_vehicle` | COUNT WHERE `current_status` = 'Active' |
| Vehicles Under Maintenance | `dim_vehicle` | COUNT WHERE `current_status` = 'Maintenance' |
| Fleet Availability Rate % | `dim_vehicle` | Active / Total Vehicles |
| Maintenance Alert Count | `dim_vehicle` | COUNT WHERE `is_maintenance_alert` = TRUE |
| Hub Daily Capacity | `dim_hub` | `daily_capacity` field |
| Hub Orders Received (hourly) | `fact_hub_hourly` | `orders_received` |
| Hub Backlog | `fact_hub_hourly` | `backlog_volume` |
| Delay Root Cause Distribution | `fact_orders` | GROUP BY `delay_reason` |

### ⚠️ Partially Supported KPIs (available but with caveats)

| KPI | Caveat |
|---|---|
| Hub Capacity Utilization % | Values average 2.81% — very low; visually unimpressive but technically valid. |
| Fleet Utilization Rate | Only static status (Active/Maintenance) available, not time-based utilization. |
| Vehicle Age | Calculable from `purchase_date`, but represents age since purchase, not operational age. |
| ML Delay Predictions | Only 10 sample predictions in `ml.predictions`. |

### ❌ Unsupported KPIs (data does not exist)

| KPI | Reason |
|---|---|
| Package Weight Analysis | All NULL |
| Priority-Based Segmentation | Single value ("Standard") |
| Shipping Method Comparison | Column does not exist |
| Route-Level Delivery Performance | No order-to-route FK |
| Maintenance Cost Analytics (Warehouse) | `fact_maintenance` empty; CSV data is synthetic |
| Order Backlog Trend (absolute) | Backlog range 0–2, minimal variance |
| Promised vs Actual Delivery Comparison | No promised delivery timestamp |

---

## 7. Recommended Power BI Data Source Strategy

Based on the inspection, the Power BI semantic model should source data from:

1. **Primary Source: `warehouse` schema** — `fact_orders`, `dim_date`, `dim_hub`, `dim_driver`, `dim_vehicle`, `fact_hub_hourly`
2. **Secondary Source: `ml` schema** — `model_registry`, `model_evaluations`, `predictions`
3. **Supplementary Source: CSV** — `data/synthetic/synthetic_maintenance.csv` (loaded as `FactMaintenance` with clear "source: synthetic" labeling)
4. **Excluded from Power BI**: `fact_order_events` (50 rows — too sparse), `fact_vehicle_telemetry` (121 rows — supplementary only), `dim_route` (no FK from fact_orders)

---

> **Stage 1 Inspection Complete. Dashboard construction has NOT begun. Awaiting confirmation to proceed to Stage 2: Business Requirements & KPI Dictionary.**
