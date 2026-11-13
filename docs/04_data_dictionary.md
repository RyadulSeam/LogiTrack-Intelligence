# Data Dictionary
# LogiTrack Intelligence — Phase 1

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-04 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-13 |

---

## 1. Hubs Master Entity (`Hubs.csv`)

| Column Name | Inferred Source Type | Target SQL Type | Nullable | Primary Key | Description & Business Rules |
|---|---|---|---|---|---|
| `Hub ID` | Integer | `INTEGER` | No | Yes | Unique identifier for regional distribution hub (1–6). |
| `HubName` | String | `VARCHAR(100)` | No | No | Official hub name (e.g., Dallas Main Hub, Houston Hub). Unique across records. |
| `Hub Capacity` | Integer | `INTEGER` | No | No | Operating throughput capacity limit (range: 150–380). |

---

## 2. Drivers Master Entity (`Drivers.csv`)

| Column Name | Inferred Source Type | Target SQL Type | Nullable | Primary Key | Description & Business Rules |
|---|---|---|---|---|---|
| `DriverID` | Integer | `INTEGER` | No | Yes | Unique driver personnel ID (1–55). |
| `DriverName` | String | `VARCHAR(100)` | No | No | Official legal name of driver in HR master. |
| `Employment Type` | String | `VARCHAR(50)` | No | No | Driver contract classification: `Full-time`, `Part-time`, `Contract`. |
| `Hire Date` | String | `DATE` | No | No | Date hired. Converted from mixed formats (`DD-MM-YYYY` / `M/D/YYYY`) to ISO `YYYY-MM-DD`. |
| `Experience Years` | Integer | `INTEGER` | No | No | Cumulative logistics driving experience (range: 1–7). |
| `Performance Rating` | Integer | `INTEGER` | No | No | Operational evaluation score (integer 3 to 5). |

---

## 3. Vehicles Master Entity (`Vehicles.csv`)

| Column Name | Inferred Source Type | Target SQL Type | Nullable | Primary Key | Description & Business Rules |
|---|---|---|---|---|---|
| `Purchase Date` | String | `DATE` | No | No | Fleet acquisition date. Standardized to ISO `YYYY-MM-DD`. |
| `Vehicle ID` | Integer | `INTEGER` | No | Yes | Internal numeric asset primary key (1–45). |
| `Vehicle Model` | String | `VARCHAR(100)` | No | No | Vehicle make and model (e.g., Mercedes Sprinter, Freightliner M2). |
| `Vehicle Status` | String | `VARCHAR(50)` | No | No | Asset state: `Active`, `Maintenance`. |
| `Breakdown` | Integer | `INTEGER` | No | No | Lifetime breakdown incidents recorded (1–25). |
| `Maintenance count Alert`| Integer | `SMALLINT` | No | No | Binary maintenance warning flag: `0` = OK, `1` = Service Required. |
| `Vehicle Code` | String | `VARCHAR(20)` | No | No | Operational call-sign (e.g., `FT-001` to `FT-045`). Unique natural key. |

---

## 4. Orders Transaction Entity (`Orders.csv`)

| Column Name | Inferred Source Type | Target SQL Type | Nullable | Primary Key | Foreign Key | Description & Business Rules |
|---|---|---|---|---|---|---|
| `Order ID` | Integer | `BIGINT` | No | Yes | No | Unique transaction identifier (1–27,979). |
| `Order Date` | String | `DATE` | No | No | No | Date order was placed. Range: 2023-01-01 to 2024-12-31. |
| `Actual Delivery Date` | String | `DATE` | Yes | No | No | Date delivery concluded. `NULL` if order was cancelled. |
| `Order Status` | String | `VARCHAR(30)` | No | No | No | Lifecycle status: `Delivered` (27,727) or `Cancelled` (252). |
| `Is Delayed` | Boolean | `BOOLEAN` | No | No | No | Flag indicating if delivery exceeded SLA (`TRUE` or `FALSE`). |
| `Is On Time` | Boolean | `BOOLEAN` | No | No | No | Inverse of `Is Delayed`. Validated mutually exclusive. |
| `Delay Reason` | String | `VARCHAR(100)` | Yes | No | No | Root cause for delay. Mandatory when `Is Delayed = TRUE`; `NULL` otherwise. |
| `Driver ID` | Integer | `INTEGER` | No | No | `Drivers.DriverID` | Assigned driver ID. Validated referential integrity. |
| `Driver Name` | String | `VARCHAR(100)` | No | No | No | Operational driver display label at shipment dispatch. |
| `Hub Name` | String | `VARCHAR(100)` | No | No | `Hubs.HubName` | Processing hub. Validated against `Hubs.HubName`. |
| `Vehicle Name` | String | `VARCHAR(20)` | No | No | `Vehicles.Vehicle Code` | Fleet code assigned (e.g. `FT-036`). Matches `Vehicle Code`. |
| `Vehicle Type` | String | `VARCHAR(50)` | No | No | No | Operational vehicle class: `Van`, `Truck`, `Pickup`, `Box Truck`. |
| `Customer Satisfaction Score` | Integer | `SMALLINT` | No | No | No | CSAT rating (integer 1–5). Cancelled orders always receive `1`. |
| `Delivery Time Hours` | Float | `NUMERIC(8,2)` | Yes | No | No | Total delivery transit duration in hours. `NULL` for cancelled orders. |
| `Hub Processing Time Hours` | Float | `NUMERIC(6,2)` | No | No | No | Duration package was staged inside distribution center. Range: 0.43–4.19 hrs. |
