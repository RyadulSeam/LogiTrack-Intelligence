# Batch ETL Pipeline Architecture & Design
# LogiTrack Intelligence — Phase 4

## Document Information

| Field | Value |
|---|---|
| Document ID | DOC-10 |
| Version | 1.0 |
| Status | Approved |
| Author | Ryadul Seam |
| Last Updated | 2026-11-13 |

---

## 1. Pipeline Overview

The LogiTrack Batch Ingestion Pipeline provides automated, deterministic, and idempotent ETL processing for historical enterprise logistics data.

```
┌─────────────────────────────────────────────────────────────┐
│                       EXTRACT LAYER                         │
│  Hubs.csv · Drivers.csv · Vehicles.csv · Orders.csv         │
│  - File existence & encoding verification                   │
│  - SHA256 cryptographic checksum generation                 │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 CLEAN & STANDARDIZE LAYER                   │
│  - Whitespace trimming across object/string fields          │
│  - Mixed date parsing (DD-MM-YYYY & M/D/YYYY ➔ YYYY-MM-DD)  │
│  - Type casting (numeric, boolean)                          │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                      TRANSFORM LAYER                        │
│  - Canonical snake_case naming                              │
│  - Texas Hub geospatial coordinate enrichment (Lat/Lon)     │
│  - Driver name snapshot preservation                        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 DATA QUALITY GATE & QUARANTINE              │
│  - Evaluates DQ-001 through DQ-010 rules                    │
│  - Valid records ──────────────► Clean Staging Set          │
│  - Failed records ─────────────► data/quarantine/ (CSV)     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     LOAD & AUDIT LAYER                      │
│  - Idempotent load to raw.* (Bronze)                        │
│  - Idempotent load to staging.* (Silver)                    │
│  - Execution metrics appended to pipeline_audit.csv         │
└─────────────────────────────────────────────────────────────┘
```

---

## 2. Pipeline Modules (`src/logitrack/ingestion/`)

| Module | Primary Responsibility |
|---|---|
| `extract.py` | Validates file existence, generates SHA256 hashes, extracts raw records |
| `clean.py` | Whitespace stripping, mixed date format resolution, boolean parsing |
| `transform.py` | Transforms to canonical staging schema, injects Texas hub coordinates |
| `quality_gate.py` | Enforces PK uniqueness, FK referential integrity, routes failures to quarantine |
| `load.py` | Idempotent atomic load into DuckDB (and Neon PostgreSQL if configured) |
| `audit.py` | Persists run metrics (`run_id`, start/end times, durations, row counts) |
| `pipeline.py` | Master orchestrator coordinating the complete workflow |

---

## 3. Data Lineage & Checksum Verification

Every execution captures the SHA256 checksum of source files:

| Dataset | Records | Source Checksum (SHA-256 Prefix) |
|---|---|---|
| `Hubs.csv` | 6 | `e4f2af44...` |
| `Drivers.csv` | 55 | `04d450f3...` |
| `Vehicles.csv` | 45 | `48b85d2f...` |
| `Orders.csv` | 27,979 | `49506c9b...` |

Lineage metadata (`ingestion_batch_id`, `data_origin`, `source_file`, `loaded_at`) is stamped on every Bronze and Silver table record.

---

## 4. Quarantine Mechanics

When a record fails a critical check (e.g. Missing primary key, foreign key not found in master table):
1. The record is diverted from the load set.
2. The failure reason and batch ID are attached (`rejection_reason`, `rejection_batch_id`).
3. The invalid records are exported to:
   `data/quarantine/{batch_id}_{entity}_rejected.csv`.
4. Staging table ingestion continues safely with remaining valid records.

---

## 5. Audit Log Structure (`pipeline_audit.csv`)

| Field | Description |
|---|---|
| `run_id` | Unique batch execution identifier (e.g. `run-ff48b51f`) |
| `start_time` | Pipeline start timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `end_time` | Pipeline conclusion timestamp |
| `duration_seconds` | Total execution duration (typically < 0.5s for 28k rows) |
| `source_rows` | Total records read across all source files |
| `loaded_rows` | Total records successfully written to staging tables |
| `quarantined_rows` | Total rejected records routed to quarantine |
| `status` | `SUCCESS` or error message if failed |
