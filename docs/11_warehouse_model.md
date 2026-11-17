# Enterprise Data Warehouse Model & dbt Specification
# LogiTrack Intelligence — Phase 6

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-11 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-17 |

---

## 1. Dimensional Architecture Overview

LogiTrack Intelligence implements a dimensional **Star Schema** model within the **Gold (`warehouse`) layer**.

```
                           ┌──────────────────┐
                           │   dim_date       │
                           │ 1,461 calendar d │
                           └────────┬─────────┘
                                    │
                                    │ order_date_key / delivery_date_key
                                    ▼
┌──────────────────┐       ┌──────────────────┐       ┌──────────────────┐
│   dim_hub        │       │   fact_orders    │       │   dim_vehicle    │
│ 6 Texas Hubs     │◄──────┤ 27,979 shipments ├──────►│ 45 Fleet Units   │
│ Lat/Lon coords   │hub_key│ Grain: 1/order   │veh_key│ Asset classes    │
└──────────────────┘       └────────┬─────────┘       └──────────────────┘
                                    │
                                    │ driver_key
                                    ▼
                           ┌──────────────────┐
                           │   dim_driver     │
                           │ 55 Personnel     │
                           │ Performance, Exp │
                           └──────────────────┘
```

Supporting Marts:
* **`dim_route`**: 36 inter-hub freight routes across Texas highway corridors (I-35, I-45, I-10).
* **`fact_order_events`**: Granular order state transition events.
* **`fact_vehicle_telemetry`**: GPS, speed, and fuel sensor pings.
* **`fact_hub_hourly`**: Hourly aggregated throughput and congestion metrics.

---

## 2. Table Grains & Key Design

| Model Name | Model Type | Grain | Primary Key | Foreign Keys |
|---|---|---|---|---|
| `warehouse.dim_date` | Dimension | 1 row per calendar day (2023–2026) | `date_key` (YYYYMMDD) | None |
| `warehouse.dim_hub` | Dimension | 1 row per regional distribution center | `hub_key` | None |
| `warehouse.dim_driver` | Dimension | 1 row per logistics driver | `driver_key` | None |
| `warehouse.dim_vehicle` | Dimension | 1 row per fleet vehicle | `vehicle_key` | None |
| `warehouse.dim_route` | Dimension | 1 row per origin-destination hub pair | `route_key` | `origin_hub_id`, `destination_hub_id` |
| `warehouse.fact_orders` | Fact | 1 row per delivery order | `order_id` | `order_date_key`, `delivery_date_key`, `hub_key`, `driver_key`, `vehicle_key` |
| `warehouse.fact_order_events` | Fact | 1 row per lifecycle state transition | `event_id` | `hub_key`, `driver_key`, `vehicle_key` |
| `warehouse.fact_vehicle_telemetry` | Fact | 1 row per GPS/IoT sensor ping | `telemetry_id` | `vehicle_key` |
| `warehouse.fact_hub_hourly` | Fact | 1 row per hub per hour | `hub_hourly_id` | `hub_key`, `date_key` |

---

## 3. Slowly Changing Dimensions (SCD Type 2)

Driver assignments and vehicle maintenance statuses evolve over time.
To track historical transitions:
* **`valid_from`** and **`valid_to`** timestamps capture the active window.
* **`is_current`** boolean flag enables fast filtering for current operational state.
* Historical order assignments point to the surrogate key version active at dispatch.

---

## 4. dbt Transformation & Automated Testing

The dbt project (`dbt_project/`) automates model generation and continuous quality testing:

| Stage | Models | Materialization | Test Coverage |
|---|---|---|---|
| **Staging** | `stg_hubs`, `stg_drivers`, `stg_vehicles`, `stg_orders` | View | `unique`, `not_null` |
| **Marts** | `dim_date`, `dim_hub`, `dim_driver`, `dim_vehicle`, `dim_route`, `fact_orders`, `fact_order_events`, `fact_vehicle_telemetry`, `fact_hub_hourly` | Table | `unique`, `not_null`, `relationships` |

**Verification Results:**
* **13 models built** (4 views + 9 tables) in 1.67 seconds.
* **36 data tests passed** in 0.51 seconds (100% pass rate).
