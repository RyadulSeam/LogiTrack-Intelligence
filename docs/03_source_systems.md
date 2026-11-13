# Source Systems & Data Profiling Report
# LogiTrack Intelligence — Phase 1

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-03 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-13 |

---

## 1. Executive Summary

This document captures the audit, physical characteristics, and profiling findings of the four original source CSV datasets delivered for **LogiTrack Intelligence**.

All source files are stored immutably in `data/source/`. No manual alterations were performed on raw source assets.

| Dataset Name | Source File | Row Count | Column Count | File Size | Primary Key |
|---|---|---|---|---|---|
| **Hubs** | `data/source/Hubs.csv` | 6 | 3 | 0.2 KB | `Hub ID` |
| **Drivers** | `data/source/Drivers.csv` | 55 | 6 | 2.4 KB | `DriverID` |
| **Vehicles** | `data/source/Vehicles.csv` | 45 | 7 | 2.3 KB | `Vehicle ID` |
| **Orders** | `data/source/Orders.csv` | 27,979 | 15 | 2.98 MB | `Order ID` |

---

## 2. Source System Profiles

### 2.1 Hubs Dataset (`Hubs.csv`)
* **Business Concept:** Regional distribution centers operating across Texas.
* **Volume:** 6 records (Dallas Main Hub, Houston Hub, Austin Hub, San Antonio Hub, Fort Worth Hub, El Paso Hub).
* **Missing Values:** 0 nulls across all fields (100% complete).
* **Duplicates:** 0 full duplicates, 0 primary key collisions.
* **Observations:**
  - `Hub Capacity` ranges between 150 and 380.
  - The dataset lacks geographic coordinates (Latitude / Longitude), which are needed for route analysis and real-time visualization. Coordinate enrichment is flagged for Phase 2/3.

### 2.2 Drivers Dataset (`Drivers.csv`)
* **Business Concept:** Driver master profiles, employment classifications, and tenure.
* **Volume:** 55 driver records.
* **Missing Values:** 0 nulls (100% complete).
* **Key Fields:**
  - `Employment Type`: Full-time, Part-time, Contract.
  - `Hire Date`: Mixed format strings (`DD-MM-YYYY` and `M/D/YYYY`). Earliest: `2019-01-28`, Latest: `2023-10-15`.
  - `Experience Years`: Range 1–7 years.
  - `Performance Rating`: Integer rating from 3 to 5.

### 2.3 Vehicles Dataset (`Vehicles.csv`)
* **Business Concept:** Fleet assets inventory and operational maintenance alerts.
* **Volume:** 45 fleet vehicles.
* **Missing Values:** 0 nulls (100% complete).
* **Key Fields:**
  - `Vehicle Code`: Alphanumeric identifiers `FT-001` through `FT-045`.
  - `Vehicle Model`: Mercedes Sprinter, Freightliner M2, Chevrolet Express, Chevrolet Silverado, Ford Transit, Isuzu NPR.
  - `Vehicle Status`: Active, Maintenance.
  - `Breakdown`: Numeric breakdown count (range 1–25).
  - `Maintenance count Alert`: Binary alert indicator (0 = Normal, 1 = Maintenance Alert Due).

### 2.4 Orders Dataset (`Orders.csv`)
* **Business Concept:** Historical delivery shipments from January 1, 2023 through December 31, 2024.
* **Volume:** 27,979 delivery orders.
* **Key Fields & Missing Value Breakdown:**
  - `Actual Delivery Date`: 252 missing (0.90%). Exactly matches the 252 cancelled orders.
  - `Delivery Time Hours`: 252 missing (0.90%). Exactly matches the 252 cancelled orders.
  - `Delay Reason`: 22,071 missing (78.88%). Exactly matches the 22,071 on-time orders (`Is Delayed == False`).
  - All other 12 columns: 0 missing values.

---

## 3. Discrepancies & Audit Findings

### Audit Finding AF-01: Driver Name vs Driver ID Discrepancy
* **Issue:** In `Orders.csv`, each `Driver ID` (1–55) maps consistently to a name, but that name does not match the driver's name in `Drivers.csv` (e.g., Driver ID 43 is named "Karen Rodriguez" in Orders, but "Thomas Thomas" in Drivers).
* **Root Cause:** Denormalized operational exports from disconnected systems where driver ID remained the primary relational key but names were captured independently.
* **Resolution Strategy:** `Driver ID` is treated as the authoritative foreign key. Staging and warehouse layers will retain raw names in `raw_orders` and join against `dim_driver` to surface the authoritative master profile.

### Audit Finding AF-02: Heterogeneous Date String Formats
* **Issue:** Across Orders, Drivers, and Vehicles, dates are stored in mixed formats:
  - Hyphenated: `DD-MM-YYYY` (e.g., `25-10-2024`)
  - Slashed: `M/D/YYYY` or `D/M/YYYY` (e.g., `5/7/2024`)
* **Resolution Strategy:** Standardize all timestamp conversions to ISO-8601 (`YYYY-MM-DD`) during Bronze → Silver ETL extraction using explicit parsing rules.

### Audit Finding AF-03: Unassigned Fleet Vehicles
* **Issue:** 4 out of 45 vehicles in `Vehicles.csv` (`FT-014`, `FT-024`, `FT-038`, `FT-042`) have zero orders assigned in historical logs.
* **Assessment:** Real-world valid state. For example, `FT-024` is in `Maintenance` with `Maintenance count Alert = 1`.

### Audit Finding AF-04: Perfect Cancellation & Delay Consistency
* **Issue Verification:**
  - All 252 cancelled orders have `Actual Delivery Date = NULL`, `Delivery Time Hours = NULL`, and `Customer Satisfaction Score = 1`.
  - All 5,908 delayed orders have a documented non-null `Delay Reason`.
  - All 22,071 on-time orders have `Delay Reason = NULL`.
* **Assessment:** Exceptional internal logic consistency; rules confirmed for data quality test automation.
