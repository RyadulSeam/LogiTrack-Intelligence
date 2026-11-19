# LogiTrack Intelligence — API & Application Layer Guide
**Phase 10 Deliverable | Version 1.0.0**

---

## 1. Executive Summary

Phase 10 provides the enterprise access and visualization layer for the LogiTrack Intelligence platform. It encompasses two primary interfaces:
1. **FastAPI REST Service (`src/logitrack/api`)**: High-performance, low-latency RESTful API serving executive metrics, regional hub operations, live vehicle telematics, real-time machine learning inference, and multi-horizon time-series forecasts.
2. **Operational Control Tower (`src/logitrack/app/app.py` & `app/streamlit_app.py`)**: An enterprise Streamlit web application providing executives, dispatch managers, and supply chain analysts with an interactive operational command center.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER / CLIENT INTERFACES                        │
│                                                                        │
│   Power BI Dashboard        Streamlit Control Tower       REST API     │
│   (Executive Analytics)     (Operational Dispatch)        (Automations)│
└───────────────┬──────────────────────────┬──────────────────────┬──────┘
                │                          │                      │
                ▼                          ▼                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   FASTAPI REST API SERVICE (:8000)                     │
│  /health  •  /kpis  •  /hubs  •  /fleet  •  /ml/predict  •  /forecasting │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼
┌────────────────────────────────────────────────────────────────────────┐
│                   DUCKDB LAKEHOUSE & MODEL ARTIFACTS                   │
│   data/lake/logitrack.duckdb  •  models/artifacts/*.joblib             │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 2. FastAPI REST Service

### 2.1 Starting the API Server
```bash
# Using uvicorn from project root
.venv\Scripts\uvicorn.exe logitrack.api.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI (Swagger) documentation is available at:
- **Swagger UI**: `http://127.0.0.1:8000/docs`
- **ReDoc**: `http://127.0.0.1:8000/redoc`
- **OpenAPI Schema**: `http://127.0.0.1:8000/openapi.json`

---

### 2.2 Endpoint Catalog

#### System
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System diagnostics & DuckDB lakehouse connectivity check |

**Sample Response (`/health`):**
```json
{
  "status": "HEALTHY",
  "version": "1.0.0",
  "database": "CONNECTED",
  "environment": "production-ready"
}
```

---

#### Executive KPIs
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/kpis/executive` | Executive Control Tower KPIs with optional `hub_name` filter |

**Query Parameters:**
- `hub_name` *(optional)*: Filter by Texas hub (e.g. `Dallas Main Hub`, `Austin Hub`).

**Sample Response (`/api/v1/kpis/executive`):**
```json
{
  "total_orders": 27979,
  "delivered_orders": 27727,
  "cancelled_orders": 252,
  "on_time_delivery_rate_pct": 79.6,
  "delay_rate_pct": 20.4,
  "avg_delivery_time_hours": 25.1,
  "avg_hub_processing_hours": 2.1,
  "avg_csat_score": 4.1,
  "total_fleet": 45,
  "active_fleet": 33,
  "fleet_utilization_pct": 73.3,
  "maintenance_alerts": 8
}
```

---

#### Regional Hub Operations
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/hubs` | Regional hub throughput, sorting capacity, GPS coordinates, and dwell times |

**Sample Item (`hubs[0]`):**
```json
{
  "hub_name": "Dallas Main Hub",
  "city": "Dallas",
  "daily_capacity": 4500,
  "latitude": 32.7767,
  "longitude": -96.797,
  "total_orders": 6850,
  "delayed_orders": 1380,
  "avg_delivery_hours": 24.2,
  "avg_processing_hours": 1.9,
  "avg_csat": 4.15,
  "workload_ratio": 1.52
}
```

---

#### Fleet Telematics
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/fleet` | Live vehicle positions, fuel levels, speed, and engine health |

**Sample Item (`vehicles[0]`):**
```json
{
  "vehicle_code": "VEH-DAL-01",
  "vehicle_model": "Ford Transit Cargo",
  "vehicle_type": "Van",
  "current_status": "Active",
  "latitude": 32.812,
  "longitude": -96.754,
  "speed_kmh": 68.4,
  "fuel_level_pct": 82.5,
  "engine_temp_c": 91.2,
  "engine_status": "Normal"
}
```

---

#### Machine Learning Real-Time Inference
| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/v1/ml/predict-delay` | Real-time SLA delay risk probability via trained XGBoost Classifier |
| `POST` | `/api/v1/ml/predict-eta` | Estimated transit duration (hours) with 80% confidence interval |

**Sample Payload (`POST /api/v1/ml/predict-delay`):**
```json
{
  "distance_km": 245.5,
  "planned_duration_hours": 36.0,
  "package_weight_kg": 18.5,
  "delivery_priority": "High",
  "vehicle_type": "Van",
  "driver_experience_years": 5,
  "driver_rating": 4.5,
  "is_weekend": false,
  "hub_id": "HUB-DAL-01"
}
```

**Sample Response:**
```json
{
  "predicted_label": "DELAY_RISK",
  "delay_probability_pct": 78.5,
  "risk_level": "CRITICAL",
  "explanation": "Shipment analyzed with 78.5% probability of SLA exception. Risk classified as CRITICAL.",
  "model_version": "1.0.0"
}
```

---

#### Time-Series Forecasting
| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/v1/forecasting/demand` | 7-day and 30-day forecasted order demand with 95% Confidence Intervals |
| `GET` | `/api/v1/forecasting/workload` | Hub capacity utilization %, dispatched volume, and bottleneck flags |
| `GET` | `/api/v1/forecasting/fleet` | Vehicle requirement counts by class (Van, Truck, Pickup, Box Truck) & gaps |

**Query Parameters:**
- `horizon_days` *(int, default=30)*: Number of forward forecast days (1 to 30).
- `hub_name` *(optional)*: Filter by Texas hub.

---

## 3. Streamlit Operational Control Tower

### 3.1 Launching the Web App
```bash
# Launch Streamlit Operational Control Tower
.venv\Scripts\streamlit.exe run app/streamlit_app.py
```
Or directly:
```bash
.venv\Scripts\streamlit.exe run src/logitrack/app/app.py
```
The application opens automatically at `http://localhost:8501`.

### 3.2 Feature Modules

1. **📊 Executive KPI Command Center**:
   - Executive metric scorecard: Total Orders (27,979), Delivered (27,727), OTD SLA % (79.6% vs 85% Target), Delay % (20.4%), Active Fleet (33/45), Avg Delivery Duration (25.1 hrs).
   - Regional Hub Performance Matrix table with sorting and filtering.
   - Throughput vs Delay volume bar chart.
2. **🏢 Regional Hub Operations**:
   - Facility deep-dive selector across 6 Texas Regional Hubs.
   - Daily sorting capacity vs actual processed volume.
   - Processing dwell time and customer CSAT monitoring.
   - Regional throughput share donut chart and transit duration horizontal rankings.
3. **🛰️ Live Fleet Telematics & Asset Tracking**:
   - Real-time GPS map plotting active vehicle positions across Texas highways.
   - Vehicle status breakdown (Active, Maintenance, Idle).
   - Telemetry data grid tracking speed (km/h), fuel %, engine temperature (°C), and engine health alerts.
4. **🧠 Real-Time ML Inference & Delay Risk Scoring**:
   - Interactive shipment dispatch simulator.
   - Real-time delay classification and ETA regressor scoring.
   - Risk classification badges (`ON_TIME` vs `DELAY_RISK`), probability percentage, and confidence interval bounds.
5. **📈 AI Time-Series Forecasting Center**:
   - 7-day and 30-day forecast horizon toggle.
   - Point forecast demand curves with shaded 95% Confidence Interval bands.
   - Projected hub capacity utilization % with bottleneck risk threshold warning ($\ge 85\%$).
   - Vehicle requirement matrix by vehicle type showing surplus and deficit alerts.

---

## 4. Automated Testing & Verification

A dedicated Pytest test suite verifies all API endpoints and response contracts:
```bash
.venv\Scripts\pytest.exe tests/api/test_api_endpoints.py -v
```

### Verification Matrix
- `test_health_check`: Validates `/health` returns HTTP 200, status `HEALTHY`, and database `CONNECTED`.
- `test_executive_kpis`: Validates baseline order counts (27,979 total, 27,727 delivered, 252 cancelled) and OTD rate (79.6%).
- `test_executive_kpis_filtered`: Validates filtered KPI queries for regional facilities.
- `test_hubs_endpoint`: Validates all 6 Texas hubs are returned with valid geographic coordinates.
- `test_fleet_endpoint`: Validates telematics records for active fleet vehicles.
- `test_ml_predict_delay`: Validates XGBoost delay risk classification and probability scoring.
- `test_ml_predict_eta`: Validates transit duration ETA regressor and confidence intervals.
- `test_forecasting_demand`: Validates 30-day demand forecasts and 95% confidence intervals.
- `test_forecasting_workload`: Validates hub workload utilization and bottleneck alert logic.
- `test_forecasting_fleet`: Validates fleet requirement counts across vehicle classes.
