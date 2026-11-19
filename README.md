<p align="center">
  <h1 align="center">🚛 LogiTrack Intelligence</h1>
  <p align="center">
    <strong>Enterprise Logistics Data & Predictive Operations Platform</strong>
  </p>
  <p align="center">
    End-to-end data engineering, real-time streaming, warehouse modeling,<br/>
    business intelligence, and machine learning for logistics operations.
  </p>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.10%2B-blue?logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/PostgreSQL-Neon-green?logo=postgresql&logoColor=white" alt="Neon"/>
  <img src="https://img.shields.io/badge/DuckDB-Analytics-yellow?logo=duckdb&logoColor=white" alt="DuckDB"/>
  <img src="https://img.shields.io/badge/MQTT-Mosquitto-purple?logo=eclipsemosquitto&logoColor=white" alt="MQTT"/>
  <img src="https://img.shields.io/badge/dbt-Transform-orange?logo=dbt&logoColor=white" alt="dbt"/>
  <img src="https://img.shields.io/badge/FastAPI-Serve-teal?logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/license-MIT-brightgreen" alt="License"/>
</p>

---

## 📋 Overview

**LogiTrack Intelligence** is a full-stack logistics data platform that demonstrates
production-grade data engineering, analytics, and machine learning capabilities.

The platform ingests historical and simulated real-time data from vehicles, drivers,
hubs, and orders — transforming raw operational signals into actionable intelligence
through a modern data stack.

### Key Capabilities

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Ingestion** | Python Batch ETL, MQTT Streaming | Historical + real-time data capture |
| **Storage** | Neon PostgreSQL, DuckDB, Parquet | Cloud relational + local analytics + data lake |
| **Transformation** | dbt Core, SQL, Python | Bronze → Silver → Gold medallion architecture |
| **BI & Dashboards** | Power BI, Streamlit, Grafana | Executive, operational, and monitoring views |
| **Machine Learning** | Scikit-learn, XGBoost, Prophet | Delay prediction, ETA, demand forecasting |
| **Application** | FastAPI, Streamlit | REST API + operational control tower |
| **Reliability** | Pytest, GitHub Actions, Grafana | Testing, CI/CD, monitoring |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                            │
│  Orders · Vehicles · Drivers · Hubs · GPS · Maintenance     │
└──────────┬─────────────────────────────────┬────────────────┘
           │ Batch ETL                       │ MQTT Streaming
           ▼                                 ▼
┌─────────────────────┐         ┌─────────────────────────┐
│  Neon PostgreSQL    │         │  Mosquitto MQTT Broker   │
│  (Cloud Database)   │◄────────│  (Event Ingestion)       │
└──────────┬──────────┘         └─────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────────────────┐
│               TRANSFORMATION (dbt Core)                     │
│         Bronze  ──►  Silver  ──►  Gold                      │
└──────────┬──────────────────────────────────┬───────────────┘
           │                                  │
           ▼                                  ▼
┌─────────────────────┐         ┌─────────────────────────┐
│   BI & Dashboards   │         │   ML & Forecasting      │
│  Power BI           │         │  Delay Risk Prediction  │
│  Streamlit          │         │  ETA Estimation         │
│  Grafana            │         │  Demand Forecasting     │
└─────────────────────┘         │  Predictive Maintenance │
                                └──────────┬──────────────┘
                                           │
                                           ▼
                                ┌─────────────────────────┐
                                │   FastAPI + Streamlit    │
                                │   Operations Control    │
                                │   Tower                 │
                                └─────────────────────────┘
```

---

## 📁 Project Structure

```
LogiTrack-Intelligence/
│
├── configs/              # YAML configuration files
├── data/
│   ├── source/           # Original historical datasets (immutable)
│   ├── synthetic/        # Generated synthetic data
│   ├── processed/        # Cleaned & transformed outputs
│   ├── quarantine/       # Rejected / invalid records
│   └── lake/             # Parquet data lake
│
├── docs/                 # Project documentation
├── scripts/              # Utility & automation scripts
├── src/logitrack/        # Core application source code
│   ├── ingestion/        # Batch ETL pipeline
│   ├── simulation/       # Synthetic data generators
│   ├── streaming/        # MQTT producer & consumer
│   ├── transformation/   # Data quality & cleaning
│   ├── ml/               # Machine learning models
│   ├── forecasting/      # Time-series forecasting
│   ├── api/              # FastAPI application
│   └── monitoring/       # System health & drift monitoring
│
├── database/             # SQL migrations & schemas
├── dbt_project/          # dbt transformation models
├── notebooks/            # Exploratory analysis notebooks
├── dashboards/           # Dashboard configurations
├── tests/                # Pytest test suites
├── deployment/           # Docker & service configs
└── .github/workflows/    # CI/CD pipelines
```

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Git
- Docker Desktop (for Mosquitto MQTT)
- Power BI Desktop (optional, for BI reports)

### Setup

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/LogiTrack-Intelligence.git
cd LogiTrack-Intelligence

# Create virtual environment
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash
# or
.venv\Scripts\activate          # Windows CMD/PowerShell

# Install core dependencies
pip install -e .

# Copy environment config
cp .env.example .env
# Edit .env with your Neon credentials
```

### Phase-Specific Dependencies

```bash
pip install -e ".[audit]"       # Phase 1: Data profiling
pip install -e ".[simulation]"  # Phase 2: Synthetic data
pip install -e ".[database]"    # Phase 3: Database setup
pip install -e ".[streaming]"   # Phase 5: MQTT streaming
pip install -e ".[ml]"          # Phase 8-9: ML & forecasting
pip install -e ".[api]"         # Phase 10: FastAPI
pip install -e ".[all]"         # Everything
```

---

## 📊 Source Datasets

| Dataset | Records | Description |
|---------|---------|-------------|
| `Hubs.csv` | 6 | Logistics hub locations in Texas |
| `Drivers.csv` | 55 | Driver profiles and performance |
| `Vehicles.csv` | 45 | Fleet vehicles and maintenance status |
| `Orders.csv` | 27,979 | Delivery orders with lifecycle data |

> **Data Provenance:** The platform clearly separates **original historical data**,
> **synthetic historical data**, and **simulated real-time events**.
> All dashboards and models label data origin transparently.

---

## 📈 Implementation Phases

| Phase | Focus | Status |
|-------|-------|--------|
| **0** | Project Discovery & Business Requirements | ✅ Completed |
| **1** | Source Data Audit & Data Governance | ✅ Completed |
| **2** | Realistic Synthetic Data Engineering | ✅ Completed |
| **3** | Database Design & Cloud Storage | ✅ Completed |
| **4** | Batch Data Engineering Pipeline | ✅ Completed |
| **5** | Real-Time Event Streaming | ✅ Completed |
| **6** | Enterprise Data Warehouse (dbt) | ✅ Completed |
| **7** | BI & Operational Dashboards | ✅ Completed |
| **8** | Machine Learning Engineering | ✅ Completed |
| **9** | Forecasting Engineering | ✅ Completed |
| **10** | API & Application Layer | ✅ Completed |
| **11** | Monitoring, Testing & CI/CD | ✅ Completed |
| **12** | Final Production-Style Release | 🔲 Next |

---

## 🛠️ Tech Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.10+ |
| Cloud Database | Neon (Serverless PostgreSQL) |
| Local Analytics | DuckDB |
| Data Lake | Apache Parquet |
| Streaming | MQTT + Eclipse Mosquitto |
| Transformation | dbt Core + SQL + Python |
| BI | Power BI Desktop, Streamlit, Grafana |
| ML | Scikit-learn, XGBoost, LightGBM |
| Forecasting | Prophet, Statsmodels |
| API | FastAPI + Uvicorn |
| Testing | Pytest + GitHub Actions |
| Containerization | Docker + Docker Compose |

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file.

---

## 👤 Author

**Ryadul Seam** — [GitHub](https://github.com/YOUR_USERNAME)
