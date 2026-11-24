<div align="center">

# 🚛 LogiTrack Intelligence
### An End-to-End Logistics Analytics & Predictive Operations Platform

**Unifying multi-echelon supply chain data engineering, predictive machine learning, real-time IoT event simulation, and executive Power BI intelligence into an operational decision platform.**

[![CI/CD Pipeline](https://github.com/RyadulSeam/LogiTrack-Intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/RyadulSeam/LogiTrack-Intelligence/actions/workflows/ci.yml)
[![Automated Tests](https://img.shields.io/badge/Tests-107%20Passed%20(100%25)-success?style=for-the-badge&logo=pytest&logoColor=white)](tests/)
[![Test Coverage](https://img.shields.io/badge/Coverage-62%25%20Verified-brightgreen?style=for-the-badge&logo=codecov&logoColor=white)](htmlcov/)
[![Python Version](https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Power BI TMDL](https://img.shields.io/badge/Power_BI-TMDL%20%7C%20PBIP-F2C811?style=for-the-badge&logo=powerbi&logoColor=black)](dashboards/powerbi/)
[![FastAPI](https://img.shields.io/badge/FastAPI-REST%20Endpoints-009688?style=for-the-badge&logo=fastapi&logoColor=white)](src/logitrack/api/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

<br/>

**Developed by [Ryadul Islam Seam](https://www.linkedin.com/in/ryadulseam-data)**
*Logistics & Operations Analytics Consultant | Predictive Delivery Risk & Automated Power BI Dashboards for E-Commerce, Retail & Distribution*
[LinkedIn Profile](https://www.linkedin.com/in/ryadulseam-data) • [GitHub Repository](https://github.com/RyadulSeam/LogiTrack-Intelligence)

---

### ⏱️ Executive Briefing (30-Second Summary)

| Dimension | Platform Capability | Operational Value |
| :--- | :--- | :--- |
| **Operational Scale** | Analyzes **27,979 multi-leg shipments** across **6 Texas distribution hubs**, **45 fleet assets**, and **55 drivers**. | Replaces siloed spreadsheets with a single, governed operational source of truth. |
| **SLA & Delay Visibility** | Pinpoints root causes behind a baseline **20.4% delivery delay rate** (5,653 delayed orders). | Enables dispatchers and terminal managers to mitigate transit bottlenecks proactively. |
| **Predictive Intelligence** | Trains **4 ML models** (Delay Risk, Transit ETA, Hub Congestion, Fleet Health) + **3 time-series forecasters**. | Provides forward-looking ETA confidence intervals and 30-day capacity deficit warnings. |
| **Enterprise BI Suite** | Modern **Power BI PBIP/TMDL tabular model** with **4 operational pages**, **8 drill-through views**, and **69 measures**. | Delivers sub-second KPI visibility from C-suite summaries down to vehicle telematics. |
| **Code Quality & CI/CD** | **107 automated tests (100% pass rate)** with **62% statement coverage** validated on GitHub Actions. | Ensures data integrity, migration idempotency, and regression prevention in production. |

</div>

---

## 📌 1. Executive Summary

Logistics and distribution enterprises manage complex, fast-moving transportation networks. Operational leadership—CEOs, Chief Operating Officers, and VPs of Supply Chain—frequently confront three structural obstacles:

1. **Fragmented Data Silos:** Transportation Management Systems (TMS), Warehouse Management Systems (WMS), and GPS telematics vendors store information in disjointed schemas, forcing operations teams to rely on delayed, error-prone manual spreadsheet consolidation.
2. **Reactive Exception Management:** Dispatchers and hub managers discover transit delays, hub capacity bottlenecks, and vehicle breakdowns *after* delivery SLAs are breached, driving up customer churn and overtime labor expenses.
3. **Disconnected Planning & Execution:** Forward capacity planning (fleet allocation and warehouse staffing) relies on backward-looking historical averages rather than statistical time-series demand projections.

**LogiTrack Intelligence** is an end-to-end data engineering, machine learning, and business intelligence platform engineered to bridge these gaps. It ingests transactional supply chain records, cleanses and models them into a dimensional lakehouse, generates predictive risk intelligence before shipments depart, simulates near-real-time IoT fleet telemetry, and surfaces actionable operational insights through an enterprise Power BI suite and FastAPI microservices.

```
Transactional Ingestion ──► Medallion Lakehouse ──► Predictive Models ──► Power BI & APIs
(Orders, Hubs, Fleet)       (DuckDB / PostgreSQL)   (XGBoost / Forecaster) (Operations Control)
```

---

## 🎯 2. Business Problems & Operational Solutions

| Operational Challenge | Root Cause in Conventional Operations | LogiTrack Intelligence Solution | Targeted Business Impact |
| :--- | :--- | :--- | :--- |
| **Customer SLA Breaches** | Dispatchers lack advance warning when shipments encounter severe transit risk. | Pre-dispatch **XGBoost Delay Risk Classifier** scores probability of delay and flags high-risk orders. | Earlier intervention, customer proactive notification, and reduced SLA penalty chargebacks. |
| **Terminal Hub Congestion** | Unbalanced arrival volumes create warehouse receiving queues and staging delays. | **Hub Congestion Classifier** (ROC-AUC: 0.8898) and **30-Day Workload Forecaster** project bottleneck risks. | Dynamic cross-dock scheduling and optimized terminal labor shift staffing. |
| **Unplanned Fleet Downtime** | Vehicles run until mechanical breakdown due to static, calendar-based maintenance schedules. | **Predictive Maintenance Classifier** combines engine temperature, mileage, and fault codes. | Minimized roadside breakdowns, reduced expedited towing costs, and higher asset utilization. |
| **Inaccurate Transit ETAs** | Static distance-over-speed calculations ignore priority, weather, and hub dwell times. | **Transit ETA Regressor** predicts delivery duration with statistical variance bands. | Realistic customer delivery promises and lower call center WISMO ("Where Is My Order") volume. |
| **Fragmented Executive Reporting** | Conflicting KPI calculations across branch offices and executive presentations. | Governed **Medallion Star-Schema** with **69 TMDL DAX measures** standardizing SLA formulas. | Unified corporate metrics, audit-ready data lineage, and trusted board-level visibility. |

---

## 📊 3. Key Project Metrics & Operational Scale

All metrics documented below reflect verified values from the repository datasets, dimensional warehouse tables, and automated test validations:

<div align="center">

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                              LOGITRACK OPERATIONAL SCALE                               │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│    27,979 Total Orders   │    6 Texas Hub Terminals │       107 Automated Tests        │
│   27,727 Fulfilled (99%) │   45 Commercial Vehicles │        100% Test Suite Pass Rate │
│      252 Cancelled (1%)  │   55 Certified Drivers   │        62% Statement Coverage    │
├──────────────────────────┴──────────────────────────┴──────────────────────────────────┤
│                              BASELINE SERVICE PERFORMANCE                              │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│    79.6% On-Time Delivery│   20.4% Delay Rate       │   5,653 Delayed Deliveries       │
│    (22,074 Orders)       │   (SLA Exception Window) │   (Tracked with Root Causes)     │
└──────────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

</div>

### Network Topology & Baseline Operational Distribution

* **Regional Hub Network (6 Hubs):** Dallas Main Hub (Central Gateway), Houston Hub, Austin Hub, San Antonio Hub, Fort Worth Hub, and El Paso Hub.
* **Commercial Fleet (45 Assets):** 33 Active line-haul and delivery assets, 12 in scheduled maintenance or reserve readiness; 41 tracked with near-real-time simulated GPS telematics.
* **Service Line Breakdown:** Standard Ground, Express Courier, and Freight line-haul operations.
* **Baseline Delay Distribution:** 5,653 delayed deliveries categorized into primary root causes: Heavy Traffic/Congestion (34.2%), Severe Weather (25.1%), Terminal Handling Delay (18.6%), Mechanical Dispatch Issue (13.4%), and Route Detour (8.7%).

> [!NOTE]
> **Data Transparency:** The 27,979 orders and associated vehicle telemetry represent a rigorously generated synthetic benchmark dataset designed to mirror realistic distribution distributions, diurnal patterns, and Texas supply chain logistics corridors without compromising proprietary shipper data.

---

## 🖼️ 4. Executive Dashboard & Operational Suite Preview

The production analytics suite is constructed using Microsoft Power BI's modern **Tabular Model Definition Language (TMDL)** and **PBIP (Power BI Project)** format, paired with a companion lightweight Streamlit Control Tower.

### Page 1: Executive Control Tower
> **Target Audience:** CEO, Chief Operating Officer, VP of Transportation
> **Key Decisions:** High-level SLA compliance monitoring, network throughput tracking, executive OTD trend analysis, and fleet utilization health.

![Executive Control Tower](dashboards/powerbi/LogiTrack_Analytics/Dashboard_Images/Executive_control_tower.png)

* **Key Features:** KPI summary cards (Total Orders, Delivered Volume, OTD Rate %, Delay Rate %, Fleet Active Ratio), daily delivery volume trends, service level breakdown, and regional performance matrices.

---

### Page 2: Regional Hub Operations & Capacity Management
> **Target Audience:** Director of Distribution, Terminal Operations Managers, Warehouse Shift Supervisors
> **Key Decisions:** Terminal capacity utilization, inbound/outbound volume balance, processing bottleneck detection, and labor shift scheduling.

![Regional Hub Operations](dashboards/powerbi/LogiTrack_Analytics/Dashboard_Images/Regional_Hub_Operations.png)

* **Key Features:** Hub throughput rankings, processing time distributions, capacity utilization heatmaps across the 6 Texas hubs, and threshold-based bottleneck alert indicators.

---

### Page 3: Delay & Root-Cause Analytics
> **Target Audience:** Quality Assurance Director, Customer Experience VP, Continuous Improvement Managers
> **Key Decisions:** Root-cause incident prioritization, carrier/driver coaching, chronic delay corridor remediation, and CSAT impact mitigation.

![Delay and Root Cause Analytics](dashboards/powerbi/LogiTrack_Analytics/Dashboard_Images/Delay_&_Root_Cause_Analytics.png)

* **Key Features:** Delay reason frequency Pareto analysis, delivery delay hours distribution, correlation between transit delay and CSAT degradation, and priority-level SLA breakdown.

---

### Page 4: Fleet Telematics & Asset Intelligence
> **Target Audience:** Fleet Maintenance Director, Chief Dispatcher, Safety & Compliance Officers
> **Key Decisions:** Real-time asset positioning, engine temperature safety alerts, preventative maintenance scheduling, and fuel efficiency optimization.

![Fleet Telematics and Maintenance](dashboards/powerbi/LogiTrack_Analytics/Dashboard_Images/Fleet_Telematrics_&_Maintenance.png)

* **Key Features:** Active fleet asset cards, telematics diagnostic signals (speed km/h, fuel %, engine temp °C, status), mileage thresholds, and high-risk maintenance alerts.

---

### Dedicated Drill-Through Analysis Pages & Contextual Tooltips

The Power BI model incorporates **8 dedicated drill-through pages** and **10 custom tooltip canvases** to enable deep root-cause forensic investigations without navigating away from primary operational workflows:

| Drill-Through & Tooltip Capability | Operational Investigation Enabled |
| :--- | :--- |
| **Hub Drill-Through (`Dril_Hub.png`)** | Isolates a specific hub's historical throughput, hourly congestion spikes, and regional delivery radius. |
| **Delay Reason Drill (`Drill_Delay_Reason.png`)** | Drills down from network delay KPIs into granular incidents, affected routes, and driver assignments. |
| **Fleet Asset Drill (`Drill_Vehicle.png`)** | Inspects individual vehicle service history, odometer milestones, telemetry history, and maintenance logs. |
| **KPI Pulse Tooltip (`Tooltip_KPI_Pulse.png`)** | Hovering over any KPI card displays 30-day sparklines, target thresholds, and month-over-month trajectory. |

<div align="center">

| Regional Hub Drill-Through | Delay Reason Root-Cause Drill |
| :---: | :---: |
| ![Hub Drill](dashboards/powerbi/LogiTrack_Analytics/Dashboard_Images/Dril_Hub.png) | ![Delay Reason Drill](dashboards/powerbi/LogiTrack_Analytics/Dashboard_Images/Drill_Delay_Reason.png) |

</div>

---

## 🏛️ 5. End-to-End System Architecture

The LogiTrack Intelligence architecture implements a decoupled, event-driven pattern designed for high throughput, reproducibility, and clear separation of concerns across data engineering, analytical modeling, and user presentation:

```mermaid
flowchart TD
    subgraph S1["1. Data Generation & Extraction"]
        D1["Raw CSV Operational Extracts\n(Orders, Hubs, Vehicles, Drivers)"]
        D2["IoT Telematics Generator\n(GPS Pings, Engine Diagnostics)"]
    end

    subgraph S2["2. Ingestion & Quality Lakehouse (DuckDB / Postgres)"]
        B1["Bronze Raw Layer\n(raw_orders, raw_hubs, raw_vehicles)"]
        G1["Data Quality Gate (DQ-001 - DQ-010)\n(Validation, Quarantine, Standardization)"]
        S11["Silver Staging Layer\n(stg_orders, stg_hubs, stg_vehicles)"]
        W1["Gold Dimensional Warehouse (Star Schema)\n(fact_orders, dim_hub, dim_vehicle, dim_driver, dim_date)"]
    end

    subgraph S3["3. Streaming & Event Consumer"]
        M1["MQTT Producer & Simulation\n(paho-mqtt / simulated queue)"]
        M2["Idempotent Consumer & DLQ\n(realtime.vehicle_events, dead_letter)"]
    end

    subgraph S4["4. Machine Learning & Forecasting"]
        ML1["Delay Classifier (XGBoost)\nTransit ETA Regressor"]
        ML2["Hub Congestion (Random Forest)\nFleet Maintenance (GBM)"]
        FC1["30-Day Demand & Workload Forecasters\n(Point Estimates + 95% Confidence Intervals)"]
    end

    subgraph S5["5. Serving, REST APIs & Dashboards"]
        API["FastAPI REST Microservice (:8000)\n(/kpis, /hubs, /fleet, /ml, /forecasting)"]
        PBI["Enterprise Power BI TMDL Suite\n(Executive Control Tower, Hubs, Fleet, Delays)"]
        STR["Streamlit Control Tower (:8501)\n(Interactive Diagnostics & Map Tracking)"]
    end

    D1 --> B1
    D2 --> M1
    M1 --> M2 --> W1
    B1 --> G1 --> S11 --> W1
    W1 --> ML1 & ML2 & FC1
    W1 & ML1 & FC1 --> API
    W1 --> PBI
    W1 & API --> STR
```

---

## 🤖 6. Predictive Intelligence & Forecasting Engine

LogiTrack Intelligence implements **4 specialized machine learning models** and **3 multi-horizon forecasting pipelines** to deliver forward-looking decision support across distinct logistics functions:

### Machine Learning Models (Evaluated on Historical Network Data)

| Model Name | Operational Purpose | Algorithm | Dataset Grain & Size | Key Features | Evaluated Metrics |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Delay Risk Classifier** | Scores pre-dispatch delivery delay probability | `XGBoostClassifier` | 27,727 historical deliveries (80/20 chronological split) | Distance (km), planned duration, package weight, priority, vehicle type, driver experience | **Accuracy:** 58.3%<br/>**Recall:** 34.4%<br/>**ROC-AUC:** 0.4989 (Baseline synthetic) |
| **Transit ETA Regressor** | Predicts real-time transit duration in hours | `XGBoostRegressor` | 27,727 completed shipment records | Route distance, priority, vehicle type, driver experience, planned hours | **MAE:** 18.87 hrs<br/>**MedAE:** 16.80 hrs<br/>**RMSE:** 23.93 hrs |
| **Hub Congestion Classifier** | Detects receiving and dispatch bottleneck risk | `RandomForestClassifier` | 4,296 hourly hub records across 6 hubs | Inbound orders, dispatch velocity, capacity ratio, hour of day, day of week | **ROC-AUC:** 0.8898<br/>**Accuracy:** 93.7%<br/>**Precision:** 1.0000 |
| **Fleet Maintenance Classifier** | Detects mechanical breakdown risk before failure | `GradientBoostingClassifier` | 45 commercial fleet vehicles | Odometer km, engine temp °C, speed variance, engine fault codes | **ROC-AUC:** 1.0000<br/>**Accuracy:** 100%<br/>**F1-Score:** 1.0000 |

### Multi-Horizon Forecasting Engine

| Forecaster Module | Target Projection | Horizon | Methodology | Verified Validation Metrics |
| :--- | :--- | :--- | :--- | :--- |
| **Regional Demand Forecaster** | Daily order demand volume per regional hub | 30 Days forward | Chronological Ridge / Random Forest regression with 95% Confidence Intervals | **Test MAE:** 1.96 orders<br/>**Test R²:** 0.5983<br/>**95% Interval Coverage:** 97.05% |
| **Hub Workload Forecaster** | Projected processing load vs daily capacity | 7 & 30 Days forward | Queue intake projection & capacity utilization risk classification | **Bottleneck Alerts:** Dynamic (Low / Medium / High / Critical) |
| **Fleet Requirement Forecaster** | Projected vehicle needs by type (Van, Truck, Reefer) | 30 Days forward | Demand-to-payload volumetric allocation modeling | **Output:** 720 scenario forecasts (30 days × 6 hubs × 4 vehicle types) |

> [!IMPORTANT]
> **Model Performance Qualification:** The models are trained on reproducible benchmark data. While the Hub Congestion (ROC-AUC: 0.8898) and Demand Forecaster (R²: 0.5983, 97.05% interval coverage) exhibit strong predictive power, the Delay Classifier's performance (ROC-AUC ~0.50) reflects the stochastic, uniformly distributed noise injected into the synthetic order delay generator. In a commercial deployment, additional telematics features (live road telemetry, weather API feeds, and real-time shipper dwell times) would be ingested to elevate discriminative power.

---

## ⚙️ 7. Data Engineering & Medallion Lakehouse Architecture

The analytical foundation follows the industry-standard **Medallion Architecture (Bronze ➔ Silver ➔ Gold)** hosted in an embedded, high-performance **DuckDB** lakehouse (fully portable to cloud PostgreSQL, Snowflake, or Databricks):

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                MEDALLION LAKEHOUSE LAYERS                              │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│       BRONZE LAYER       │       SILVER LAYER       │            GOLD LAYER            │
│   (Raw Source Records)   │  (Cleaned & Standardized)│   (Dimensional Star-Schema Mart) │
├──────────────────────────┼──────────────────────────┼──────────────────────────────────┤
│ • raw.raw_orders         │ • staging.stg_orders     │ • warehouse.fact_orders          │
│ • raw.raw_hubs           │ • staging.stg_hubs       │ • warehouse.fact_order_events    │
│ • raw.raw_vehicles       │ • staging.stg_vehicles   │ • warehouse.fact_vehicle_telem   │
│ • raw.raw_drivers        │ • staging.stg_drivers    │ • warehouse.fact_hub_hourly      │
│                          │ • realtime.vehicle_events│ • warehouse.dim_hub              │
│                          │ • realtime.order_events  │ • warehouse.dim_vehicle          │
│                          │                          │ • warehouse.dim_driver           │
│                          │                          │ • warehouse.dim_date             │
└──────────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

### Data Quality Gate (DQ-001 through DQ-010)

Before promotion to the Gold layer, every raw record passes through an automated validation suite:
* **DQ-001 (Primary Key Uniqueness):** Asserts zero duplicate primary keys across orders, hubs, vehicles, and drivers.
* **DQ-002 (Referential Integrity):** Validates that 100% of orders reference valid `hub_id`, `driver_id`, and `vehicle_code` keys.
* **DQ-003 (Logical Consistency):** Ensures cancelled orders have zero delivery dates and zero transit durations.
* **DQ-004 (SLA Temporal Sanity):** Verifies `actual_delivery_date >= order_date` and bounds delivery duration within physiological limits (0 to 120 hours).
* **DQ-005 (Coordinate Boundary Checks):** Confirms all GPS pings fall strictly within the Texas operational bounding box (Lat: `25.8°N - 36.5°N`, Lon: `-106.6°W - -93.5°W`).
* **DQ-006 (Quarantine Routing):** Malformed or unparseable records are diverted to dead-letter storage without blocking pipeline execution.

---

## 📡 8. IoT & Real-Time Event Simulation

To demonstrate modern real-time event streaming and fleet telematics capabilities without requiring a multi-million-dollar physical IoT sensor deployment, the platform includes a native streaming simulator built on **MQTT (Paho-MQTT)** and an asynchronous consumer pipeline:

* **Simulated Telematics Stream:** Emits real-time GPS coordinates, vehicle speed (km/h), fuel tank level (%), engine operating temperature (°C), and onboard diagnostic fault codes across 41 commercial fleet assets.
* **Event Topic Hierarchy:**
  * `logitrack/vehicle/telemetry`: Vehicle GPS pings, engine diagnostics, and speed alerts.
  * `logitrack/order/status`: Real-time order milestone transitions (`Created` ➔ `Dispatched` ➔ `In_Transit` ➔ `Delivered`).
  * `logitrack/hub/capacity`: Terminal gate check-in events and loading dock status.
* **Dead-Letter Queue (DLQ):** Messages failing JSON schema validation or event contract requirements are safely routed to `realtime.ingestion_errors` for offline auditing and alerting.

> [!NOTE]
> **Simulation Transparency:** All GPS telematics, engine diagnostics, and event streams are programmatically simulated to demonstrate near-real-time streaming, idempotent ingestion, and dead-letter routing capabilities in an end-to-end environment.

---

## ⚡ 9. API & Application Layer

LogiTrack Intelligence exposes its core analytical models, operational KPIs, and telematics through high-performance REST microservices built with **FastAPI** and an interactive **Streamlit Control Tower**:

### FastAPI REST Endpoints (`http://localhost:8000`)

| Method | Endpoint | Description | Response Schema |
| :--- | :--- | :--- | :--- |
| `GET` | `/health` | Lakehouse database connectivity & service health status | `HealthCheckResponse` |
| `GET` | `/api/v1/kpis/executive` | Executive Control Tower KPIs (OTD %, Delay %, Fleet Ratio, CSAT) | `ExecutiveKPIsResponse` |
| `GET` | `/api/v1/hubs` | Regional hub throughput, daily capacity, and geographic coordinates | `HubsResponse` |
| `GET` | `/api/v1/fleet` | Latest GPS coordinates, fuel %, and engine health for active fleet | `FleetResponse` |
| `POST` | `/api/v1/ml/predict-delay` | Real-time order delay risk scoring with XGBoost classifier | `DelayPredictionResponse` |
| `POST` | `/api/v1/ml/predict-eta` | Real-time transit duration prediction with statistical variance bands | `ETAPredictionResponse` |
| `GET` | `/api/v1/ml/models` | Active model registry metadata, versions, and algorithm details | `ModelRegistryResponse` |
| `GET` | `/api/v1/forecasting/demand` | 7-day to 30-day regional order demand forecast with 95% Confidence Intervals | `DemandForecastResponse` |
| `GET` | `/api/v1/forecasting/workload` | Forward hub workload projection and capacity bottleneck risk levels | `HubWorkloadResponse` |
| `GET` | `/api/v1/forecasting/fleet` | Forward fleet vehicle requirement forecasts by vehicle asset type | `FleetForecastResponse` |

### Streamlit Operational Control Tower (`http://localhost:8501`)

The repository includes a companion operational console providing:
1. **Interactive KPI Overview:** Real-time metrics with threshold-based conditional alerting.
2. **Texas Regional Telematics Map:** Live geospatial plotting of vehicle locations, route corridors, and hub distribution centers.
3. **Hub Workload Diagnostics:** Interactive capacity utilization sliders and terminal congestion alerts.
4. **Predictive What-If Scenarios:** Real-time inference simulator allowing operators to test how package weight, driver experience, and priority impact delay probability.

---

## 📈 10. Power BI TMDL Semantic Modeling & DAX Library

The enterprise Power BI solution is authored as a version-controlled **Power BI Project (`.pbip`)** using **Tabular Model Definition Language (TMDL)**, enabling software-grade version control, code reviews, and automated CI/CD deployment.

### Architecture of the DAX Measure Library

The repository contains three levels of measure governance to eliminate calculation inconsistencies:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                            DAX MEASURE GOVERNANCE STRUCTURE                            │
├──────────────────────────┬──────────────────────────┬──────────────────────────────────┤
│    37 Production KPIs    │   69 TMDL Model Measures │   87 Master Reference Library    │
│  (Executive & SLA Core)  │  (Active in PBIP Model)  │  (Includes UI & Color Helpers)   │
└──────────────────────────┴──────────────────────────┴──────────────────────────────────┘
```

1. **37 Production KPI Measures:** The core business metrics defining executive delivery performance (Folders 01–05: Executive KPIs, Delivery SLAs, Hub Operations, Fleet Telematics, and Driver Performance).
2. **69 TMDL Model Measures:** The complete set of active measures compiled directly inside `dashboards/powerbi/LogiTrack_Analytics/LogiTrack_Analytics_(pbip).SemanticModel/definition/tables/_Measures.tmdl`.
3. **87 Master Reference Measures:** Documented in `dashboards/powerbi/dax_measures.txt`, containing all 69 operational measures plus 18 visual helper measures (dynamic conditional formatting HEX colors, target reference lines, dynamic card titles, and contextual drill-through breadcrumbs).

### Core Executive DAX Formulas

```dax
// 1. Executive On-Time Delivery Rate (OTD %) — Strict SLA Standard
[On-Time Delivery Rate %] =
DIVIDE(
    CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[is_on_time] = TRUE(), 'fact_orders'[order_status] = "Delivered"),
    CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[order_status] = "Delivered"),
    0
)

// 2. Network Delivery Delay Rate %
[Delivery Delay Rate %] =
DIVIDE(
    CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[is_delayed] = TRUE(), 'fact_orders'[order_status] = "Delivered"),
    CALCULATE(COUNTROWS('fact_orders'), 'fact_orders'[order_status] = "Delivered"),
    0
)

// 3. Commercial Fleet Active Utilization Ratio %
[Fleet Utilization Rate %] =
DIVIDE(
    CALCULATE(COUNTROWS('dim_vehicle'), 'dim_vehicle'[current_status] = "Active"),
    COUNTROWS('dim_vehicle'),
    0
)
```

---

## 🛡️ 11. Automated Testing & CI/CD Pipeline

To ensure reliability, migration idempotency, and regression prevention, the repository is guarded by an automated **GitHub Actions CI/CD pipeline** running across 5 orchestrated jobs:

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                           GITHUB ACTIONS ORCHESTRATION PIPELINE                         │
├───────────────────┬───────────────────┬───────────────────┬───────────────────┬─────────┤
│   Code Quality    │    Test Suite     │   Health Check    │  API Smoke Test   │ Summary │
│  (Ruff / Black)   │ (107 Tests / 62%) │  (Drift Monitor)  │  (Endpoints/E2E)  │ (Report)│
└───────────────────┴───────────────────┴───────────────────┴───────────────────┴─────────┘
```

### Verified Test Suite Summary (107 Tests / 100% Pass Rate)

| Test Category | Test File(s) | Tests | Verified Scope |
| :--- | :--- | :---: | :--- |
| **Foundation & Environment** | `tests/test_foundation.py` | 5 | Python 3.11 environment, package imports, critical directory paths, secrets isolation |
| **Batch Ingestion & ETL** | `tests/unit/test_batch_pipeline.py` | 4 | Source data extraction, mixed date formatting, quarantine logic, idempotent reload |
| **Data Quality & Integrity** | `tests/data_quality/test_source_integrity.py`<br/>`tests/data_quality/test_warehouse_models.py` | 12 | Primary key uniqueness, foreign key integrity, Texas coordinate bounds, grain verification |
| **Database Schema** | `tests/integration/test_database_schema.py` | 7 | Migration execution across 6 SQL files, schema existence (raw, staging, warehouse, ml) |
| **IoT & Streaming Engine** | `tests/unit/test_streaming.py`<br/>`tests/unit/test_simulation.py` | 13 | Event contract schemas, QoS 1 deduplication, DLQ error routing, Texas GPS simulation |
| **ML Models & Inference** | `tests/unit/test_ml_models.py` | 13 | Model serialization, ROC-AUC evaluation, feature transformation, inference schema bounds |
| **Forecasting Engine** | `tests/unit/test_forecasting.py`<br/>`tests/unit/test_forecasting_quality.py` | 23 | Forward horizon validation, 95% Confidence Interval ordering, non-negative demand constraints |
| **Operational Health Monitor** | `tests/unit/test_monitoring.py` | 8 | Lakehouse table completeness, model artifact freshness, KPI drift detection |
| **API Endpoints & Contracts** | `tests/api/test_api_endpoints.py` | 10 | FastAPI route responses, status codes, query filtering, telematics response contracts |
| **End-to-End Operational Pipeline** | `tests/end_to_end/test_pipeline_e2e.py` | 8 | End-to-end integration: Raw ingestion ➔ Lakehouse ➔ ML inference ➔ Forecasts ➔ API |
| **Analytics & Dashboards** | `tests/unit/test_dashboards.py` | 4 | OTD and Delay rate mathematical edge cases (division-by-zero protection) |
| **TOTAL VERIFIED SUITE** | **13 Test Modules** | **107** | **107 Passed (100%), 0 Failures, 62% Statement Coverage** |

> [!NOTE]
> **Advisory Quality Checks:** In the `code-quality` workflow job, style and linting checks (Ruff, Black, isort) run with `continue-on-error: true` as non-blocking advisory gates due to historical codebase formatting conventions. All functional test jobs (`test-suite`, `health-check`, `api-smoke-test`) are 100% strictly blocking with enforced coverage thresholds.

---

## 🧰 12. Complete Technology Stack

| Architecture Domain | Technologies & Libraries | Practical Role in Platform |
| :--- | :--- | :--- |
| **Core Programming** | **Python 3.11** | Core language for pipelines, models, APIs, and automated testing |
| **Data Lakehouse** | **DuckDB**, **PostgreSQL**, **SQLAlchemy** | Local analytical lakehouse, transactional schema storage, and migration execution |
| **Data Engineering** | **Pandas**, **NumPy**, **PyArrow** | Data ingestion, date standardization, schema casting, and Parquet archiving |
| **Data Quality** | **Custom Quality Gate Engine** (DQ-001 - DQ-010) | Automated validation, schema enforcement, and quarantine routing |
| **Streaming & IoT** | **Paho-MQTT**, **JSON Schema**, **Loguru** | Asynchronous IoT telematics generation, MQTT message consumer, and DLQ handling |
| **Machine Learning** | **Scikit-Learn**, **XGBoost**, **LightGBM**, **Joblib** | Predictive classification, duration regression, and model artifact persistence |
| **Forecasting** | **Statsmodels**, **Ridge Regression**, **Prophet** | Time-series decomposition, 30-day demand projections, and 95% Confidence Intervals |
| **API & Microservices** | **FastAPI**, **Uvicorn**, **Pydantic v2**, **HTTPX** | High-concurrency REST endpoints, schema validation, and health checks |
| **Business Intelligence** | **Microsoft Power BI (PBIP / TMDL)**, **DAX** | Enterprise semantic model, 4 operational pages, 8 drill-throughs, custom Midnight Theme |
| **Operational UI** | **Streamlit**, **Plotly**, **Folium** | Rapid operational control tower, interactive telematics map, and what-if simulation |
| **Quality Assurance** | **Pytest**, **Pytest-Cov**, **Pytest-Asyncio** | 107-test automated verification suite with XML and HTML coverage reporting |
| **DevOps & CI/CD** | **GitHub Actions**, **Docker**, **Docker Compose** | Multi-job CI/CD pipeline, containerized multi-service deployment, and build reporting |

---

## 🚀 13. Installation & Quick Start Guide

### Prerequisites
* **Operating System:** Windows 10/11, macOS, or Linux (Ubuntu 20.04+)
* **Python Version:** Python **3.11** recommended
* **Git:** Version 2.30+ installed
* **Optional:** Power BI Desktop (for opening PBIP/PBIX files) or Docker Engine

### Local Environment Setup

#### 1. Clone Repository & Create Virtual Environment
```bash
# Clone the repository
git clone https://github.com/RyadulSeam/LogiTrack-Intelligence.git
cd LogiTrack-Intelligence

# Create Python 3.11 virtual environment
python -m venv .venv

# Activate virtual environment
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Linux / macOS:
# source .venv/bin/activate
```

#### 2. Install Dependencies
```bash
# Upgrade pip
python -m pip install --upgrade pip

# Install complete platform with all optional dependencies:
pip install -e ".[simulation,streaming,database,ml,api,testing,dashboards]"

# Or install all extras at once:
pip install -e ".[all]"
```

#### 3. Initialize Lakehouse & Train ML Models
Run the verified 6-step initialization sequence to generate the DuckDB lakehouse, run migrations, simulate streaming telemetry, build dimensional models, and train machine learning artifacts:

```bash
python -c "
import sys; sys.path.insert(0, 'src'); sys.path.insert(0, '.')
from scripts.run_migrations import run_duckdb_migrations
from logitrack.ingestion.pipeline import run_batch_pipeline
from logitrack.streaming.stream_runner import run_streaming_simulation
from logitrack.transformation.warehouse_builder import build_warehouse_tables
from logitrack.ml.train_all import run_training_pipeline
from logitrack.forecasting.train_all import run_forecasting_pipeline

print('1. Running migrations...'); run_duckdb_migrations()
print('2. Ingesting batch data...'); run_batch_pipeline()
print('3. Simulating streaming telemetry...'); run_streaming_simulation()
print('4. Building warehouse dimensional models...'); build_warehouse_tables()
print('5. Training ML models...'); run_training_pipeline()
print('6. Running forecasting pipeline...'); run_forecasting_pipeline()
print('Lakehouse initialization complete!')
"
```

#### 4. Run the 107-Test Automated Verification Suite
```bash
# Run all tests with coverage report
pytest -v --tb=short --cov=src/logitrack --cov-report=term-missing
```

#### 5. Launch Application Services
```bash
# Terminal 1: Launch FastAPI REST Microservice
uvicorn logitrack.api.main:app --host 0.0.0.0 --port 8000 --reload
# Interactive Swagger Documentation: http://localhost:8000/docs

# Terminal 2: Launch Streamlit Operational Control Tower
streamlit run dashboards/streamlit/app.py --server.port 8501
# Operational Dashboard URL: http://localhost:8501
```

#### 6. Open Power BI Analytics
Open the master Power BI Project file directly in Microsoft Power BI Desktop:
`dashboards/powerbi/LogiTrack_Analytics/LogiTrack_Analytics_(pbip).pbip`

---

## 📁 14. Project Directory Structure

```
LogiTrack-Intelligence/
├── .github/workflows/ci.yml           # GitHub Actions 5-job CI/CD workflow
├── app/                               # Lightweight application entrypoint
├── data/
│   ├── source/                        # Raw source CSV datasets (Orders, Hubs, Vehicles, Drivers)
│   └── lake/                          # Local DuckDB analytical lakehouse (logitrack.duckdb)
├── database/migrations/               # 6 idempotent SQL migration scripts (001 to 006)
├── dashboards/
│   ├── powerbi/                       # Enterprise Power BI Suite
│   │   ├── LogiTrack_Analytics/       # Master PBIP & TMDL model project
│   │   │   ├── Dashboard_Images/      # High-res operational screenshots (Pages, Drills, Tooltips)
│   │   │   ├── LogiTrack_Analytics_(pbip).pbip
│   │   │   └── LogiTrack_Analytics_(pbip).SemanticModel/ # TMDL definitions & 69 measures
│   │   ├── dax_measures.txt           # Master 87-measure DAX production reference library
│   │   └── semantic_views.sql         # 7 production SQL semantic views
│   └── streamlit/app.py               # Streamlit Operational Control Tower & Map Viewer
├── deployment/docker/                 # Dockerfiles & container deployment configurations
├── models/artifacts/                  # Persisted ML and forecasting .joblib model bundles
├── scripts/                           # Database migration, audit, and verification utilities
├── src/logitrack/                     # Core production Python package
│   ├── analytics/                     # Metric computation engine (SLA, OTD, Congestion)
│   ├── api/                           # FastAPI application, routes, and Pydantic schemas
│   ├── forecasting/                   # Multi-horizon demand, workload, and fleet forecasters
│   ├── ingestion/                     # Extract, clean, transform, and quality gate engine
│   ├── ml/                            # XGBoost classifiers, ETA regressors, and training pipelines
│   ├── monitoring/                    # Table health, model freshness, and KPI drift monitors
│   ├── simulation/                    # Real-time event generators & Texas GPS bounding logic
│   ├── storage/                       # DuckDB and PostgreSQL database connection managers
│   ├── streaming/                     # MQTT producer, consumer, contract validation, and DLQ
│   └── transformation/                # Warehouse star-schema dimensional builders
├── tests/                             # 107-test automated verification suite
│   ├── api/                           # FastAPI endpoint tests
│   ├── data_quality/                  # Source data and warehouse model integrity tests
│   ├── end_to_end/                    # Full pipeline end-to-end integration tests
│   ├── integration/                   # Database schema and migration tests
│   └── unit/                          # Unit tests across ETL, ML, forecasting, and streaming
├── pyproject.toml                     # Modern PEP 621 package metadata & optional dependency groups
└── README.md                          # Master platform documentation
```

---

## 🔍 15. Limitations, Assumptions & Data Transparency

To maintain technical credibility and clear business expectations with enterprise evaluators, the following design boundaries and data characteristics are explicitly documented:

1. **Benchmark Synthetic Data:** The 27,979 shipment records and associated fleet telematics represent a statistically synthesized operational dataset. Patterns in customer ordering, transit delays, and Texas hub volumes are modeled after real-world logistics distributions, but do not originate from a commercial carrier's production database.
2. **Simulated Telematics:** Fleet GPS telemetry pings, speed readings, and engine temperatures are generated via an internal simulation engine and dispatched through MQTT message brokers. The platform does not currently maintain active integrations with physical OBD-II telematics hardware (e.g., Geotab, Samsara).
3. **Machine Learning Noise Characteristics:** The Delay Risk Classifier's evaluation score (ROC-AUC ~0.50) directly reflects the random uniform noise injected into the synthetic order delay generator. In an enterprise operational deployment, access to real-time external features—such as live roadway congestion feeds, localized National Weather Service alerts, and shipper dock dwell times—would be required to achieve commercial-grade predictive discrimination.
4. **Local vs Cloud Deployment:** By default, the platform runs in an embedded local environment utilizing DuckDB for sub-second analytical execution without cloud infrastructure overhead. The SQL migrations and dimensional schemas are designed to be fully portable to enterprise data platforms such as Snowflake, Amazon Redshift, Google BigQuery, or Databricks.

---


## 👨‍💼 About the Consultant

<div align="center">

### **Ryadul Islam Seam**
**Logistics & Operations Analytics Consultant**  
*Predictive Delivery Risk & Automated Power BI Dashboards for E-Commerce, Retail & Distribution*

[![LinkedIn Profile](https://img.shields.io/badge/LinkedIn-Connect%20with%20Ryadul-0A66C2?style=for-the-badge&logo=linkedin)](https://www.linkedin.com/in/ryadulseam-data)
[![GitHub Profile](https://img.shields.io/badge/GitHub-Follow%20on%20GitHub-181717?style=for-the-badge&logo=github)](https://github.com/RyadulSeam)

</div>

### Core Consulting Capabilities:

- **Logistics & Supply Chain Analytics**: SLA delivery compliance, root-cause delay attribution, warehouse dwell analysis, and fleet utilization benchmarking.
- **Executive Business Intelligence**: Enterprise Power BI dashboard architecture, advanced DAX calculations, Star-Schema tabular data modeling, and corporate UI/UX styling.
- **Data Engineering & Lakehousing**: Python ETL pipelines, dbt Core dimensional modeling, DuckDB OLAP lakehouse design, and PostgreSQL transactional architecture.
- **Predictive Machine Learning**: Applied classification and regression (XGBoost, Scikit-learn), multi-horizon time-series forecasting (Prophet, Statsmodels), and model drift monitoring.
- **Production Architecture**: FastAPI REST API development, Docker multi-container orchestration, and automated CI/CD quality engineering.

---

## 📬 Contact & Consulting Engagement

Are delivery delays, fragmented spreadsheets, or opaque operational data impacting your supply chain performance?

I partner with logistics carriers, 3PL providers, retail distributors, and e-commerce brands to build automated reporting infrastructure and predictive operational intelligence:

- **Automated Power BI Operations Dashboards** tailored to your WMS, OMS, and fleet systems.
- **Predictive Delivery Risk Systems** that identify SLA breaches before departure.
- **Modern Data Lakehouse Infrastructure** replacing brittle manual spreadsheets with reliable reporting.

**Let's discuss how data-driven intelligence can optimize your distribution operations:**

- **LinkedIn**: [linkedin.com/in/ryadulseam-data](https://www.linkedin.com/in/ryadulseam-data)
- **GitHub**: [github.com/RyadulSeam](https://github.com/RyadulSeam)
- **Project Repository**: [github.com/RyadulSeam/LogiTrack-Intelligence](https://github.com/RyadulSeam/LogiTrack-Intelligence)

---

## 📄 License

This project is open-source and distributed under the **MIT License**. See the [LICENSE](LICENSE) file for complete details.

---

<div align="center">
  <sub>LogiTrack Intelligence v1.0.0 • Designed, Engineered, and Documented by Ryadul Islam Seam • © 2026</sub>
</div>

