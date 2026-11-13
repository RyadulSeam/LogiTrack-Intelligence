-- ============================================================
-- Migration: 006_create_ml_tables.sql
-- Description: Machine Learning Registry, Evaluations, & Predictions
-- ============================================================

-- Model Registry
CREATE TABLE IF NOT EXISTS ml.model_registry (
    model_id VARCHAR(64) PRIMARY KEY,
    model_name VARCHAR(100) NOT NULL, -- delay_risk_classifier, eta_regressor, etc.
    version VARCHAR(20) NOT NULL,
    algorithm VARCHAR(100) NOT NULL, -- XGBoost, LightGBM, Random Forest
    training_dataset_size INTEGER,
    hyperparameters JSON,
    artifact_path VARCHAR(255),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Model Evaluations & Metrics
CREATE TABLE IF NOT EXISTS ml.model_evaluations (
    evaluation_id VARCHAR(64) PRIMARY KEY,
    model_id VARCHAR(64) REFERENCES ml.model_registry(model_id),
    metric_name VARCHAR(50) NOT NULL, -- ROC_AUC, F1, MAE, RMSE
    metric_value DECIMAL(10, 4) NOT NULL,
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Live Predictions Store
CREATE TABLE IF NOT EXISTS ml.predictions (
    prediction_id VARCHAR(64) PRIMARY KEY,
    model_id VARCHAR(64) REFERENCES ml.model_registry(model_id),
    entity_type VARCHAR(50) NOT NULL, -- order, vehicle, hub
    entity_id VARCHAR(64) NOT NULL,
    predicted_label VARCHAR(50),
    predicted_score DECIMAL(8, 4), -- e.g. 0.8421 delay probability
    prediction_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Feature Snapshots (Audit & Explainability Store)
CREATE TABLE IF NOT EXISTS ml.feature_snapshots (
    snapshot_id VARCHAR(64) PRIMARY KEY,
    entity_id VARCHAR(64) NOT NULL,
    features_json JSON NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
