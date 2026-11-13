# Business Requirements
# LogiTrack Intelligence

## Document Information

| Field | Value |
|-------|-------|
| Document ID | DOC-01 |
| Version | 1.0 |
| Status | Approved |
| Created | 2026-11-13 |

---

## 1. Business Problem Analysis

| Business Area | Problem | Impact |
|--------------|---------|--------|
| Delivery | No proactive delay detection | Customer dissatisfaction |
| Fleet | No real-time vehicle visibility | Inefficient dispatch |
| Maintenance | Reactive (breakdown-first) approach | Unexpected downtime |
| Hub | No backlog / congestion early warning | Processing delays |
| Driver | No shift and workload visibility | Overload or underutilization |
| Planning | No demand forecasting capability | Over/under resourcing |
| Reporting | Fragmented data in spreadsheets | Slow manual reporting |

> **Note:** These are hypothetical business assumptions for a fictional company.
> They are not verified problems of any real organization.

---

## 2. Functional Requirements

### FR-001 — Historical Data Ingestion
**Description:** The platform must ingest all four source CSV datasets into the
raw database layer without modifying the original files.

**Acceptance Criteria:**
- All records from `Hubs.csv`, `Drivers.csv`, `Vehicles.csv`, `Orders.csv`
  are loaded into the `raw` schema in Neon.
- Source file checksums are recorded before and after ingestion.
- Pipeline is idempotent: re-running does not create duplicate records.
- Rejected records are written to `data/quarantine/` with rejection reason.
- Pipeline audit log records row counts (source, loaded, rejected).

---

### FR-002 — Continuous Event Ingestion
**Description:** The platform must receive and persist simulated real-time events
published via MQTT.

**Acceptance Criteria:**
- MQTT consumer receives events from all configured topics.
- Each event is validated against its schema contract before database insert.
- Duplicate events (same `event_id`) are detected and not double-inserted.
- Out-of-order events are handled without corrupting timeline.
- Failed events are routed to dead-letter storage.
- Event ingestion latency is measurable.

---

### FR-003 — Vehicle Status & Location Tracking
**Description:** The platform must maintain a current and historical record of
each vehicle's operational status and simulated GPS location.

**Acceptance Criteria:**
- Each vehicle's latest status (Active / Maintenance / Retired) is queryable.
- Simulated GPS coordinates (latitude, longitude) are stored per telemetry event.
- Vehicle status history is preserved (SCD Type 2 in warehouse layer).
- Vehicles in Maintenance status cannot be assigned active orders simultaneously.

---

### FR-004 — Order Lifecycle Tracking
**Description:** The platform must track every order through its full delivery lifecycle.

**Order Lifecycle States:**
```
Order Created
    ↓
Hub Received
    ↓
Processing Started
    ↓
Processing Completed
    ↓
Dispatched
    ↓
In Transit
    ↓
Out for Delivery
    ↓
Delivered ──► (terminal)
    └──► Cancelled ──► (terminal)
    └──► Exception ──► Re-attempted or Cancelled
```

**Acceptance Criteria:**
- Every state transition is captured as a timestamped event.
- An order's current state is always queryable.
- Full event history for any order is retrievable.
- Cancelled and exception orders are stored separately from delivered orders.

---

### FR-005 — Delivery KPI Calculation
**Description:** The platform must compute and expose key delivery performance metrics.

**Core KPIs:**

| KPI | Definition |
|-----|-----------|
| On-Time Delivery Rate | `(On-time delivered orders / Total eligible delivered orders) × 100` |
| Delay Rate | `(Delayed eligible orders / Total eligible delivered orders) × 100` |
| Average Delivery Time | Mean of `Delivery Time Hours` for delivered orders |
| Hub Processing Time | Mean of `Hub Processing Time Hours` per hub |
| Customer Satisfaction | Mean `Customer Satisfaction Score` per driver / hub / period |

> **Note:** "Eligible" excludes cancelled orders. Final KPI definitions depend
> on the data dictionary completed in Phase 1.

**Acceptance Criteria:**
- KPIs are computed in the Gold layer of the data warehouse.
- KPIs are filterable by hub, driver, vehicle type, and time period.
- SQL formula and DAX formula are documented for each KPI.
- KPI results are visible in at least one dashboard.

---

### FR-006 — Delivery Delay Prediction
**Description:** The platform must predict the probability that a given order
will experience a delivery delay.

**Acceptance Criteria:**
- Model produces a delay risk score (0.0 – 1.0) for each order.
- Risk category (Low / Medium / High) is assigned based on threshold.
- Model version and prediction timestamp are logged with each prediction.
- Model card documents: objective, features, training data, metrics, limitations.
- Predictions are exposed via FastAPI endpoint.

---

### FR-007 — Demand Forecasting
**Description:** The platform must forecast future order demand at hub level
for planning purposes.

**Acceptance Criteria:**
- Forecast horizon: 7-day and 30-day.
- Output includes point forecast and confidence interval.
- Backtesting is performed using chronological (non-leaking) split.
- Forecast is labeled as synthetic/simulated in all dashboards.
- Forecast results are displayed in Streamlit and/or Power BI.

---

### FR-008 — Operational Alerts
**Description:** The platform must generate alerts for critical operational conditions.

**Alert Types:**

| Alert | Trigger |
|-------|---------|
| High Delay Risk | Order delay risk score > threshold |
| Vehicle Maintenance Due | `Maintenance count Alert` = 1 |
| Hub Congestion Warning | Hub backlog > capacity threshold |
| Driver Overload | Driver assigned orders > shift limit |

**Acceptance Criteria:**
- Alerts are queryable via FastAPI `/alerts` endpoint.
- Alerts appear in Streamlit operational dashboard.
- Alert history is stored in the database.

---

## 3. Non-Functional Requirements

| ID | Requirement | Detail |
|----|-------------|--------|
| NFR-001 | Data Traceability | Every record has `data_origin`, `source_system`, `ingestion_batch_id` |
| NFR-002 | Duplicate Detection | Duplicate records detected and rejected at all pipeline stages |
| NFR-003 | Pipeline Logging | Each pipeline run logged with start, end, row counts, status |
| NFR-004 | Automated Data Quality | dbt tests (unique, not_null, relationships) run on every transformation |
| NFR-005 | Error Handling | No silent failures; all errors logged with context |
| NFR-006 | Secure Credentials | No secrets in Git; all credentials in `.env` (gitignored) |
| NFR-007 | Reproducibility | Fixed random seed for all synthetic data generation |
| NFR-008 | Controlled Memory | DuckDB limited to 2 GB; services not all running simultaneously |
| NFR-009 | Idempotency | Re-running any pipeline stage does not corrupt data |
| NFR-010 | Data Separation | Original, synthetic, and simulated data never mixed without labels |
