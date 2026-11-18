# LogiTrack Intelligence — Power BI Project
# Stage 3: Star-Schema Semantic Model Architecture
**Document Reference:** `docs/pbi/stage3_semantic_model.md`  
**Phase:** Phase 7 (Specialized) — Enterprise Power BI Analytics  
**Version:** 1.0.0  
**Status:** Validated & Integrity-Checked (0 Orphan Keys)  

---

## 1. Enterprise Star Schema Architecture

The **LogiTrack Intelligence** Power BI semantic model is engineered as a clean, high-performance **Star Schema** with explicit fact-to-dimension relationships, single-direction filter propagation, and zero circular paths or bidirectional ambiguity.

```
                           ┌──────────────────────────┐
                           │         DimDate          │
                           │   date_key (PK: INT)     │
                           └─────────────┬────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │ 1:* (Active)          │ 1:* (Inactive)        │ 1:* (Active)
                 │ [order_date_key]      │ [delivery_date_key]   │ [date_key]
                 ▼                       │                       ▼
┌─────────────────────────────────┐      │              ┌───────────────────┐
│           FactOrders            │◄─────┘              │   FactHubHourly   │
│  order_id (PK: BIGINT)          │                     │ hub_hourly_id (PK)│
└────▲───────────────▲────────▲───┘                     └───▲───────────────┘
     │ 1:*           │ 1:*    │ 1:*                         │ 1:*
     │               │        │                             │
┌────┴────────┐ ┌────┴──────┐ │ 1:*                         │
│   DimHub    │ │ DimDriver │ └─────────────┐               │
│ hub_key (PK)│ │driver_key │               │               │
└────┬────────┘ └───────────┘               ▼               │
     │                              ┌───────────────┐       │
     └─────────────────────────────►│  DimVehicle   │◄──────┼──────────┐
      1:* [hub_key]                 │vehicle_key(PK)│       │          │
                                    └───────▲───────┘       │          │
                                            │ 1:*           │          │
                                    ┌───────┴───────┐       │          │
                                    │FactMaintenance│       │          │
                                    │(source: synth)│       │          │
                                    └───────────────┘       │          │
                                                            │          │
                                                            └──────────┘
```

---

## 2. Table & Grain Inventory

### 2.1 Dimension Tables (Single Source of Business Truth)

| Table Name | Source File | Row Count | Granularity (Grain) | Primary Key | Business Role |
|---|---|---|---|---|---|
| **`DimDate`** | `DimDate.csv` | 1,461 | 1 row per calendar day (2023-01-01 to 2026-12-31) | `date_key` (INT: YYYYMMDD) | Role-playing date dimension for order placement and delivery fulfillment. Marked as official Date table. |
| **`DimHub`** | `DimHub.csv` | 6 | 1 row per physical distribution center in Texas | `hub_key` (INT) | Spatial & physical routing entity (Dallas, Houston, Austin, San Antonio, Fort Worth, El Paso). |
| **`DimDriver`** | `DimDriver.csv` | 55 | 1 row per professional delivery driver | `driver_key` (INT) | Human capital dimension with experience years, employment type, and performance rating. |
| **`DimVehicle`** | `DimVehicle.csv` | 45 | 1 row per registered fleet vehicle | `vehicle_key` (INT) | Capital asset dimension with vehicle model, classification type (Van, Truck, Pickup, Box Truck), status, and breakdown history. |

### 2.2 Fact Tables (Transactional & Measurable Events)

| Table Name | Source File | Row Count | Granularity (Grain) | Primary Key | Business Role |
|---|---|---|---|---|---|
| **`FactOrders`** | `FactOrders.csv` | 27,979 | 1 row per distinct order placement | `order_id` (BIGINT) | Primary transactional fact tracking delivery outcomes, SLAs, transit duration, processing time, and CSAT scores. |
| **`FactHubHourly`** | `FactHubHourly.csv` | 4,296 | 1 row per hub per date per hour (0–23) | `hub_hourly_id` (VARCHAR MD5) | Periodic snapshot fact tracking hourly intake, dispatches, processing time, backlog, and capacity utilization. |
| **`FactMaintenance`** | `FactMaintenance.csv` | 500 | 1 row per workshop maintenance intervention | `maintenance_id` (VARCHAR) | Supplementary transactional fact tracking downtime, service types, costs, and repair status (`source: synthetic`). |
| **`FactMLPredictions`** | `FactMLPredictions.csv` | 10 | 1 row per inference execution on an entity | `prediction_id` (VARCHAR) | Pilot batch scoring feed displaying model delay predictions and continuous probability scores. |

---

## 3. Relationship & Cardinality Map

All relationships follow **Single-Direction Filter Propagation (Dimension filters Fact)**. Bidirectional cross-filtering is strictly avoided to preserve index performance and eliminate ambiguous filter loops.

| From Table (Dimension) | From Column (PK) | To Table (Fact) | To Column (FK) | Cardinality | Filter Direction | State | Business Role |
|---|---|---|---|---|---|---|---|
| `DimDate` | `date_key` | `FactOrders` | `order_date_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Active** | Primary chronological slicer filter for order placement. |
| `DimDate` | `date_key` | `FactOrders` | `delivery_date_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Inactive** | Role-playing date activated via DAX `USERELATIONSHIP` for delivery completion analysis. |
| `DimHub` | `hub_key` | `FactOrders` | `hub_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Active** | Filters orders by origin Texas regional hub. |
| `DimDriver` | `driver_key` | `FactOrders` | `driver_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Active** | Filters orders by assigned delivery driver. |
| `DimVehicle` | `vehicle_key` | `FactOrders` | `vehicle_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Active** | Filters orders by assigned delivery vehicle asset. |
| `DimDate` | `date_key` | `FactHubHourly` | `date_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Active** | Filters hourly hub throughput by calendar observation date. |
| `DimHub` | `hub_key` | `FactHubHourly` | `hub_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Active** | Filters hourly throughput by regional hub. |
| `DimVehicle` | `vehicle_key` | `FactMaintenance` | `vehicle_key` | 1 : Many (1:*) | Single (Dim → Fact) | **Active** | Filters maintenance repair records by vehicle asset. |
| `FactOrders` | `order_id` | `FactMLPredictions` | `order_id` | 1 : 1 (or 1:*) | Single (Fact → ML) | **Active** | Integrates ML pilot inference risk scores to corresponding orders. |

### Integrity Verification Results
- **PK Uniqueness:** 100% verified (0 duplicate keys across all 8 tables).
- **FK Orphans:** 0 orphans on all active and inactive relationships.
- **Null Handling:** `FactOrders.delivery_date_key` has 252 nulls, strictly representing unfulfilled/cancelled orders (handled cleanly by Power BI blank row semantics).

---

## 4. Date Dimension & Time Intelligence Design

The `DimDate` table satisfies all Microsoft Power BI Date Dimension requirements:
1. **Contiguous Date Sequence:** Daily records from `2023-01-01` to `2026-12-31` with zero missing days (1,461 rows).
2. **Explicit Data Types:** `full_date` is typed as `Date`, `date_key` is typed as integer `YYYYMMDD`.
3. **Official Marking:** Marked as Date Table in the semantic model with `full_date` as the designated date column.
4. **Time Hierarchy Attributes:**
   - `year` (Integer)
   - `quarter` (1–4)
   - `month_number` (1–12)
   - `month_name` (Text: "January", "February", etc. — sorted by `month_number`)
   - `day_of_month` (1–31)
   - `day_name` (Text: "Monday", "Tuesday", etc. — sorted by `day_of_week`)
   - `is_weekend` (Boolean)

### Dual-Role Date Handling in DAX
- By default, visual slicers on `DimDate` slice orders based on their **Order Placement Date** (`order_date_key`).
- For delivery-completion metrics (e.g., measuring performance based on when goods reached the customer), DAX measures utilize the inactive relationship via:
  ```dax
  Delivered on Date = 
  CALCULATE(
      [Delivered Orders],
      USERELATIONSHIP('DimDate'[date_key], 'FactOrders'[delivery_date_key])
  )
  ```

---

## 5. Column Visibility & Surrogate Key Masking Rules

To ensure a clean, executive-ready Power BI reporting canvas, all technical surrogate keys, join IDs, and internal audit columns are **hidden from report view (`isHidden: true`)**. End users interact solely with natural business descriptors.

| Table | Hidden Technical Columns (`isHidden: true`) | Visible Business Attributes |
|---|---|---|
| `DimDate` | `date_key` | `full_date`, `day_name`, `month_name`, `quarter`, `year`, `is_weekend` |
| `DimHub` | `hub_key`, `hub_id`, `data_origin` | `hub_name`, `city`, `state`, `daily_capacity`, `latitude`, `longitude` |
| `DimDriver` | `driver_key`, `driver_id`, `data_origin` | `driver_name`, `employment_type`, `hire_date`, `experience_years`, `performance_rating` |
| `DimVehicle` | `vehicle_key`, `vehicle_id`, `data_origin` | `vehicle_code`, `vehicle_model`, `vehicle_type`, `current_status`, `lifetime_breakdowns`, `is_maintenance_alert`, `purchase_date` |
| `FactOrders` | `order_date_key`, `delivery_date_key`, `hub_key`, `driver_key`, `vehicle_key`, `data_origin` | `order_id`, `order_status`, `is_delayed`, `is_on_time`, `delay_reason`, `csat_score`, `delivery_time_hours`, `hub_processing_time_hours` |
| `FactHubHourly` | `hub_hourly_id`, `date_key`, `hub_key` | `hour_of_day`, `orders_received`, `orders_dispatched`, `avg_processing_time_hours`, `backlog_volume`, `capacity_utilization_pct` |
| `FactMaintenance` | `vehicle_key`, `data_origin` | `maintenance_id`, `vehicle_code`, `service_type`, `maintenance_status`, `scheduled_date`, `completed_date`, `downtime_hours`, `cost_usd` |
| `FactMLPredictions`| `model_id` | `prediction_id`, `model_name`, `entity_type`, `order_id`, `predicted_label`, `predicted_score`, `prediction_timestamp` |

---

## 6. Measure Organization & Folder Architecture

All business calculations are hosted in a dedicated **`_Measures`** table and classified into five strict display folders:

```
_Measures Table
├── 📁 01 - Executive KPIs
│   ├── [Total Orders]
│   ├── [Delivered Orders]
│   ├── [Cancelled Orders]
│   ├── [Cancellation Rate %]
│   ├── [On-Time Delivery Rate %]
│   ├── [Delay Rate %]
│   └── [Avg CSAT Score]
│
├── 📁 02 - Delivery & SLAs
│   ├── [On-Time Deliveries]
│   ├── [Delayed Deliveries]
│   ├── [Avg Delivery Duration (Hours)]
│   ├── [Delayed Delivery Duration (Hours)]
│   └── [Cumulative Delay Reason %] (Pareto)
│
├── 📁 03 - Hub Operations
│   ├── [Total Hubs]
│   ├── [Network Daily Capacity]
│   ├── [Avg Hub Processing Time (Hours)]
│   ├── [Total Orders Received]
│   ├── [Total Orders Dispatched]
│   └── [Current Backlog Volume]
│
├── 📁 04 - Fleet & Maintenance
│   ├── [Total Fleet Vehicles]
│   ├── [Active Vehicles]
│   ├── [Vehicles In Maintenance]
│   ├── [Fleet Availability Rate %]
│   ├── [Maintenance Alert Vehicles]
│   ├── [Avg Fleet Age (Days)]
│   ├── [Total Maintenance Events]
│   ├── [Total Maintenance Expense]
│   └── [Total Downtime Hours]
│
└── 📁 05 - Driver Metrics
    ├── [Total Drivers]
    ├── [Avg Driver Experience (Years)]
    └── [Avg Driver Rating]
```

---

## 7. Data Source & Power Query Connection Strategy

To guarantee that the Power BI Project (`.pbip`) opens instantly on any machine without requiring PostgreSQL server credentials or complex ODBC setup:
1. **Clean CSV Ingestion:** Tables are sourced from the verified local directory `dashboards/powerbi/data_export/`.
2. **Relative File Paths via Power Query Parameter:** A single Power Query parameter `DataFolderPath` defaults to the local directory path, allowing seamless portability across different developer workstations.
3. **Explicit Type Casting:** Power Query M-scripts strictly enforce column types (`Int64.Type`, `type text`, `type date`, `type number`, `type logical`) before loading into the VertiPaq tabular model.

---

> **Stage 3 Complete. The Star-Schema Semantic Model is fully architected, data integrity validated, and verified with zero orphan foreign keys. Ready to advance to Stage 4: Advanced DAX Engineering.**
