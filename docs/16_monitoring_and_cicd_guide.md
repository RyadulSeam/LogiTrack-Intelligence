# LogiTrack Intelligence — Monitoring, Testing & CI/CD Guide
**Phase 11 Deliverable | Version 1.0.0**

---

## 1. Executive Summary

Phase 11 implements the enterprise-grade monitoring, automated testing, and CI/CD quality assurance framework for the LogiTrack Intelligence data platform. It guarantees data integrity, model freshness, SLA performance, and system stability across all layers of the logistics architecture.

```
┌────────────────────────────────────────────────────────────────────────┐
│                      LOGITRACK CI/CD & RELIABILITY                     │
└────────────────────────────────────────────────────────────────────────┘
                                    │
    ┌───────────────────────────────┼───────────────────────────────┐
    ▼                               ▼                               ▼
┌─────────────────────────┐   ┌─────────────────────────┐   ┌─────────────────────────┐
│     CONTINUOUS CI/CD    │   │    TEST SUITE ENGINE    │   │    SYSTEM MONITORING    │
│  .github/workflows/     │   │  tests/ (107 Tests)     │   │  src/logitrack/         │
│  ci.yml (5 Jobs)        │   │  Coverage: 62%          │   │  monitoring/            │
│  • code-quality         │   │  • Unit & Integration   │   │  • Table Health         │
│  • test-suite (3.11/12) │   │  • Data Quality & E2E   │   │  • Model Freshness      │
│  • health-check         │   │  • ML & Forecasting Q/A │   │  • Completeness Checks  │
│  • api-smoke-test       │   │  • REST API Contracts   │   │  • KPI Drift Detection  │
│  • build-report         │   │  • Regression & Schemas │   │  • ML Model Drift       │
└─────────────────────────┘   └─────────────────────────┘   └─────────────────────────┘
```

---

## 2. System Health & Drift Monitoring Architecture

The monitoring module resides under `src/logitrack/monitoring/` and operates as a standalone diagnostic engine or imported Python library for scheduled automations and health check APIs.

### 2.1 Table Health Monitor (`check_lakehouse_table_health`)
Scans 13 key tables across all lakehouse layers in DuckDB (`data/lake/logitrack.duckdb`):
- **Staging Layer**: `staging.stg_orders`, `staging.stg_vehicles`, `staging.stg_hubs`, `staging.stg_drivers`
- **Warehouse Layer**: `warehouse.fact_orders`, `warehouse.dim_hub`, `warehouse.dim_driver`, `warehouse.dim_vehicle`, `warehouse.dim_route`
- **Forecasting Layer**: `forecasting.demand_forecasts`, `forecasting.hub_workload_forecasts`, `forecasting.fleet_requirement_forecasts`
- **Machine Learning Layer**: `ml.model_registry`

Each table is evaluated for existence, minimum row threshold, and schema validity.

### 2.2 Model Artifact Freshness Monitor (`check_model_artifact_freshness`)
Inspects trained `.joblib` model binaries located in `models/artifacts/`:
- `delay_risk_classifier.joblib`
- `eta_regressor.joblib`
- `hub_congestion_model.joblib`
- `maintenance_classifier.joblib`
- `demand_forecaster.joblib`
- `hub_workload_forecaster.joblib`
- `fleet_requirement_forecaster.joblib`

Validates file presence, non-zero file size, and timestamp freshness against max-age thresholds (default: 30 days).

### 2.3 Data Completeness Monitor (`check_data_completeness`)
Executes null-rate validations across 11 business-critical attributes:
- `fact_orders.order_id` (0.0% null allowed)
- `fact_orders.driver_id` (0.0% null allowed)
- `fact_orders.vehicle_code` (0.0% null allowed)
- `fact_orders.origin_hub_id` & `destination_hub_id` (0.0% null allowed)
- `fact_orders.delivery_status` (0.0% null allowed)
- `dim_hub.latitude` & `dim_hub.longitude` (0.0% null allowed)

Returns percentage completeness and flags violations exceeding strict tolerances.

### 2.4 KPI Drift Detection (`check_kpi_drift`)
Compares active lakehouse metrics against established business baselines:
- **Total Orders**: Baseline 27,979
- **Delivered Orders**: Baseline 27,727 (used as denominator for delivery SLAs)
- **On-Time Delivery (OTD) Rate**: Baseline 79.6% (tolerance ±5.0%)
- **Delay Rate**: Baseline 20.4% (tolerance ±5.0%)

### 2.5 Machine Learning Drift Monitor (`src/logitrack/monitoring/model_monitor.py`)
Re-evaluates deployed ML pipelines against current warehouse ground truth:
- **Delay Risk Classifier**: Evaluates Area Under ROC Curve (ROC-AUC target ≥ 0.65).
- **ETA Regressor**: Evaluates Mean Absolute Error (MAE target ≤ 12.0 hours).
- **Composite Drift Report**: Aggregates model drift status, triggering automated retraining alerts when performance metrics degrade.

---

## 3. Test Suite Architecture

The test suite consists of **107 passing automated tests** organized across functional domains:

| Test Module | Test File | Cases | Primary Scope |
|---|---|:---:|---|
| **Foundation** | `tests/test_foundation.py` | 5 | Python version, package imports, directory structure, secrets audit |
| **Monitoring** | `tests/unit/test_monitoring.py` | 20 | Table health, model freshness, data completeness, KPI drift |
| **Forecasting QA** | `tests/unit/test_forecasting_quality.py` | 19 | Forecast schemas, horizon bounds, confidence intervals, provenance |
| **REST API** | `tests/api/test_api_endpoints.py` | 10 | FastAPI endpoints: health, KPIs, hubs, fleet, ML, forecasts |
| **End-to-End** | `tests/end_to_end/test_pipeline_e2e.py` | 8 | Lakehouse-to-API consistency, full lifecycle pipelines |
| **Data Quality** | `tests/data_quality/test_source_integrity.py` | 7 | PK uniqueness, referential integrity, status consistency |
| **Warehouse** | `tests/data_quality/test_warehouse_models.py` | 5 | Grain, referential integrity, date coverage, coordinates |
| **Database Schema**| `tests/integration/test_database_schema.py` | 7 | Schema creation, raw/staging/gold tables, migration idempotency |
| **Batch ETL** | `tests/unit/test_batch_pipeline.py` | 4 | Extraction, date standardization, quarantine gate |
| **BI Metrics** | `tests/unit/test_dashboards.py` | 6 | OTD calculation, zero division handling, SLA formulas |
| **ML Models** | `tests/unit/test_ml_models.py` | 6 | Lifecycle, features, delay classifier, ETA regressor |
| **Simulation** | `tests/unit/test_simulation.py` | 5 | Haversine distance, seed determinism, provenance, bounding box |
| **Streaming** | `tests/unit/test_streaming.py` | 5 | Event contracts, validation bounds, deduplication, dead-letter |
| **Total** | | **107** | **100% Pass Rate** |

---

## 4. Test Coverage Reporting

Coverage is calculated using `pytest-cov` against the `src/logitrack` package:
- **Overall Line Coverage**: **62%** (exceeding the CI minimum threshold of **55%**)
- **Coverage Reports**:
  - Terminal missing-line summary
  - HTML visual report: `htmlcov/index.html`
  - XML machine-readable report: `coverage.xml`

### Key Module Coverage Highlights
- `src/logitrack/ingestion/transform.py`: **100%**
- `src/logitrack/ingestion/clean.py`: **100%**
- `src/logitrack/analytics/metrics.py`: **98%**
- `src/logitrack/ml/eta_regressor.py`: **98%**
- `src/logitrack/ml/hub_congestion.py`: **97%**
- `src/logitrack/ml/delay_classifier.py`: **96%**
- `src/logitrack/api/schemas.py`: **100%**
- `src/logitrack/api/routes/fleet.py`: **100%**
- `src/logitrack/api/routes/hubs.py`: **100%**
- `src/logitrack/api/routes/kpis.py`: **100%**
- `src/logitrack/monitoring/health_monitor.py`: **91%**

---

## 5. CI/CD Automation Pipeline (`.github/workflows/ci.yml`)

The GitHub Actions workflow automates quality gates on every push to `main` and `develop` and on all pull requests.

```
┌────────────────────────────────────────────────────────────────────────┐
│                        GITHUB ACTIONS CI PIPELINE                      │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Job 1: code-quality                                                    │
│ Ruff linter  •  isort import sorting  •  Black code formatting         │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Job 2: test-suite (Matrix: Python 3.11 & 3.12)                         │
│ Seed DuckDB  •  107 Tests  •  Coverage >= 55%  •  Upload to Codecov    │
└──────────────────┬────────────────┬────────────────────────────────────┘
                   │                │
                   ▼                ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│ Job 3: health-check     │   │ Job 4: api-smoke-test   │
│ Lakehouse Health Tests  │   │ REST API & E2E Tests    │
│ Forecasting QA Checks   │   │ Contract Verification   │
└──────────────────┬──────┘   └─────────────┬───────────┘
                   │                        │
                   └───────────┬────────────┘
                               │
                               ▼
┌────────────────────────────────────────────────────────────────────────┐
│ Job 5: build-report                                                    │
│ Consolidate results  •  Publish Markdown Step Summary to GitHub PR/Run │
└────────────────────────────────────────────────────────────────────────┘
```

### Pipeline Jobs Breakdown
1. **`code-quality`**:
   - Runs `ruff check src/ tests/` for linting.
   - Runs `isort --check-only` for import order consistency.
   - Runs `black --check` for PEP 8 formatting.
2. **`test-suite`**:
   - Runs across Python 3.11 and 3.12 matrix on `ubuntu-latest`.
   - Rebuilds warehouse tables in DuckDB.
   - Runs all 107 test cases with `--cov-fail-under=55`.
   - Uploads coverage artifacts and Codecov integration.
3. **`health-check`**:
   - Verifies table integrity, model artifact freshness, and forecasting schema quality.
4. **`api-smoke-test`**:
   - Exercises FastAPI REST endpoints and verifies lakehouse-to-API ground truth consistency.
5. **`build-report`**:
   - Consolidates execution metrics into a GitHub Actions Step Summary table.

---

## 6. Operational Runbook

### 6.1 Running Tests Locally
```bash
# Run complete test suite (all 107 tests)
.venv\Scripts\pytest.exe tests/ -v --tb=short

# Run specific functional suite
.venv\Scripts\pytest.exe tests/unit/test_monitoring.py -v
.venv\Scripts\pytest.exe tests/unit/test_forecasting_quality.py -v
.venv\Scripts\pytest.exe tests/end_to_end/test_pipeline_e2e.py -v
.venv\Scripts\pytest.exe tests/api/test_api_endpoints.py -v
```

### 6.2 Generating Coverage Reports Locally
```bash
# Generate terminal summary, HTML report, and XML file
.venv\Scripts\pytest.exe tests/ \
  --cov=src/logitrack \
  --cov-report=term-missing \
  --cov-report=html:htmlcov \
  --cov-report=xml:coverage.xml \
  -q

# View HTML report (opens in default browser)
start htmlcov/index.html
```

### 6.3 Executing Health Monitoring Programmatically
```python
from logitrack.monitoring.health_monitor import run_full_health_check
from logitrack.monitoring.model_monitor import run_model_drift_report

# Run composite lakehouse health check
health = run_full_health_check()
print(f"Overall Status: {health['overall_status']}")
print(f"Summary: {health['summary']}")

# Run ML model drift evaluation
drift = run_model_drift_report()
print(f"Delay Model Drift: {drift['delay_classifier']['drift_detected']}")
print(f"ETA Model Drift: {drift['eta_regressor']['drift_detected']}")
```

---

## 7. Compliance & Standards Verification

- **Data Provenance**: Every monitored table and forecast preserves explicit `is_synthetic_simulated` labeling.
- **SLA Calculation Consistency**: All OTD and delay calculations strictly adhere to the `Delivered Orders` (27,727) denominator standard.
- **Lakehouse Concurrency**: Health monitors and tests utilize `read_only=True` for DuckDB access, preventing lock contention.
- **CI/CD Reliability**: Complete isolation and automated database seeding in CI guarantees deterministic test execution on clean runners.
