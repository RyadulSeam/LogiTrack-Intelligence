# Project Charter
# LogiTrack Intelligence

## Document Information

| Field | Value |
|-------|-------|
| Document ID | DOC-00 |
| Version | 1.0 |
| Status | Approved |
| Created | 2026-11-13 |
| Author | Ryadul Seam |

---

## 1. Project Overview

**Project Name:** LogiTrack Intelligence  
**Type:** Enterprise Logistics Data & Predictive Operations Platform  
**Classification:** Portfolio / Demonstration Project  

LogiTrack Intelligence is a full-stack logistics data platform built to demonstrate
production-grade data engineering, real-time streaming, analytics, and machine
learning capabilities using modern open-source tooling at zero infrastructure cost.

---

## 2. Business Context

### Hypothetical Company
**LogiTrack Logistics Co.** operates a regional delivery network across Texas with:
- **6 distribution hubs** (Dallas, Houston, Austin, San Antonio, Fort Worth, El Paso)
- **45 fleet vehicles** (Vans, Trucks — Mercedes Sprinter, Freightliner M2, Ford Transit, etc.)
- **55 drivers** (Full-time, Part-time, Contract)
- **~28,000 historical delivery orders**

### Problem Statement
The company's operational data is fragmented across spreadsheets with no unified
platform for real-time visibility, predictive analytics, or demand planning.
Management lacks the tools to proactively prevent delivery delays, optimize fleet
utilization, or forecast hub capacity requirements.

---

## 3. Business Objectives

| ID | Objective |
|----|-----------|
| BO-01 | Unify all logistics data into a single, governed data platform |
| BO-02 | Achieve real-time visibility into vehicle location and order status |
| BO-03 | Reduce delivery delays through predictive risk scoring |
| BO-04 | Optimize fleet maintenance through predictive maintenance alerts |
| BO-05 | Enable data-driven demand forecasting for hub capacity planning |
| BO-06 | Provide management with self-service BI dashboards |

---

## 4. Project Scope

### In Scope
- Historical data engineering (batch ETL from CSV sources)
- Synthetic data generation for realistic scale testing
- Simulated real-time streaming (MQTT) for vehicle telemetry and order events
- Cloud data warehouse (Neon PostgreSQL) with Medallion Architecture
- Local analytical engine (DuckDB) + Parquet data lake
- dbt Core transformation models (Bronze / Silver / Gold)
- 5 BI dashboards (Power BI + Streamlit + Grafana)
- 4 ML models (delay risk, ETA, hub congestion, predictive maintenance)
- 3 forecasting models (demand, hub workload, fleet requirement)
- FastAPI REST endpoints + Streamlit operational control tower
- Automated testing (Pytest) + CI/CD (GitHub Actions)
- Monitoring and alerting (Grafana)

### Out of Scope
- Production deployment to real logistics company
- Integration with live third-party APIs (GPS hardware, TMS systems)
- Kubernetes / enterprise-scale orchestration
- Guaranteed production SLAs

---

## 5. Data Assets

| Dataset | File | Records | Status |
|---------|------|---------|--------|
| Hubs | `data/source/Hubs.csv` | 6 | ✅ Available |
| Drivers | `data/source/Drivers.csv` | 55 | ✅ Available |
| Vehicles | `data/source/Vehicles.csv` | 45 | ✅ Available |
| Orders | `data/source/Orders.csv` | 27,979 | ✅ Available |

> **Important:** Original source files are immutable. No transformation
> or enrichment will be applied directly to files in `data/source/`.

---

## 6. Data Provenance Policy

The platform strictly separates three categories of data:

| Category | Description | Label in Dashboards |
|----------|-------------|---------------------|
| **Original Historical** | The 4 real source CSV files | `source: original` |
| **Synthetic Historical** | Python-generated realistic records | `source: synthetic` |
| **Simulated Live Events** | MQTT-based real-time event simulation | `source: simulated` |

No synthetic or simulated data will be presented as real without clear labeling.

---

## 7. Technology Stack

| Layer | Technology | Rationale |
|-------|-----------|-----------|
| Language | Python 3.10+ | Industry standard for data engineering & ML |
| Cloud DB | Neon (PostgreSQL) | Free serverless PostgreSQL, no local server needed |
| Local Analytics | DuckDB | Zero-config, fastest in-process OLAP engine |
| Data Lake | Apache Parquet | Columnar format for high-volume telemetry |
| Streaming | MQTT + Mosquitto | Standard IoT/telematics protocol; lightweight for 16 GB RAM |
| Transformation | dbt Core | SQL-based transformation with built-in testing |
| BI | Power BI + Streamlit + Grafana | Historical, operational, and monitoring dashboards |
| ML | Scikit-learn, XGBoost, Prophet | Production-grade, well-documented open-source |
| API | FastAPI | High-performance, auto-documented REST API |
| Testing | Pytest + GitHub Actions | Industry-standard test automation |

---

## 8. Timeline

| Week | Phase | Deliverable |
|------|-------|-------------|
| 1 | Foundation + Phase 0 + Phase 1 | Data Audit Complete |
| 2 | Phase 2 + Phase 3 | Synthetic Data + Database Ready |
| 3 | Phase 4 | Batch ETL Pipeline |
| 4 | Phase 5 | MQTT Streaming |
| 5 | Phase 6 | Data Warehouse (dbt) |
| 6 | Phase 7 | BI Dashboards |
| 7 | Phase 8 + 9 | ML + Forecasting |
| 8 | Phase 10 + 11 | API + Testing + Security |
| 9 | Phase 12 | v1.0.0 Final Release |

---

## 9. Resource Constraints

| Resource | Constraint | Strategy |
|----------|-----------|----------|
| RAM | 16 GB | Run one heavy service at a time; DuckDB limited to 2 GB |
| Storage (Neon) | Free tier | Operational data only; archive in Parquet |
| Cost | $0 budget | 100% open-source and free-tier cloud services |

---

## 10. Definition of Done

The project is complete when:
- [ ] Fresh clone + setup works in a new environment
- [ ] Original, synthetic, and simulated data are clearly separated
- [ ] End-to-end pipeline runs without manual intervention
- [ ] All 5 dashboards are functional
- [ ] All 4 ML models have evaluation metrics and model cards
- [ ] All 3 forecasting models have backtesting results
- [ ] FastAPI and Streamlit application are operational
- [ ] Pytest suites pass in CI
- [ ] No secrets committed to the repository
- [ ] v1.0.0 release tag created with documentation
