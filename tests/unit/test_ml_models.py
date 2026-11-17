"""
Unit & Integration Tests for Phase 8 ML Models & Registry
LogiTrack Intelligence — Phase 8
"""

import os
import pytest
import pandas as pd
import numpy as np

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
from logitrack.storage.duckdb_manager import DuckDBManager


def test_feature_extraction_integrity():
    """Verify all 4 feature extractors yield valid datasets without target nulls."""
    delay_df = extract_delay_features()
    assert len(delay_df) > 1000
    assert "is_delayed" in delay_df.columns
    assert delay_df["is_delayed"].isna().sum() == 0

    eta_df = extract_eta_features()
    assert len(eta_df) > 1000
    assert "delivery_time_hours" in eta_df.columns
    assert eta_df["delivery_time_hours"].isna().sum() == 0

    hub_df = extract_hub_congestion_features()
    assert len(hub_df) > 500
    assert "is_congested" in hub_df.columns
    assert hub_df["is_congested"].isna().sum() == 0

    fleet_df = extract_maintenance_features()
    assert len(fleet_df) >= 40
    assert "maintenance_target" in fleet_df.columns
    assert fleet_df["maintenance_target"].isna().sum() == 0


def test_delay_risk_classifier_lifecycle(tmp_path):
    """Verify training, prediction, scoring range, and artifact persistence."""
    df = extract_delay_features().head(1000)
    model = DelayRiskClassifier(n_estimators=30, max_depth=3)
    metrics, pipeline = model.train(df, test_size=0.2)

    assert "roc_auc" in metrics
    assert "f1_score" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0

    preds = model.predict(df.tail(20))
    probs = model.predict_proba(df.tail(20))

    assert len(preds) == 20
    assert set(preds).issubset({0, 1})
    assert len(probs) == 20
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    # Save and reload
    save_path = str(tmp_path / "test_delay.joblib")
    model.save(save_path)
    assert os.path.exists(save_path)

    loaded = DelayRiskClassifier.load(save_path)
    loaded_preds = loaded.predict(df.tail(20))
    np.testing.assert_array_equal(preds, loaded_preds)


def test_eta_regressor_lifecycle(tmp_path):
    """Verify regression training, prediction, and positive duration bounds."""
    df = extract_eta_features().head(1000)
    model = ETARegressor(n_estimators=30, max_depth=4)
    metrics, pipeline = model.train(df, test_size=0.2)

    assert "mae" in metrics
    assert "rmse" in metrics
    assert metrics["mae"] > 0.0

    preds = model.predict(df.tail(20))
    assert len(preds) == 20
    assert (preds > 0.0).all()

    save_path = str(tmp_path / "test_eta.joblib")
    model.save(save_path)
    loaded = ETARegressor.load(save_path)
    loaded_preds = loaded.predict(df.tail(20))
    np.testing.assert_allclose(preds, loaded_preds, rtol=1e-5)


def test_hub_congestion_classifier_lifecycle(tmp_path):
    """Verify hub congestion classification and probabilities."""
    df = extract_hub_congestion_features().head(500)
    model = HubCongestionClassifier(n_estimators=25, max_depth=3)
    metrics, _ = model.train(df, test_size=0.2)

    assert "roc_auc" in metrics
    assert 0.0 <= metrics["accuracy"] <= 1.0

    preds = model.predict(df.tail(15))
    probs = model.predict_proba(df.tail(15))
    assert len(preds) == 15
    assert (probs >= 0.0).all() and (probs <= 1.0).all()

    save_path = str(tmp_path / "test_hub.joblib")
    model.save(save_path)
    loaded = HubCongestionClassifier.load(save_path)
    np.testing.assert_array_equal(preds, loaded.predict(df.tail(15)))


def test_fleet_maintenance_classifier_lifecycle(tmp_path):
    """Verify fleet maintenance classification."""
    df = extract_maintenance_features()
    model = FleetMaintenanceClassifier(n_estimators=20, max_depth=2)
    metrics, _ = model.train(df, test_size=0.25)

    assert "f1_score" in metrics
    preds = model.predict(df.head(10))
    assert len(preds) == 10
    assert set(preds).issubset({0, 1})

    save_path = str(tmp_path / "test_maint.joblib")
    model.save(save_path)
    loaded = FleetMaintenanceClassifier.load(save_path)
    np.testing.assert_array_equal(preds, loaded.predict(df.head(10)))


def test_duckdb_ml_registry_populated():
    """Verify DuckDB ml schema contains all 4 registered models and evaluations."""
    manager = DuckDBManager()
    models = manager.query("SELECT model_name, is_active FROM ml.model_registry;")
    assert len(models) >= 4
    registered_names = set(models["model_name"])
    assert "delay_risk_classifier" in registered_names
    assert "eta_regressor" in registered_names
    assert "hub_congestion_classifier" in registered_names
    assert "fleet_maintenance_classifier" in registered_names

    evals = manager.query("SELECT COUNT(*) AS total_evals FROM ml.model_evaluations;")
    assert int(evals["total_evals"].iloc[0]) >= 16

    preds = manager.query("SELECT COUNT(*) AS total_preds FROM ml.predictions;")
    assert int(preds["total_preds"].iloc[0]) >= 10
    manager.close()
