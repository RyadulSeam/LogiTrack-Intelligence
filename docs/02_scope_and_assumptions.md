# Scope & Assumptions
# LogiTrack Intelligence

## Document Information

| Field | Value |
|-------|-------|
| Document ID | DOC-02 |
| Version | 1.0 |
| Created | 2026-11-13 |

---

## 1. Project Scope

### In Scope

| Component | Description |
|-----------|-------------|
| Batch ETL | Ingest and clean 4 source CSV datasets |
| Synthetic Data | Generate realistic-scale historical records |
| MQTT Streaming | Simulate real-time vehicle and order events |
| Neon Database | Cloud PostgreSQL for operational and warehouse data |
| DuckDB | Local analytical engine for high-volume queries |
| Parquet Lake | Archive for telemetry and event history |
| dbt Warehouse | Bronze → Silver → Gold medallion models |
| Power BI | Historical management dashboards |
| Streamlit | Operational control tower (live data) |
| Grafana | Pipeline and system monitoring |
| ML Models | Delay risk, ETA, hub congestion, predictive maintenance |
| Forecasting | Demand, hub workload, fleet requirement |
| FastAPI | REST API for predictions and operational data |
| Pytest + CI | Automated testing and GitHub Actions |

### Out of Scope

| Item | Reason |
|------|--------|
| Real GPS hardware integration | Simulated via MQTT producer |
| Production cloud deployment (AWS/GCP/Azure) | Free-tier local-first approach |
| Kubernetes orchestration | Exceeds 16 GB RAM constraints |
| Apache Kafka | Replaced by MQTT (appropriate for IoT/telematics use case) |
| Apache Spark | Replaced by DuckDB (sufficient for dataset scale) |
| Apache Airflow (heavy deployment) | Lightweight Python scheduler used instead |
| Real logistics company data validation | This is a portfolio/demonstration project |
| Revenue or cost financial modeling | Not present in source data |

---

## 2. Business Assumptions

| ID | Assumption |
|----|-----------|
| A-001 | LogiTrack Logistics Co. is a hypothetical company for portfolio demonstration |
| A-002 | Source datasets represent a real operational snapshot of this hypothetical company |
| A-003 | "Hub Capacity" in `Hubs.csv` represents maximum simultaneous orders (unit unverified) |
| A-004 | `Customer Satisfaction Score` is on a 1–5 scale |
| A-005 | `Is Delayed` and `Is On Time` are mutually exclusive boolean flags |
| A-006 | `Delivery Time Hours` represents total elapsed time from order creation to delivery |
| A-007 | `Hub Processing Time Hours` is a subset of total delivery time |
| A-008 | No Promised Delivery Timestamp exists in source data — SLA-based delay target cannot be derived |
| A-009 | Vehicle assignment in Orders is by vehicle code, not Vehicle ID |
| A-010 | `Maintenance count Alert` is a binary flag (0 = OK, 1 = Alert), not a count |

---

## 3. Technical Assumptions

| ID | Assumption |
|----|-----------|
| TA-001 | Python 3.10+ is installed on the development machine |
| TA-002 | Docker Desktop is available for running Mosquitto MQTT broker |
| TA-003 | Neon free tier provides sufficient storage for operational data |
| TA-004 | 16 GB RAM is sufficient when services are run sequentially, not simultaneously |
| TA-005 | DuckDB memory limited to 2 GB to avoid RAM pressure |
| TA-006 | All synthetic data uses a fixed random seed (42) for reproducibility |
| TA-007 | MQTT QoS Level 1 (at-least-once) — consumer handles potential duplicates |
| TA-008 | Neon free-tier limits may change; storage strategy reviewed before v1.0.0 release |

---

## 4. Data Quality Assumptions

| ID | Assumption |
|----|-----------|
| DQ-001 | Mixed date formats in source (DD-MM-YYYY and M/D/YYYY) are a known issue to be resolved in Phase 1 |
| DQ-002 | Missing `Delay Reason` for non-delayed orders is expected (not a data quality issue) |
| DQ-003 | Driver Name in Orders may not perfectly match Driver Name in Drivers.csv — to be validated in Phase 1 |
| DQ-004 | Vehicle Code in Orders (e.g., FT-036) references vehicles beyond the 45 in Vehicles.csv — to be investigated |
| DQ-005 | Original source files are immutable; no manual editing will be performed on them |

---

## 5. Known Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Neon free tier storage exceeded | Medium | High | Store only operational data in Neon; archive in Parquet |
| RAM pressure during ML training | Medium | Medium | Train one model at a time; use DuckDB memory limit |
| Date parsing ambiguity in source data | High | Medium | Document all ambiguous dates; apply consistent parsing rule |
| Synthetic data quality issues | Low | High | Validate referential integrity after each generator run |
| ML model claims not generalizable | Certain | Low | Document clearly in model cards; label all predictions |
