# Source-to-Target Mapping (STTM)
# LogiTrack Intelligence — Phase 1

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-06 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-13 |

---

## 1. Overview & Layer Architecture

This specification outlines the transformation rules mapping source columns to the Medallion Architecture:
- **Bronze (`raw` schema):** Verbatim column representations + ingestion metadata.
- **Silver (`staging` schema):** Standardized snake_case naming, typed values, cleaned dates.
- **Gold (`warehouse` schema):** Dimension tables (`dim_*`) and Fact tables (`fact_*`).

---

## 2. Hubs Entity Mapping

| Source File Column | Raw Column (`raw.raw_hubs`) | Staging Column (`staging.stg_hubs`) | Warehouse Dimension (`warehouse.dim_hub`) | Transformation Logic |
|---|---|---|---|---|
| `Hub ID` | `hub_id` | `hub_id` | `hub_key` (PK), `hub_id` | Direct integer mapping |
| `HubName` | `hub_name` | `hub_name` | `hub_name`, `city` | Trim whitespace; extract city name |
| `Hub Capacity` | `hub_capacity` | `hub_capacity` | `daily_capacity` | Cast to integer |
| *(Derived)* | `ingestion_batch_id` | `ingestion_batch_id` | `dbt_updated_at` | Added by pipeline metadata |
| *(Derived)* | `data_origin` | `data_origin` | `data_origin` | Default: `'source: original'` |
| *(Enrichment)* | *(None)* | `latitude`, `longitude` | `latitude`, `longitude` | Texas hub coordinates mapped in Silver |

---

## 3. Drivers Entity Mapping

| Source File Column | Raw Column (`raw.raw_drivers`) | Staging Column (`staging.stg_drivers`) | Warehouse Dimension (`warehouse.dim_driver`) | Transformation Logic |
|---|---|---|---|---|
| `DriverID` | `driver_id` | `driver_id` | `driver_key` (PK), `driver_id` | Direct integer mapping |
| `DriverName` | `driver_name` | `driver_name` | `driver_name` | Trim whitespace; authoritative name |
| `Employment Type` | `employment_type` | `employment_type` | `employment_type` | Standardize casing (Full-time / Part-time / Contract) |
| `Hire Date` | `hire_date_raw` | `hire_date` | `hire_date`, `tenure_days` | Parse mixed format to `DATE` (`YYYY-MM-DD`) |
| `Experience Years` | `experience_years` | `experience_years` | `experience_years` | Cast to integer |
| `Performance Rating`| `performance_rating` | `performance_rating` | `performance_rating` | Cast to integer [1–5] |

---

## 4. Vehicles Entity Mapping

| Source File Column | Raw Column (`raw.raw_vehicles`) | Staging Column (`staging.stg_vehicles`) | Warehouse Dimension (`warehouse.dim_vehicle`) | Transformation Logic |
|---|---|---|---|---|
| `Vehicle ID` | `vehicle_id` | `vehicle_id` | `vehicle_key` (PK), `vehicle_id` | Integer ID |
| `Vehicle Code` | `vehicle_code` | `vehicle_code` | `vehicle_code` | Alphanumeric (e.g. `FT-001`), unique natural key |
| `Vehicle Model` | `vehicle_model` | `vehicle_model` | `vehicle_model`, `manufacturer` | Trim, extract manufacturer (e.g. Mercedes) |
| `Vehicle Status` | `vehicle_status` | `vehicle_status` | `current_status` | Standardize category (`Active`, `Maintenance`) |
| `Breakdown` | `breakdown_count` | `breakdown_count` | `lifetime_breakdowns` | Cast to integer |
| `Maintenance count Alert`| `maintenance_alert_raw` | `is_maintenance_alert` | `is_maintenance_alert` | Cast to boolean (`1` -> TRUE, `0` -> FALSE) |
| `Purchase Date` | `purchase_date_raw` | `purchase_date` | `purchase_date`, `fleet_age_days` | Standardize date parsing to ISO `YYYY-MM-DD` |

---

## 5. Orders Entity Mapping

| Source File Column | Raw Column (`raw.raw_orders`) | Staging Column (`staging.stg_orders`) | Warehouse Fact (`warehouse.fact_orders`) | Transformation Logic |
|---|---|---|---|---|
| `Order ID` | `order_id` | `order_id` | `order_id` (PK) | Bigint cast |
| `Order Date` | `order_date_raw` | `order_date` | `order_date_key`, `order_date` | Standardize date; generate integer date key (`YYYYMMDD`) |
| `Actual Delivery Date` | `actual_delivery_date_raw` | `actual_delivery_date` | `delivery_date_key`, `delivery_date` | Standardize date; handle NULLs for cancelled orders |
| `Order Status` | `order_status` | `order_status` | `order_status` | Categorical: `Delivered`, `Cancelled` |
| `Is Delayed` | `is_delayed` | `is_delayed` | `is_delayed` | Boolean cast |
| `Is On Time` | `is_on_time` | `is_on_time` | `is_on_time` | Boolean cast |
| `Delay Reason` | `delay_reason` | `delay_reason` | `delay_reason` | String or `'None'` for on-time |
| `Driver ID` | `driver_id` | `driver_id` | `driver_key` (FK) | Reference to `dim_driver` |
| `Driver Name` | `order_driver_name_snapshot`| `driver_name_snapshot` | *(Preserved for audit)* | Driver name snapshot recorded on delivery sheet |
| `Hub Name` | `hub_name` | `hub_name` | `hub_key` (FK) | Foreign key resolved via `dim_hub.hub_name` |
| `Vehicle Name` | `vehicle_code` | `vehicle_code` | `vehicle_key` (FK) | Foreign key resolved via `dim_vehicle.vehicle_code` |
| `Vehicle Type` | `vehicle_type` | `vehicle_type` | `vehicle_type` | Categorical |
| `Customer Satisfaction Score`| `customer_satisfaction_score` | `csat_score` | `csat_score` | Smallint [1–5] |
| `Delivery Time Hours` | `delivery_time_hours` | `delivery_time_hours` | `delivery_time_hours` | Decimal(8,2), NULL if cancelled |
| `Hub Processing Time Hours` | `hub_processing_time_hours` | `hub_processing_time_hours` | `hub_processing_time_hours` | Decimal(6,2) |
