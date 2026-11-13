# Data Quality Rules & Governance Policy
# LogiTrack Intelligence — Phase 1

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-05 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-13 |

---

## 1. Governance Objectives

Data quality rules define the constraints and operational standards that ingested data must meet before moving from the **Bronze (Raw)** layer to the **Silver (Staging)** and **Gold (Warehouse)** layers.

Failure to satisfy a **Critical** rule forces the record into `data/quarantine/` with an audit reason tag.

---

## 2. Data Quality Rules Matrix

| Rule ID | Entity | Target Column(s) | Rule Logic | Severity | Action on Failure |
|---|---|---|---|---|---|
| **DQ-001** | All | Primary Key (`Order ID`, `DriverID`, `Vehicle ID`, `Hub ID`) | Must be strictly unique and non-null | Critical | Quarantine duplicate row |
| **DQ-002** | Orders | `Driver ID` | Must exist in `Drivers.DriverID` master | Critical | Quarantine record (Orphan FK) |
| **DQ-003** | Orders | `Hub Name` | Must exist in `Hubs.HubName` master | Critical | Quarantine record (Orphan FK) |
| **DQ-004** | Orders | `Vehicle Name` | Must match a valid `Vehicles.Vehicle Code` | Critical | Quarantine record (Orphan FK) |
| **DQ-005** | Orders | `Order Status`, `Actual Delivery Date` | If `Order Status = 'Cancelled'`, `Actual Delivery Date` and `Delivery Time Hours` MUST be NULL | Critical | Log warning & quarantine |
| **DQ-006** | Orders | `Is Delayed`, `Delay Reason` | If `Is Delayed = TRUE`, `Delay Reason` must be non-null; if `FALSE`, must be NULL | Medium | Set default reason or alert |
| **DQ-007** | Orders | `Order Date`, `Actual Delivery Date` | `Actual Delivery Date` must be >= `Order Date` | Critical | Quarantine record |
| **DQ-008** | Orders | `Is Delayed`, `Is On Time` | Must be strictly opposite boolean values (`Is Delayed != Is On Time`) | Critical | Recompute flag |
| **DQ-009** | Drivers, Orders | Scores & Ratings | `Performance Rating` and `Customer Satisfaction Score` must fall within range `[1, 5]` | High | Cap/Flag anomaly |
| **DQ-010** | Vehicles | `Maintenance count Alert` | Must be binary `0` or `1` | Medium | Coerce to 0/1 |

---

## 3. Quarantine & Anomaly Handling Policy

When records violate critical rules during the Batch ETL Pipeline (Phase 4):
1. **Quarantine Directory:** Written to `data/quarantine/{batch_id}_{entity}_rejected.csv`.
2. **Rejection Audit Table:** Ingested into `realtime.ingestion_errors` or logged in `pipeline_audit`.
3. **Immutability:** Original files in `data/source/` are never overwritten or altered.
