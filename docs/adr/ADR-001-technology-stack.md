# ADR-001: Technology Stack Selection
# LogiTrack Intelligence

## Status
Accepted — 2026-11-13

---

## Context

LogiTrack Intelligence requires a complete end-to-end data platform covering:
batch ingestion, real-time streaming, cloud storage, analytical querying,
BI dashboards, machine learning, forecasting, and a REST API.

The platform must run on a single machine with 16 GB RAM at zero infrastructure cost.

---

## Decisions

### 1. Python 3.10+ (Primary Language)

**Decision:** Use Python as the single implementation language across all layers.

**Rationale:**
- Industry standard for data engineering, ML, and API development.
- Unified language reduces context switching and dependency complexity.
- Rich ecosystem covers every required capability.

**Alternatives Considered:**
- Scala/Java (Spark ecosystem): Excessive JVM overhead, too heavy for 16 GB RAM.
- R: Strong statistical capabilities but weak for data engineering and APIs.

---

### 2. Neon (Cloud PostgreSQL)

**Decision:** Use Neon serverless PostgreSQL as the primary operational and
warehouse database.

**Rationale:**
- Free tier with no credit card required.
- Eliminates local PostgreSQL server setup (saves RAM).
- Full PostgreSQL compatibility — works with psycopg2, SQLAlchemy, dbt-postgres.
- Serverless scaling: no manual instance management.
- Branching feature enables safe schema experimentation.

**Alternatives Considered:**
- Local PostgreSQL (Docker): Consumes RAM even when idle.
- SQLite: Not suitable for concurrent writes or cloud-ready architecture.
- Supabase: Free tier but heavier feature set than needed.

---

### 3. DuckDB (Local Analytical Engine)

**Decision:** Use DuckDB for local analytical queries and Parquet file processing,
limited to 2 GB memory.

**Rationale:**
- Zero-dependency in-process OLAP engine — no server to manage.
- Fastest analytical query engine per benchmark for local workloads.
- Native Parquet read/write support.
- Python-native API.

**Alternatives Considered:**
- Apache Spark: Requires JVM, 4+ GB RAM overhead before data processing.
- ClickHouse (local): Requires separate server, additional RAM.
- Polars: Great for DataFrames but not a full OLAP engine.

---

### 4. MQTT + Eclipse Mosquitto (Event Streaming)

**Decision:** Use MQTT protocol with Mosquitto broker for real-time event simulation.

**Rationale:**
- Industry standard protocol for IoT and vehicle telematics (GPS trackers, 
  fleet management systems universally use MQTT).
- Mosquitto is a C-based broker: runs on <50 MB RAM.
- Appropriate for logistics vehicle tracking use case — not a high-throughput
  financial trading platform.
- Paho Python client is well-maintained and simple.

**Alternatives Considered:**
- Apache Kafka: Overkill for single-machine simulation; 1–2 GB RAM for JVM alone;
  better suited for multi-producer enterprise throughput.
- Redis Streams: Viable alternative but less industry-standard for IoT/telematics.
- RabbitMQ: AMQP protocol, less appropriate for telematics use case.

**Note for Portfolio:** When presenting, clearly state: *"I chose MQTT because it
is the standard protocol used by real fleet GPS telematics devices (e.g., Teltonika,
Calamp), making this simulation architecturally authentic."*

---

### 5. Apache Parquet + Data Lake Structure

**Decision:** Store high-volume historical telemetry and event archives in Parquet
files in a local `data/lake/` directory.

**Rationale:**
- Columnar format is 5–10x more efficient for analytical queries than CSV.
- DuckDB reads Parquet natively without loading into memory.
- Avoids exceeding Neon free-tier storage limits.
- Industry-standard data lake format.

---

### 6. dbt Core (Transformation)

**Decision:** Use dbt Core for all SQL transformations in the data warehouse.

**Rationale:**
- Enforces transformation best practices (modularity, testing, documentation).
- Built-in data tests (unique, not_null, relationships, accepted_values).
- Auto-generates data lineage documentation.
- dbt-postgres works directly with Neon.
- Used by thousands of production data teams.

---

### 7. Scikit-learn + XGBoost + Prophet (ML & Forecasting)

**Decision:** Use scikit-learn and XGBoost for classification/regression models,
Prophet for time-series forecasting.

**Rationale:**
- Scikit-learn: Industry standard, stable API, well-documented.
- XGBoost: State-of-the-art gradient boosting, top performer on tabular data.
- Prophet: Designed for business time-series with seasonality; interpretable outputs.

---

### 8. FastAPI (REST API)

**Decision:** Use FastAPI for the application and prediction API layer.

**Rationale:**
- Automatic OpenAPI/Swagger documentation.
- Native async support.
- Pydantic integration for request/response validation.
- Fastest Python web framework per benchmarks.

---

### 9. Streamlit (Operational Dashboard)

**Decision:** Use Streamlit as the primary operational dashboard and control tower.

**Rationale:**
- Pure Python — no frontend JavaScript required.
- Native support for maps (pydeck), charts (plotly), and live refresh.
- Can connect directly to Neon and DuckDB.
- Fast to build; appropriate for operational/near-real-time dashboards.

---

### Consequences

**Positive:**
- Entire stack runs on 16 GB RAM with no paid services.
- Architecture mirrors real production logistics platforms (MQTT telematics,
  PostgreSQL warehouse, dbt transformations, ML predictions via API).
- Each technology choice is defensible in a technical interview.

**Negative:**
- MQTT instead of Kafka may be questioned by evaluators expecting Kafka.
  (Mitigation: document rationale clearly; MQTT is correct for IoT/telematics.)
- No distributed computing — not suitable for petabyte-scale real workloads.
  (Mitigation: document scale limitations in `20_known_limitations.md`.)
