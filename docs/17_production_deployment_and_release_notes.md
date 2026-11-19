# LogiTrack Intelligence — Production Deployment & Release Notes
**Phase 12 Deliverable | Version 1.0.0 (Production Release)**

---

## 1. Executive Summary

LogiTrack Intelligence is an enterprise-grade, end-to-end logistics analytics, real-time IoT telematics, machine learning, and operational control tower platform. Phase 12 packages the complete system for reliable, multi-container production deployment, automated monitoring, and enterprise operations.

```
┌────────────────────────────────────────────────────────────────────────┐
│              LOGITRACK INTELLIGENCE — PRODUCTION TOPOLOGY              │
└────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│   PORT 8501: WEB UI     │   │   PORT 8000: REST API   │   │   PORT 1883: STREAMING  │
│ Streamlit Control Tower │   │  FastAPI REST Service   │   │  Eclipse Mosquitto MQTT │
│ • Executive KPIs        │   │  • /health • /kpis      │   │  • Telemetry ingestion  │
│ • Regional Hub Grid     │   │  • /hubs   • /fleet     │   │  • Order lifecycle      │
│ • Fleet Telematics GPS  │   │  • /ml/predict          │   │  • Dead-letter routing  │
│ • Real-Time Scoring     │   │  • /forecasting         │   │                         │
└───────────┬─────────────┘   └───────────┬─────────────┘   └───────────┬─────────────┘
            │                             │                             │
            └─────────────────────────────┼─────────────────────────────┘
                                          │
                                          ▼
            ┌───────────────────────────────────────────┐
            │   DUCKDB GOLD LAKEHOUSE & ARTIFACTS       │
            │   data/lake/logitrack.duckdb              │
            │   models/artifacts/*.joblib               │
            │   dashboards/powerbi/LogiTrack_Analytics  │
            └───────────────────────────────────────────┘
```

---

## 2. Production Deployment Options

### Option A: Multi-Container Deployment via Docker Compose (Recommended)

The platform is fully containerized using multi-stage, hardened `python:3.11-slim` images.

#### 1. Prerequisites
- Docker Engine 24.0+
- Docker Compose v2.20+
- 4 GB Available Host RAM
- Ports `1883`, `8000`, `8501` available

#### 2. Launch the Production Stack
```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/LogiTrack-Intelligence.git
cd LogiTrack-Intelligence

# Create environment configuration
cp .env.example .env

# Build and start all services in detached mode
docker compose up -d --build
```

#### 3. Verify Container Health
```bash
docker compose ps
```
Expected output:
```
NAME                      IMAGE                      STATUS                   PORTS
logitrack-mosquitto       eclipse-mosquitto:2.0      Up (healthy)             0.0.0.0:1883->1883/tcp
logitrack-api             logitrack-api:latest       Up (healthy)             0.0.0.0:8000->8000/tcp
logitrack-control-tower   logitrack-control-tower    Up (healthy)             0.0.0.0:8501->8501/tcp
```

#### 4. Access Live Services
- **FastAPI OpenAPI Swagger Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **FastAPI ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **Operational Control Tower**: [http://localhost:8501](http://localhost:8501)
- **MQTT Event Broker**: `tcp://localhost:1883`

---

### Option B: Bare-Metal / Virtual Environment Deployment

For native execution on Linux or Windows Server:

```bash
# 1. Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate       # Linux/macOS
# or .venv\Scripts\activate     # Windows

# 2. Install production dependencies
pip install -e ".[database,dashboards,ml,api]"

# 3. Build/Seed warehouse tables
python -c "from logitrack.transformation.warehouse_builder import build_warehouse_tables; build_warehouse_tables()"

# 4. Start Mosquitto broker (Native or Docker)
docker run -d --name mosquitto -p 1883:1883 eclipse-mosquitto:2.0

# 5. Start FastAPI REST Server
uvicorn logitrack.api.main:app --host 0.0.0.0 --port 8000 --workers 4

# 6. Start Streamlit Control Tower (in separate terminal)
streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 3. Environment & Configuration Reference

All application behavior is controlled via environment variables loaded from `.env` or injected by container runtimes:

| Variable | Default Value | Description |
|---|---|---|
| `API_HOST` | `0.0.0.0` | Binding host address for FastAPI |
| `API_PORT` | `8000` | Port for FastAPI REST service |
| `API_DEBUG` | `false` | Enable/disable verbose debug logs & hot reload |
| `STREAMLIT_SERVER_PORT` | `8501` | Port for Streamlit Control Tower |
| `MQTT_BROKER_HOST` | `localhost` | Hostname of Mosquitto broker (in docker: `mosquitto`) |
| `MQTT_BROKER_PORT` | `1883` | Port for MQTT streaming broker |
| `MQTT_CLIENT_ID` | `logitrack-consumer` | Unique client identifier for event streaming |
| `DUCKDB_PATH` | `data/lake/logitrack.duckdb` | Path to persistent analytics lakehouse |
| `DUCKDB_MEMORY_LIMIT` | `2GB` | RAM allocation limit for DuckDB query engine |
| `DUCKDB_THREADS` | `2` | Worker threads allocated for analytical queries |
| `LOG_LEVEL` | `INFO` | Logging threshold (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

---

## 4. Health Probes & Monitoring

Each service includes native readiness/liveness health endpoints:

### 4.1 REST API Health Probe
- **Endpoint**: `GET /health`
- **Response Format**:
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-11-19T14:15:00.000Z",
    "version": "1.0.0",
    "lakehouse_connected": true,
    "model_artifacts_available": 7
  }
  ```

### 4.2 Control Tower Health Probe
- **Endpoint**: `GET /_stcore/health`
- **HTTP Code**: `200 OK`

### 4.3 Automated System Diagnostics CLI
Run the embedded monitoring subsystem directly from the command line:
```bash
python -c "
from logitrack.monitoring.health_monitor import run_full_health_check
report = run_full_health_check()
print('Status:', report['overall_status'])
print('Summary:', report['summary'])
"
```

---

## 5. Operational Runbooks

### 5.1 Lakehouse Backup & Restore Procedure
The DuckDB analytical lakehouse is entirely self-contained within single-file storage.

- **Backup**:
  ```bash
  # Create snapshot while container is running (safe via read-only copy)
  cp data/lake/logitrack.duckdb backups/logitrack_$(date +%Y%m%d_%H%M%S).duckdb
  ```
- **Restore**:
  ```bash
  # Stop containers
  docker compose stop api control-tower
  # Replace database file
  cp backups/logitrack_20261119_120000.duckdb data/lake/logitrack.duckdb
  # Restart containers
  docker compose start api control-tower
  ```

### 5.2 Zero-Downtime Model Re-deployment
Trained model artifacts are stored in `models/artifacts/*.joblib`. When updated models are trained:
1. Place updated `.joblib` files into `models/artifacts/`.
2. Model endpoints dynamically re-read artifacts on subsequent requests or upon container restart (`docker compose restart api`).

### 5.3 Troubleshooting Common Failure Modes
- **Port Conflicts (`Address already in use`)**:
  Check if local services are already utilizing ports `8000`, `8501`, or `1883`:
  ```bash
  netstat -ano | findstr :8000
  ```
- **DuckDB Concurrency Locks**:
  Always ensure applications open read connections with `read_only=True` when connecting to `data/lake/logitrack.duckdb`.

---

## 6. Release Notes — Version 1.0.0 (Production Release)

### Release Summary
LogiTrack Intelligence v1.0.0 marks the completion of the 13-stage end-to-end data platform build. The platform synthesizes historical enterprise datasets, real-time IoT events, predictive machine learning models, multi-horizon forecasts, and modern executive dashboards into a unified system.

### Milestone Catalog (Phases 0–12 Completed)

| Phase | Component | Highlights |
|:---:|---|---|
| **0** | **Discovery & Architecture** | Project charter, business requirements (OTD, SLA, Cost), C4 architecture diagrams. |
| **1** | **Data Audit & Governance** | Data profiling on 27,979 orders, data dictionary, null-rate quarantine policies. |
| **2** | **Synthetic Data Engineering** | Deterministic generators for GPS telemetry, event lifecycles, and fleet maintenance. |
| **3** | **Storage & Database Design** | Neon PostgreSQL DDL schemas, Alembic migrations, and DuckDB analytical lakehouse setup. |
| **4** | **Batch ETL Pipeline** | Idempotent extraction, date standardization, and quarantine gate routing. |
| **5** | **Real-Time Event Streaming** | Paho MQTT producer/consumer, strict event contracts, and dead-letter routing. |
| **6** | **Data Warehouse (dbt)** | Star-schema dimensional modeling (`fact_orders`, `dim_hub`, `dim_vehicle`, `dim_driver`). |
| **7** | **BI & Dashboards** | 4-page Power BI PBIP enterprise dashboard and interactive Streamlit applications. |
| **8** | **Machine Learning** | 4 trained models (XGBoost Delay Classifier, Transit ETA Regressor, Hub Congestion, Fleet Maintenance). |
| **9** | **Time-Series Forecasting** | Multi-horizon order demand, hub workload, and fleet vehicle deficit forecasting with 95% CIs. |
| **10** | **API & Control Tower** | FastAPI REST services (Swagger/OpenAPI) and Streamlit operational command center. |
| **11** | **Monitoring & CI/CD** | System health checker, model drift detection, GitHub Actions CI pipeline, and 107 passing tests. |
| **12** | **Production Release** | Hardened Docker images, multi-container compose, release notes, and v1.0.0 tagging. |

---

## 7. Platform Verification Metrics

- **Automated Tests**: **107 Passed / 0 Failed (100% Pass Rate)**
- **Test Line Coverage**: **62%** (Exceeds CI requirement of 55%)
- **Data Completeness**: **100%** on critical business keys (Order ID, Hub ID, Driver ID, Vehicle Code)
- **SLA Calculation Standard**: OTD (79.6%) & Delay (20.4%) calculated with 27,727 Delivered Orders denominator
- **Release Status**: **Production-Ready (v1.0.0)**
