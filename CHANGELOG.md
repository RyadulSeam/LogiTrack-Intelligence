# Changelog

All notable changes to LogiTrack Intelligence will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.8.0] - 2026-11-17

### Added
- **Phase 8: Machine Learning Engineering**:
  - `src/logitrack/ml/features.py`: Time-ordered feature extraction pipelines from Gold tables (`fact_orders`, `fact_hub_hourly`, `dim_vehicle`).
  - `src/logitrack/ml/delay_classifier.py`: XGBoost binary classifier predicting delivery delay risk with dynamic class imbalance weighting.
  - `src/logitrack/ml/eta_regressor.py`: XGBoost regressor predicting transit duration in hours (`delivery_time_hours`).
  - `src/logitrack/ml/hub_congestion.py`: Random Forest classifier forecasting hub congestion and backlog formation.
  - `src/logitrack/ml/maintenance_model.py`: Gradient Boosting classifier evaluating fleet vehicle breakdown risk.
  - `src/logitrack/ml/train_all.py`: Orchestration script saving artifacts to `models/artifacts/` and syncing metadata to DuckDB `ml.model_registry`, `ml.model_evaluations`, and `ml.predictions`.
  - `docs/13_ml_model_cards.md`: Comprehensive model documentation, evaluation metrics, feature schemas, and retraining policies.
  - `tests/unit/test_ml_models.py`: 6 automated unit & integration tests validating feature extraction, model lifecycle, artifact persistence, and registry sync.

## [0.7.0] - 2026-11-17

### Added
- **Phase 7: Business Intelligence & Dashboards**:
  - Streamlit multi-tab operations control tower (`dashboards/streamlit/app.py`).
  - Metrics calculation engine (`src/logitrack/analytics/metrics.py`).
  - Power BI semantic layer views and DAX measures.
  - `docs/12_business_metrics.md`.

## [0.1.0] - 2026-11-13

### Added
- Initial project foundation and repository structure.
- Source datasets: `Hubs.csv`, `Drivers.csv`, `Vehicles.csv`, `Orders.csv`.
- Project configuration: `pyproject.toml`, `.env.example`, `.gitignore`.
- MIT License.
