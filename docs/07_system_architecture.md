# System Architecture
# LogiTrack Intelligence

## Document Information

| Field | Value |
|-------|-------|
| Document ID | DOC-07 |
| Version | 1.0 |
| Created | 2026-11-13 |

---

## High-Level Architecture

```
╔══════════════════════════════════════════════════════════════════╗
║                        DATA SOURCES                             ║
║                                                                  ║
║  ┌──────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────────────┐║
║  │ Hubs.csv │ │Drivers  │ │Vehicles  │ │     Orders.csv       │║
║  │  6 rows  │ │.csv     │ │.csv      │ │     27,979 rows      │║
║  └────┬─────┘ │55 rows  │ │45 rows   │ └──────────┬───────────┘║
║       │       └────┬────┘ └────┬─────┘            │            ║
╚═══════╪════════════╪═══════════╪══════════════════╪════════════╝
        │            │           │                  │
        └────────────┴───────────┴──────────────────┘
                              │
                    ┌─────────▼──────────┐
                    │   BATCH ETL        │
                    │   (Python)         │
                    │  Extract → Validate│
                    │  Clean → Load      │
                    └─────────┬──────────┘
                              │
              ┌───────────────▼───────────────────────┐
              │        NEON POSTGRESQL (Cloud)         │
              │                                        │
              │  raw schema  →  staging  →  warehouse  │
              │  (Bronze)        (Silver)    (Gold)     │
              │                                        │
              │  realtime schema  │  ml schema          │
              └──┬────────────────┼────────────────────┘
                 │                │
                 │                │
   ┌─────────────▼──┐    ┌────────▼────────────────────────┐
   │ MQTT STREAMING │    │        dbt Core                 │
   │                │    │  Bronze → Silver → Gold Models  │
   │ Mosquitto      │    │  Fact Tables + Dimension Tables │
   │ Broker         │    │  Automated Tests + Docs         │
   │                │    └────────┬────────────────────────┘
   │ Python         │             │
   │ Producer ─────►│             │
   │ (simulates     │             │
   │  vehicles,     │◄────────────┘
   │  orders,       │
   │  drivers)      │
   │                │
   │ Python         │
   │ Consumer ──────┤
   └────────────────┘
              │
              ├──────────────────────┐
              │                      │
   ┌──────────▼──────────┐  ┌────────▼──────────────────┐
   │   PARQUET DATA LAKE │  │   DUCKDB (Local)          │
   │   data/lake/        │  │   Analytical Queries      │
   │   - telemetry/      │  │   Parquet Integration     │
   │   - events/         │  │   Memory: 2 GB limit      │
   │   - raw/            │  └───────────────────────────┘
   └─────────────────────┘
              │
              └────────────────────────────────┐
                                               │
   ╔══════════════════════════════════════════╧════════════════╗
   ║                ANALYTICS & INTELLIGENCE                    ║
   ║                                                            ║
   ║  ┌─────────────────┐  ┌─────────────────────────────────┐║
   ║  │   MACHINE       │  │        BI DASHBOARDS            │║
   ║  │   LEARNING      │  │                                 │║
   ║  │                 │  │  Power BI (Historical Reports)  │║
   ║  │  · Delay Risk   │  │  Streamlit (Control Tower)      │║
   ║  │  · ETA Predict  │  │  Grafana (Pipeline Monitoring)  │║
   ║  │  · Hub Congest  │  │                                 │║
   ║  │  · Pred. Maint  │  └─────────────────────────────────┘║
   ║  └────────┬────────┘                                      ║
   ║           │                                               ║
   ║  ┌────────▼────────┐  ┌─────────────────────────────────┐║
   ║  │  FORECASTING    │  │        FASTAPI                  │║
   ║  │                 │  │                                 │║
   ║  │  · 7-day Demand │  │  GET  /orders                  │║
   ║  │  · Hub Workload │  │  GET  /vehicles                │║
   ║  │  · Fleet Req.   │  │  POST /predict/delay-risk       │║
   ║  │                 │  │  POST /predict/eta              │║
   ║  └─────────────────┘  │  GET  /forecast/demand          │║
   ║                       │  GET  /alerts                   │║
   ║                       └─────────────────────────────────┘║
   ╚═══════════════════════════════════════════════════════════╝
```

---

## Component Responsibilities

| Component | Technology | Phase | Responsibility |
|-----------|-----------|-------|----------------|
| Batch ETL | Python | 4 | Extract, validate, clean, load CSV → Neon raw |
| MQTT Producer | Python + Paho | 5 | Simulate real-time events (vehicles, orders, drivers, hubs) |
| MQTT Broker | Mosquitto (Docker) | 5 | Route messages between producer and consumer |
| MQTT Consumer | Python + Paho | 5 | Receive events, validate schema, insert to Neon realtime |
| dbt Models | dbt Core | 6 | Transform raw → staging → warehouse |
| Parquet Lake | PyArrow | 4–5 | Archive high-volume telemetry and event history |
| DuckDB | DuckDB | 3+ | Analytical queries on Parquet; local OLAP |
| Power BI | Power BI Desktop | 7 | Historical management reporting |
| Streamlit | Streamlit | 7 + 10 | Operational control tower; ML prediction UI |
| Grafana | Grafana (Docker) | 11 | Pipeline metrics and monitoring |
| ML Models | Scikit-learn, XGBoost | 8 | Delay risk, ETA, hub congestion, maintenance |
| Forecasting | Prophet, Statsmodels | 9 | Demand, hub workload, fleet requirement |
| FastAPI | FastAPI | 10 | REST API for all operational and ML endpoints |
| Pytest | Pytest | 11 | Automated test suites (unit, integration, E2E) |
| GitHub Actions | YAML | 11 | CI/CD pipeline |

---

## Data Flow (End-to-End)

### Batch Flow (Historical)
```
CSV Files
  → Python ETL (extract, validate, clean)
  → Neon raw schema (Bronze)
  → dbt staging models (Silver)
  → dbt warehouse models (Gold)
  → Power BI / Streamlit dashboards
  → ML feature extraction → Model training
```

### Streaming Flow (Real-Time Simulation)
```
Python MQTT Producer (simulates events)
  → Mosquitto Broker
  → Python MQTT Consumer
  → Schema validation
  → Neon realtime schema
  → Streamlit live dashboard
  → Delay risk API (FastAPI)
  → Operational alerts
```

### Archive Flow (High Volume)
```
MQTT Consumer (telemetry events)
  → PyArrow → Parquet files (data/lake/telemetry/)
  ← DuckDB (reads Parquet for analytical queries)
  ← Power BI / Notebooks (historical telemetry analysis)
```

---

## Port Map (Local Development)

| Service | Port | Notes |
|---------|------|-------|
| Neon PostgreSQL | 5432 (cloud) | No local port needed |
| Mosquitto MQTT | 1883 | Docker container |
| FastAPI | 8000 | Development server |
| Streamlit | 8501 | Development server |
| Grafana | 3000 | Docker container |

---

## Security Design

| Concern | Approach |
|---------|---------|
| Database credentials | Environment variables only; never committed |
| API secrets | `.env` file (gitignored) |
| BI read access | Read-only Neon user for Power BI and Streamlit |
| Input validation | Pydantic for API; Great Expectations for data |
| Sensitive data | No PII in source data (fictional company) |
