"""
ML Training & Registry Orchestration Pipeline
LogiTrack Intelligence — Phase 8

Trains all 4 machine learning models, evaluates their performance metrics,
persists artifacts to disk, and registers models & metrics into DuckDB ml schema.
"""

from typing import Dict, Any, List
import os
import json
import uuid
from datetime import datetime
import pandas as pd
from loguru import logger

from logitrack.storage.duckdb_manager import DuckDBManager
from logitrack.ml.features import (
    extract_delay_features,
    extract_eta_features,
    extract_hub_congestion_features,
    extract_maintenance_features
)
from logitrack.ml.delay_classifier import DelayRiskClassifier
from logitrack.ml.eta_regressor import ETARegressor
from logitrack.ml.hub_congestion import HubCongestionClassifier
from logitrack.ml.maintenance_model import FleetMaintenanceClassifier


def run_training_pipeline(db_path: str = "data/lake/logitrack.duckdb") -> Dict[str, Any]:
    """
    Executes end-to-end training, serialization, and registry logging.
    """
    logger.info("==================================================")
    logger.info("Starting Phase 8 ML Model Training & Registry Pipeline")
    logger.info("==================================================")

    manager = DuckDBManager(db_path=db_path)
    os.makedirs("models/artifacts", exist_ok=True)
    summary_results: Dict[str, Any] = {}

    # ----------------------------------------------------
    # Model 1: Order Delay Risk Classifier
    # ----------------------------------------------------
    logger.info("--- [1/4] Training Delay Risk Classifier ---")
    delay_df = extract_delay_features(db_path=db_path)
    delay_model = DelayRiskClassifier()
    delay_metrics, _ = delay_model.train(delay_df)
    delay_artifact = delay_model.save("models/artifacts/delay_risk_classifier.joblib")
    
    model1_id = f"mod-delay-{uuid.uuid4().hex[:8]}"
    manager.execute("""
        INSERT INTO ml.model_registry (
            model_id, model_name, version, algorithm, training_dataset_size, hyperparameters, artifact_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        model1_id,
        "delay_risk_classifier",
        "1.0.0",
        "XGBoostClassifier",
        len(delay_df),
        json.dumps(delay_model.params),
        delay_artifact,
        True
    ])

    for metric_name, metric_val in delay_metrics.items():
        manager.execute("""
            INSERT INTO ml.model_evaluations (evaluation_id, model_id, metric_name, metric_value)
            VALUES (?, ?, ?, ?);
        """, [f"eval-{uuid.uuid4().hex[:8]}", model1_id, metric_name.upper(), round(metric_val, 4)])

    # Sample batch inference for registry demonstration
    sample_delay_orders = delay_df.tail(10)
    delay_preds = delay_model.predict(sample_delay_orders)
    delay_probs = delay_model.predict_proba(sample_delay_orders)
    for idx, (_, row) in enumerate(sample_delay_orders.iterrows()):
        manager.execute("""
            INSERT INTO ml.predictions (prediction_id, model_id, entity_type, entity_id, predicted_label, predicted_score)
            VALUES (?, ?, ?, ?, ?, ?);
        """, [
            f"pred-{uuid.uuid4().hex[:8]}",
            model1_id,
            "order",
            str(row["order_id"]),
            "DELAY_RISK" if delay_preds[idx] == 1 else "ON_TIME",
            round(float(delay_probs[idx]), 4)
        ])

    summary_results["delay_classifier"] = delay_metrics

    # ----------------------------------------------------
    # Model 2: Delivery ETA Regressor
    # ----------------------------------------------------
    logger.info("--- [2/4] Training Delivery ETA Regressor ---")
    eta_df = extract_eta_features(db_path=db_path)
    eta_model = ETARegressor()
    eta_metrics, _ = eta_model.train(eta_df)
    eta_artifact = eta_model.save("models/artifacts/eta_regressor.joblib")

    model2_id = f"mod-eta-{uuid.uuid4().hex[:8]}"
    manager.execute("""
        INSERT INTO ml.model_registry (
            model_id, model_name, version, algorithm, training_dataset_size, hyperparameters, artifact_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        model2_id,
        "eta_regressor",
        "1.0.0",
        "XGBoostRegressor",
        len(eta_df),
        json.dumps(eta_model.params),
        eta_artifact,
        True
    ])

    for metric_name, metric_val in eta_metrics.items():
        manager.execute("""
            INSERT INTO ml.model_evaluations (evaluation_id, model_id, metric_name, metric_value)
            VALUES (?, ?, ?, ?);
        """, [f"eval-{uuid.uuid4().hex[:8]}", model2_id, metric_name.upper(), round(metric_val, 4)])

    summary_results["eta_regressor"] = eta_metrics

    # ----------------------------------------------------
    # Model 3: Regional Hub Congestion Classifier
    # ----------------------------------------------------
    logger.info("--- [3/4] Training Hub Congestion Classifier ---")
    hub_df = extract_hub_congestion_features(db_path=db_path)
    hub_model = HubCongestionClassifier()
    hub_metrics, _ = hub_model.train(hub_df)
    hub_artifact = hub_model.save("models/artifacts/hub_congestion_model.joblib")

    model3_id = f"mod-hub-{uuid.uuid4().hex[:8]}"
    manager.execute("""
        INSERT INTO ml.model_registry (
            model_id, model_name, version, algorithm, training_dataset_size, hyperparameters, artifact_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        model3_id,
        "hub_congestion_classifier",
        "1.0.0",
        "RandomForestClassifier",
        len(hub_df),
        json.dumps(hub_model.params),
        hub_artifact,
        True
    ])

    for metric_name, metric_val in hub_metrics.items():
        manager.execute("""
            INSERT INTO ml.model_evaluations (evaluation_id, model_id, metric_name, metric_value)
            VALUES (?, ?, ?, ?);
        """, [f"eval-{uuid.uuid4().hex[:8]}", model3_id, metric_name.upper(), round(metric_val, 4)])

    summary_results["hub_congestion"] = hub_metrics

    # ----------------------------------------------------
    # Model 4: Fleet Predictive Maintenance Classifier
    # ----------------------------------------------------
    logger.info("--- [4/4] Training Fleet Predictive Maintenance Classifier ---")
    fleet_df = extract_maintenance_features(db_path=db_path)
    fleet_model = FleetMaintenanceClassifier()
    fleet_metrics, _ = fleet_model.train(fleet_df)
    fleet_artifact = fleet_model.save("models/artifacts/maintenance_classifier.joblib")

    model4_id = f"mod-maint-{uuid.uuid4().hex[:8]}"
    manager.execute("""
        INSERT INTO ml.model_registry (
            model_id, model_name, version, algorithm, training_dataset_size, hyperparameters, artifact_path, is_active
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?);
    """, [
        model4_id,
        "fleet_maintenance_classifier",
        "1.0.0",
        "GradientBoostingClassifier",
        len(fleet_df),
        json.dumps(fleet_model.params),
        fleet_artifact,
        True
    ])

    for metric_name, metric_val in fleet_metrics.items():
        manager.execute("""
            INSERT INTO ml.model_evaluations (evaluation_id, model_id, metric_name, metric_value)
            VALUES (?, ?, ?, ?);
        """, [f"eval-{uuid.uuid4().hex[:8]}", model4_id, metric_name.upper(), round(metric_val, 4)])

    summary_results["fleet_maintenance"] = fleet_metrics

    manager.close()
    logger.info("==================================================")
    logger.info("Phase 8 Model Training Pipeline Completed Successfully!")
    logger.info("==================================================")
    return summary_results


if __name__ == "__main__":
    results = run_training_pipeline()
    print("\nTraining Results Summary:")
    print(json.dumps(results, indent=2))
