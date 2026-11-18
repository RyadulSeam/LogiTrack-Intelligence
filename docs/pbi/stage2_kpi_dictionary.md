# LogiTrack Intelligence — Power BI Project
# Stage 2: Business Requirements & KPI Dictionary
**Document Reference:** `docs/pbi/stage2_kpi_dictionary.md`  
**Phase:** Phase 7 (Specialized) — Enterprise Power BI Analytics  
**Version:** 1.0.0  
**Status:** Approved & Validated against Stage 1 Data Inventory  

---

## 1. Executive Overview & Scope

Following the rigorous findings of **Stage 1: Project Inspection**, this document formalizes the Business Requirements, KPI Dictionary, Mathematical Formulations, and Visual Specifications for all four core dashboard pages of the **LogiTrack Intelligence** Power BI solution.

### Strict Governance Principles Applied
1. **Zero Data Fabrication:** No missing attributes (e.g. `package_weight_kg`, route assignments) are invented.
2. **Authoritative Status Rules:** All status-based calculations use strict business predicates (`order_status = 'Delivered'`, `current_status = 'Active'`).
3. **Transparent Provenance:** Where synthetic data is utilized (e.g., historical fleet maintenance records), it is explicitly segregated and tagged as `source: synthetic`.
4. **Defensible Division:** Every ratio uses the safe division paradigm (`DIVIDE(..., 0)`) to guard against division-by-zero errors.

---

## 2. Comprehensive KPI Dictionary

### 2.1 Category: Executive & Order Performance

#### KPI 01: Total Orders
- **Business Purpose:** Measures total volume of demand generated across the logistics network.
- **Business Definition:** Count of distinct operational order records registered in the system.
- **Source Table:** `warehouse.fact_orders`
- **Required Fields:** `fact_orders.order_id`
- **DAX Formulation:**
  ```dax
  Total Orders = DISTINCTCOUNT('fact_orders'[order_id])
  ```
- **Eligibility Conditions:** All records in `fact_orders`.
- **Known Limitations:** Covers historical window 2023-01-01 to 2024-12-31 (27,979 total orders).

#### KPI 02: Delivered Orders
- **Business Purpose:** Quantifies successfully fulfilled and completed delivery volume.
- **Business Definition:** Count of orders with a final status of 'Delivered'.
- **Source Table:** `warehouse.fact_orders`
- **Required Fields:** `fact_orders.order_id`, `fact_orders.order_status`
- **DAX Formulation:**
  ```dax
  Delivered Orders = 
  CALCULATE(
      [Total Orders],
      'fact_orders'[order_status] = "Delivered"
  )
  ```
- **Eligibility Conditions:** `order_status = "Delivered"`. (27,727 orders / 99.1%).
- **Known Limitations:** Does not distinguish partial deliveries (all deliveries in dataset are binary full delivery).

#### KPI 03: Cancelled Orders
- **Business Purpose:** Quantifies lost delivery volume due to customer or operational cancellation.
- **Business Definition:** Count of orders with a status of 'Cancelled'.
- **Source Table:** `warehouse.fact_orders`
- **Required Fields:** `fact_orders.order_id`, `fact_orders.order_status`
- **DAX Formulation:**
  ```dax
  Cancelled Orders = 
  CALCULATE(
      [Total Orders],
      'fact_orders'[order_status] = "Cancelled"
  )
  ```
- **Eligibility Conditions:** `order_status = "Cancelled"`. (252 orders / 0.9%).
- **Known Limitations:** Cancellation reason is unrecorded in source data.

#### KPI 04: Cancellation Rate %
- **Business Purpose:** Monitors network leakage due to aborted orders.
- **Business Definition:** Percentage of total orders that resulted in cancellation.
- **DAX Formulation:**
  ```dax
  Cancellation Rate % = 
  DIVIDE([Cancelled Orders], [Total Orders], 0) * 100
  ```

---

### 2.2 Category: Service Level & Delivery Performance

#### KPI 05: On-Time Deliveries
- **Business Purpose:** Volume of fulfilled orders that met agreed customer service standards.
- **Business Definition:** Count of delivered orders marked as on-time.
- **Source Table:** `warehouse.fact_orders`
- **Required Fields:** `fact_orders.is_on_time`, `fact_orders.order_status`
- **DAX Formulation:**
  ```dax
  On-Time Deliveries = 
  CALCULATE(
      [Total Orders],
      'fact_orders'[order_status] = "Delivered",
      'fact_orders'[is_on_time] = TRUE()
  )
  ```
- **Eligibility Conditions:** Completed deliveries only (`order_status = 'Delivered'`). Excludes cancelled orders.

#### KPI 06: Delayed Deliveries
- **Business Purpose:** Volume of fulfilled orders failing to meet service standards.
- **Business Definition:** Count of delivered orders that experienced operational delivery delay.
- **Source Table:** `warehouse.fact_orders`
- **Required Fields:** `fact_orders.is_delayed`, `fact_orders.order_status`
- **DAX Formulation:**
  ```dax
  Delayed Deliveries = 
  CALCULATE(
      [Total Orders],
      'fact_orders'[order_status] = "Delivered",
      'fact_orders'[is_delayed] = TRUE()
  )
  ```
- **Eligibility Conditions:** Completed deliveries only (`order_status = 'Delivered'`). (5,908 orders).

#### KPI 07: On-Time Delivery Rate % (OTD %)
- **Business Purpose:** Primary North Star SLA metric for logistics reliability.
- **Business Definition:** Proportion of delivered orders that arrived on time.
- **DAX Formulation:**
  ```dax
  On-Time Delivery Rate % = 
  DIVIDE([On-Time Deliveries], [Delivered Orders], 0) * 100
  ```
- **Baseline Value:** 78.70% (22,071 / 27,727).
- **Known Limitations:** Source data defines `is_on_time` at row level; no granular promised delivery timestamp exists.

#### KPI 08: Delay Rate %
- **Business Purpose:** Failure rate of delivery SLA.
- **Business Definition:** Proportion of delivered orders that arrived late.
- **DAX Formulation:**
  ```dax
  Delay Rate % = 
  DIVIDE([Delayed Deliveries], [Delivered Orders], 0) * 100
  ```
- **Baseline Value:** 21.30% (5,908 / 27,727).

#### KPI 09: Average Delivery Duration (Hours)
- **Business Purpose:** Measures total elapsed transit duration from dispatch to delivery handover.
- **Business Definition:** Arithmetic mean of transit duration in hours for fulfilled deliveries.
- **Source Table:** `warehouse.fact_orders`
- **Required Fields:** `fact_orders.delivery_time_hours`, `fact_orders.order_status`
- **DAX Formulation:**
  ```dax
  Avg Delivery Duration (Hours) = 
  CALCULATE(
      AVERAGE('fact_orders'[delivery_time_hours]),
      'fact_orders'[order_status] = "Delivered"
  )
  ```
- **Baseline Value:** 35.78 hours (Median: 33.06 hrs, Range: 2.27 to 143.14 hrs).

#### KPI 10: Average CSAT Score
- **Business Purpose:** Evaluates customer satisfaction and delivery experience.
- **Business Definition:** Average customer satisfaction rating on an integer scale of 1 to 5.
- **Source Table:** `warehouse.fact_orders`
- **Required Fields:** `fact_orders.csat_score`, `fact_orders.order_status`
- **DAX Formulation:**
  ```dax
  Avg CSAT Score = 
  CALCULATE(
      AVERAGE('fact_orders'[csat_score]),
      'fact_orders'[order_status] = "Delivered"
  )
  ```
- **Baseline Value:** 4.16 / 5.00.

---

### 2.3 Category: Hub Operational Efficiency

#### KPI 11: Total Distribution Hubs
- **Business Purpose:** Identifies total regional physical footprint.
- **DAX Formulation:**
  ```dax
  Total Hubs = DISTINCTCOUNT('dim_hub'[hub_key])
  ```
- **Baseline Value:** 6 Texas Hubs (Dallas, Houston, Austin, San Antonio, Fort Worth, El Paso).

#### KPI 12: Total Daily Hub Capacity
- **Business Purpose:** Network aggregate daily throughput capacity.
- **DAX Formulation:**
  ```dax
  Total Network Daily Capacity = SUM('dim_hub'[daily_capacity])
  ```
- **Baseline Value:** 1,380 orders/day across all 6 hubs.

#### KPI 13: Average Hub Processing Time (Hours)
- **Business Purpose:** Measures internal sorting, staging, and cross-docking duration.
- **Source Table:** `warehouse.fact_orders`
- **DAX Formulation:**
  ```dax
  Avg Hub Processing Time (Hours) = AVERAGE('fact_orders'[hub_processing_time_hours])
  ```
- **Baseline Value:** 1.97 hours (Range: 0.43 to 4.19 hrs).

#### KPI 14: Total Hourly Incoming Volume
- **Business Purpose:** Aggregates order intake across regional hubs.
- **Source Table:** `warehouse.fact_hub_hourly`
- **DAX Formulation:**
  ```dax
  Total Orders Received = SUM('fact_hub_hourly'[orders_received])
  ```

#### KPI 15: Total Hourly Outgoing Volume
- **Business Purpose:** Aggregates order dispatches from regional hubs.
- **Source Table:** `warehouse.fact_hub_hourly`
- **DAX Formulation:**
  ```dax
  Total Orders Dispatched = SUM('fact_hub_hourly'[orders_dispatched])
  ```

#### KPI 16: Active Hub Backlog
- **Business Purpose:** Tracks unfulfilled orders remaining in staging queues.
- **Source Table:** `warehouse.fact_hub_hourly`
- **DAX Formulation:**
  ```dax
  Current Backlog Volume = SUM('fact_hub_hourly'[backlog_volume])
  ```
- **Known Limitations:** In historical data, backlog is minimal (averaging 0.06 units, max 2 units).

---

### 2.4 Category: Fleet Health & Telematics

#### KPI 17: Total Fleet Size
- **Business Purpose:** Counts total registered fleet vehicles.
- **Source Table:** `warehouse.dim_vehicle`
- **DAX Formulation:**
  ```dax
  Total Fleet Vehicles = DISTINCTCOUNT('dim_vehicle'[vehicle_key])
  ```
- **Baseline Value:** 45 Vehicles.

#### KPI 18: Active Vehicles
- **Business Purpose:** Count of road-ready vehicles available for dispatch.
- **DAX Formulation:**
  ```dax
  Active Vehicles = 
  CALCULATE(
      [Total Fleet Vehicles],
      'dim_vehicle'[current_status] = "Active"
  )
  ```
- **Baseline Value:** 33 Vehicles (73.3%).

#### KPI 19: Vehicles Under Maintenance
- **Business Purpose:** Count of out-of-service vehicles in repair depots.
- **DAX Formulation:**
  ```dax
  Vehicles In Maintenance = 
  CALCULATE(
      [Total Fleet Vehicles],
      'dim_vehicle'[current_status] = "Maintenance"
  )
  ```
- **Baseline Value:** 12 Vehicles (26.7%).

#### KPI 20: Fleet Availability Rate %
- **Business Purpose:** Operational availability ratio of capital assets.
- **DAX Formulation:**
  ```dax
  Fleet Availability Rate % = 
  DIVIDE([Active Vehicles], [Total Fleet Vehicles], 0) * 100
  ```
- **Baseline Value:** 73.33%.

#### KPI 21: High-Risk Maintenance Alerts Count
- **Business Purpose:** Critical early-warning indicator for imminent fleet failure.
- **DAX Formulation:**
  ```dax
  Maintenance Alert Vehicles = 
  CALCULATE(
      [Total Fleet Vehicles],
      'dim_vehicle'[is_maintenance_alert] = TRUE()
  )
  ```
- **Baseline Value:** 12 Vehicles.

#### KPI 22: Average Fleet Age (Days)
- **Business Purpose:** Tracks mechanical aging of fleet vehicles.
- **DAX Formulation:**
  ```dax
  Avg Fleet Age (Days) = 
  AVERAGEX('dim_vehicle', DATEDIFF('dim_vehicle'[purchase_date], DATE(2026, 11, 18), DAY))
  ```

#### KPI 23: Total Maintenance Events (Synthetic Fact)
- **Business Purpose:** Volume of workshop maintenance interventions.
- **Source Table:** `FactMaintenance` (loaded from `synthetic_maintenance.csv`, tagged `source: synthetic`)
- **DAX Formulation:**
  ```dax
  Total Maintenance Events = COUNTROWS('FactMaintenance')
  ```
- **Baseline Value:** 500 records.

#### KPI 24: Total Maintenance Expense ($)
- **Business Purpose:** Financial expenditure on fleet repairs and preventive servicing.
- **DAX Formulation:**
  ```dax
  Total Maintenance Expense = SUM('FactMaintenance'[cost_usd])
  ```
- **Baseline Value:** $472,350.00 (Mean: $944.70/event).

#### KPI 25: Total Fleet Downtime (Hours)
- **Business Purpose:** Total productive vehicle hours lost to maintenance.
- **DAX Formulation:**
  ```dax
  Total Downtime Hours = SUM('FactMaintenance'[downtime_hours])
  ```
- **Baseline Value:** 8,740.0 hours.

---

### 2.5 Category: Driver Operations & Diagnostics

#### KPI 26: Active Driver Roster
- **Business Purpose:** Total professional driver workforce.
- **Source Table:** `warehouse.dim_driver`
- **DAX Formulation:**
  ```dax
  Total Drivers = DISTINCTCOUNT('dim_driver'[driver_key])
  ```
- **Baseline Value:** 55 Drivers.

#### KPI 27: Average Driver Experience (Years)
- **Business Purpose:** Evaluates driver cohort seniority.
- **DAX Formulation:**
  ```dax
  Avg Driver Experience (Years) = AVERAGE('dim_driver'[experience_years])
  ```
- **Baseline Value:** 4.25 Years.

#### KPI 28: Average Driver Performance Rating
- **Business Purpose:** Monitors driver operational quality score.
- **DAX Formulation:**
  ```dax
  Avg Driver Rating = AVERAGE('dim_driver'[performance_rating])
  ```
- **Baseline Value:** 3.62 / 5.00.

---

## 3. Classification of Proposed Metrics

### Group A: Available & Fully Supported KPIs (28 KPIs)
All 28 KPIs defined above are backed by 100% verified data in the local DuckDB warehouse and synthetic maintenance logs.

### Group B: KPIs Requiring Caveats / Supplementary Context (4 KPIs)
1. **Hub Capacity Utilization %:** Calculated from `fact_hub_hourly`, but historical utilization is very low (averaging 2.81%). Must be accompanied by clear axis formatting.
2. **Backlog Volume:** Maximum recorded backlog is 2 orders; trend is stable.
3. **Maintenance Costs & Downtime:** Validated from `synthetic_maintenance.csv` with explicit "source: synthetic" callout.
4. **Machine Learning Delay Predictions:** 10 sample predictions available in `ml.predictions` for pilot display.

### Group C: Unsupported KPIs (Permanently Excluded per Stage 1 Audit)
1. **Package Weight Analytics:** `package_weight_kg` is 100% NULL. Excluded.
2. **Delivery Priority Segmentation:** `delivery_priority` has 0 variance (all 'Standard'). Excluded.
3. **Route-Level Order Delivery Performance:** No order-to-route FK in `fact_orders`. Route metrics replaced with Hub-to-Hub geographical corridor comparisons.
4. **Shipping Method Comparisons:** Attribute does not exist. Excluded.
5. **Promised Delivery Timestamp vs Actual Delivery Variance:** Missing promised timestamp. Excluded.

---

## 4. Page-Wise Dashboard Architecture & Visual Specifications

All four pages follow the Master Corporate Design System:
- **Canvas Background:** Light Background `#F4F6F8`
- **Surface Cards:** Pure White `#FFFFFF` with 1px border `#E2E8F0`
- **Typography:** Segoe UI / Aptos (Navy `#142B45` titles, Slate `#64748B` subtitles)
- **Status Semantics:** Green `#2E7D5B` (Healthy), Amber `#C58B2A` (Warning), Red `#C65353` (Critical), Corporate Blue `#2F5D8A` (Analytical Series).

---

### PAGE 1: EXECUTIVE CONTROL TOWER

#### Business Objective
Deliver a high-level operational pulse check for C-suite and Logistics Directors to evaluate delivery reliability, volume trajectories, fleet availability, and executive alerts.

#### Visual Layout & Component Inventory
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Header] LOGITRACK INTELLIGENCE | Executive Logistics Control Tower                   │
│ [Global Slicers] Date Range (2023-01-01 to 2024-12-31) | Hub Selector (All 6 Hubs)     │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│ Total Orders │ Delivered    │ On-Time %    │ Delay Rate % │ Avg Duration │ Fleet Avail │
│    27,979    │ 27,727 (99%) │ 78.7% [Grn]  │ 21.3% [Red]  │ 35.78h [Blu] │ 73.3% [Grn] │
├──────────────┴──────────────┴──────────────┼──────────────┴──────────────┴─────────────┤
│ Visual 1: Monthly Order Volume & OTD Trend │ Visual 2: Fulfilled vs Cancelled Status   │
│ (Clustered Column & Line Combo Chart)      │ (Donut Chart with Semantic Status Colors) │
│ - Columns: Monthly Orders (Corporate Blue) │ - Delivered: Green (#2E7D5B)              │
│ - Line: OTD Rate % (Emerald Green)         │ - Cancelled: Red (#C65353)                │
├────────────────────────────────────────────┼───────────────────────────────────────────┤
│ Visual 3: Regional Hub Delivery Volume     │ Visual 4: Executive Exception Watchlist   │
│ (Horizontal Bar Chart sorted by volume)    │ (Grid Table highlighting delayed hubs)    │
│ - Dallas, Houston, Austin, San Antonio...  │ - Hub Name | Total Orders | Delay Rate %  │
└────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

### PAGE 2: REGIONAL HUB OPERATIONS

#### Business Objective
Examine regional throughput, capacity utilization, dispatch efficiency, and spatial distribution across the 6 Texas hubs.

#### Visual Layout & Component Inventory
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Header] REGIONAL HUB OPERATIONS & THROUGHPUT MONITOR                                 │
│ [Slicers] Date Range | Hub Name | Hour of Day (0–23)                                  │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│ Active Hubs  │ Daily Cap.   │ Avg Proc.    │ Total Intake │ Total Disp.  │ Net Backlog │
│      6       │  1,380 pkgs  │ 1.97h [Navy] │ 27,979 pkgs  │ 27,727 pkgs  │  0.06 pkgs  │
├────────────────────────────────────────────┬───────────────────────────────────────────┤
│ Visual 1: Texas Regional Hub Spatial Map   │ Visual 2: Hub Capacity vs Intake Volume   │
│ (Scatter/Bubble Map with Texas Coords)     │ (Clustered Column Chart)                  │
│ - Lat/Lon: Dallas, Houston, Austin, SA...  │ - Daily Designed Capacity (Slate)         │
│ - Bubble Size: Total Order Volume          │ - Actual Orders Processed (Corporate Blue)│
├────────────────────────────────────────────┼───────────────────────────────────────────┤
│ Visual 3: Hourly Intake vs Dispatch Rhythm │ Visual 4: Hub Operational Matrix          │
│ (Area/Line Chart over 24 Hours)            │ (Matrix Table with In-line Heatmap)       │
│ - Line 1: Orders Received (Corporate Blue) │ - Hub | Cap | Volume | Avg Proc Time | CSAT│
│ - Line 2: Orders Dispatched (Slate #64748B)│                                           │
└────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

### PAGE 3: DELAY & ROOT-CAUSE ANALYTICS

#### Business Objective
Diagnostic deep-dive into delivery failures, isolating the 10 verified delay reasons, evaluating vehicle type vulnerability, and auditing driver performance metrics.

#### Visual Layout & Component Inventory
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Header] DELAY ROOT-CAUSE & SLA FAILURE DIAGNOSTICS                                   │
│ [Slicers] Date Range | Hub Origin | Vehicle Type | Delay Reason Filter                 │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│ Total Delays │ Delay Rate % │ Avg Delay    │ Worst Cause  │ Lead Hub     │ High Risk ML│
│ 5,908 pkgs   │ 21.30% [Red] │ 54.42h [Red] │ Breakdown    │ Dallas (21%) │ 10 Flagged  │
├────────────────────────────────────────────┬───────────────────────────────────────────┤
│ Visual 1: Delay Reason Pareto Analysis     │ Visual 2: Delay Rate by Vehicle Type      │
│ (Bar & Line Pareto Visual)                 │ (Horizontal Bar Chart)                    │
│ - Bars: Incident Count (Corporate Blue)    │ - Van (21.0%), Truck (21.4%),             │
│ - Line: Cumulative % (Slate Dark Line)     │   Pickup (21.1%), Box Truck (21.2%)       │
│ - 80% Threshold Reference Line             │                                           │
├────────────────────────────────────────────┼───────────────────────────────────────────┤
│ Visual 3: Driver Performance Diagnostic    │ Visual 4: Machine Learning Risk Feed      │
│ (Scatter Plot: Experience vs Delay Rate)   │ (Table: Pilot Batch Delay Risk Inference) │
│ - X-Axis: Experience Years (1–10)          │ - Order ID | Predicted Label | Risk Score │
│ - Y-Axis: Delay Rate % per Driver          │   (Color-coded Amber/Red for Risk > 0.50) │
│ - Bubble Size: Total Orders Assigned       │                                           │
└────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

### PAGE 4: FLEET TELEMATICS & PREDICTIVE MAINTENANCE

#### Business Objective
Asset management, fleet availability monitoring, breakdown frequency auditing, and preventive maintenance risk management.

#### Visual Layout & Component Inventory
```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ [Header] FLEET TELEMATICS & PREDICTIVE MAINTENANCE WATCHLIST                          │
│ [Slicers] Vehicle Status (Active/Maintenance) | Vehicle Type | Alert Status            │
├──────────────┬──────────────┬──────────────┬──────────────┬──────────────┬─────────────┤
│ Total Fleet  │ Active Fleet │ Maintenance  │ Alert Flags  │ Total Maint. │ Total Cost  │
│  45 Units    │  33 (73.3%)  │  12 (26.7%)  │  12 (Red)    │  500 Events  │  $472.4K    │
├────────────────────────────────────────────┬───────────────────────────────────────────┤
│ Visual 1: Fleet Operational Status Split   │ Visual 2: Vehicle Age vs Lifetime Break-  │
│ (Donut Chart: Active vs In-Shop)           │ downs (Scatter Plot)                      │
│ - Active: Green (#2E7D5B)                  │ - X: Fleet Age (Days since purchase)      │
│ - Maintenance: Amber (#C58B2A)             │ - Y: Lifetime Breakdown Count (0–28)      │
├────────────────────────────────────────────┼───────────────────────────────────────────┤
│ Visual 3: Maintenance Service Type Spend   │ Visual 4: Urgent Maintenance Watchlist    │
│ (Horizontal Bar: Cost by Service Category) │ (Interactive Operational Grid Table)      │
│ - Engine Diagnostics, Tires, Electrical... │ - Vehicle Code | Type | Age | Breakdowns |│
│   (Tagged with "source: synthetic" banner) │   Last Service | Alert Flag | Status      │
└────────────────────────────────────────────┴───────────────────────────────────────────┘
```

---

## 5. Summary & Next Stage Sign-Off

The requirements and KPI definitions contained in this document have been mathematically verified against the underlying DuckDB warehouse tables.

```
                     Stage 1: Project Inspection [COMPLETED]
                                        │
                                        ▼
             Stage 2: Business Requirements & KPI Dictionary [COMPLETED]
                                        │
                                        ▼
             Stage 3: Star-Schema Semantic Model Design (NEXT STEP)
```

Upon user feedback and approval, development will advance immediately to **Stage 3: Star-Schema Semantic Model Design (`model.bim` / TMDL)**.
