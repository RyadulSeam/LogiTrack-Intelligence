# ADR-002: Data Storage Strategy
# LogiTrack Intelligence

## Status
Accepted — 2026-11-13

---

## Context

The platform handles multiple types of data with different access patterns,
volume characteristics, and retention requirements:

| Data Type | Volume | Access Pattern | Retention |
|-----------|--------|----------------|-----------|
| Source CSVs | Small (~3 MB) | Read-only, one-time | Permanent |
| Operational orders/status | Medium (~28K records) | Read/Write, frequent | Active period |
| Vehicle telemetry | Large (simulated, 50K–100K events) | Write-heavy, batch read | Long-term archive |
| Order events (lifecycle) | Large (50K–100K events) | Write-heavy, query by order | Long-term archive |
| ML predictions | Small | Write on prediction, read for dashboards | Model lifetime |
| Aggregated analytics | Small | Read-heavy | Rolling window |

---

## Decision

### Storage Assignment

| Data | Storage | Reason |
|------|---------|--------|
| Source CSVs | `data/source/` (Git) | Immutable; small enough for Git |
| Synthetic CSVs | `data/synthetic/` (local) | Git-ignored; regeneratable |
| Raw ingested records | Neon `raw` schema | Cloud-accessible; PostgreSQL querying |
| Cleaned records | Neon `staging` schema | Queryable by dbt |
| Warehouse (facts/dims) | Neon `warehouse` schema | BI and ML feature store |
| Real-time events | Neon `realtime` schema (recent window) | Live dashboard queries |
| Event archive | `data/lake/` Parquet | Volume too large for Neon free tier |
| Telemetry archive | `data/lake/telemetry/` Parquet | Same rationale |
| ML predictions | Neon `ml` schema | Logged per prediction; queryable |
| Quarantined records | `data/quarantine/` (local CSV/JSON) | Audit trail for rejected data |

---

## Medallion Architecture (Neon Schemas)

```
SOURCE FILES (data/source/)
        │
        ▼
  raw schema          ← Bronze: exact copy of source, ingestion metadata added
        │
        ▼
  staging schema      ← Silver: cleaned, typed, deduplicated, relationships validated
        │
        ▼
  warehouse schema    ← Gold: facts, dimensions, aggregated KPIs, business-ready
        │
   ┌────┴────┐
   ▼         ▼
realtime   ml schema  ← Live events + predictions
schema
```

### Schema Responsibilities

**raw (Bronze)**
- One table per source entity: `raw_vehicles`, `raw_orders`, `raw_drivers`, `raw_hubs`
- Columns are as close to source as possible
- Added metadata: `ingestion_batch_id`, `source_file`, `loaded_at`, `data_origin`
- Never modified after insert (append-only)

**staging (Silver)**
- Standardized column names (snake_case)
- Consistent data types (dates as DATE, timestamps as TIMESTAMPTZ)
- Duplicates removed
- Invalid records excluded (moved to quarantine)
- Relationships validated
- Added: `stg_created_at`, `source_record_id`

**warehouse (Gold)**
- Fact tables: `fact_orders`, `fact_order_events`, `fact_vehicle_telemetry`,
  `fact_maintenance`, `fact_hub_hourly`, `fact_driver_shift`, `fact_assignments`
- Dimension tables: `dim_date`, `dim_time`, `dim_vehicle`, `dim_driver`,
  `dim_hub`, `dim_route`
- Aggregated KPI tables for dashboard performance
- SCD Type 2 for slowly changing driver and vehicle attributes

**realtime**
- `vehicle_events`: latest GPS and status per vehicle
- `order_events`: latest order state per order
- `driver_events`: latest driver activity
- `hub_events`: latest hub operational metrics
- `ingestion_errors`: failed event records with error context

**ml**
- `model_registry`: trained model metadata
- `model_evaluations`: evaluation metrics per model version
- `predictions`: logged predictions with order_id, model_version, timestamp
- `feature_snapshots`: input features used for each prediction

---

## Parquet Lake Structure

```
data/lake/
├── raw/
│   ├── orders/           ← Partitioned by year/month
│   ├── vehicles/
│   └── drivers/
├── telemetry/            ← Vehicle GPS pings (high volume)
│   └── year=YYYY/
│       └── month=MM/
├── events/               ← Order lifecycle events archive
│   └── year=YYYY/
│       └── month=MM/
└── synthetic/            ← Synthetic data outputs (Git-ignored)
```

---

## Neon Free Tier Management

To stay within Neon free-tier limits:
1. Only the **most recent 30 days** of raw telemetry kept in Neon `realtime`.
2. Older telemetry and events archived to Parquet automatically.
3. `data/lake/` is Git-ignored — regeneratable from simulation scripts.
4. DuckDB reads Parquet directly for historical analytical queries.

---

## Consequences

**Positive:**
- Zero storage cost: Neon free tier for operational data, local Parquet for archives.
- Clear separation of concerns across storage layers.
- DuckDB + Parquet enables fast historical analytics without loading into RAM.
- Architecture mirrors real production data lake implementations (medallion pattern).

**Negative:**
- Parquet lake is local-only — not shareable without cloud storage.
  (Mitigation: document this limitation; for portfolio, screenshots and notebooks suffice.)
- Neon free-tier storage limits may require adjustment as project grows.
  (Mitigation: monitor usage; archive aggressively to Parquet.)
