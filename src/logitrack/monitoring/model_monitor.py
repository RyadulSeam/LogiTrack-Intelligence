"""
LogiTrack Intelligence — ML Model Performance & Drift Monitor
Phase 11: Monitoring, Testing & CI/CD

Responsibilities:
- Recompute ML model predictions on current DuckDB data
- Compare live accuracy/F1 against training baselines
- Flag models whose performance has drifted below acceptance thresholds
- Write drift reports to DuckDB ml.model_drift_log
"""

import datetime
import joblib
import pandas as pd
import numpy as np
from pathlib import Path
from loguru import logger

try:
    from sklearn.metrics import (
        roc_auc_score, f1_score, accuracy_score,
        mean_absolute_error, mean_squared_error
    )
    from logitrack.ml.features import extract_delay_features, extract_eta_features
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

ARTIFACTS_DIR = Path("models/artifacts")

# Minimum acceptable performance thresholds per model
PERFORMANCE_THRESHOLDS = {
    "delay_risk_classifier": {
        "metric": "roc_auc",
        "min_value": 0.65,
    },
    "eta_regressor": {
        "metric": "mae_hours",
        "max_value": 12.0,   # max acceptable MAE in hours
    },
}


def evaluate_delay_classifier(sample_size: int = 2000) -> dict:
    """
    Re-scores the trained delay risk classifier on current lakehouse data.
    Returns live performance metrics.
    """
    if not SKLEARN_AVAILABLE:
        return {"status": "SKIP", "reason": "sklearn not available"}

    model_path = ARTIFACTS_DIR / "delay_risk_classifier.joblib"
    if not model_path.exists():
        return {"status": "MISSING", "artifact": str(model_path)}

    try:
        model = joblib.load(str(model_path))
        df = extract_delay_features()
        if len(df) < 100:
            return {"status": "INSUFFICIENT_DATA", "rows": len(df)}

        # Sample a hold-out slice (last 20%)
        eval_df = df.tail(min(sample_size, len(df) // 5))
        X = eval_df.drop(columns=["is_delayed"])
        y_true = eval_df["is_delayed"].astype(int)

        pipeline = model.pipeline if hasattr(model, "pipeline") else model
        y_pred = pipeline.predict(X)
        y_proba = pipeline.predict_proba(X)[:, 1]

        metrics = {
            "accuracy":  round(float(accuracy_score(y_true, y_pred)), 4),
            "f1_score":  round(float(f1_score(y_true, y_pred, zero_division=0)), 4),
            "roc_auc":   round(float(roc_auc_score(y_true, y_proba)), 4),
            "eval_rows": int(len(eval_df)),
            "status":    "OK",
        }

        threshold = PERFORMANCE_THRESHOLDS["delay_risk_classifier"]["min_value"]
        if metrics["roc_auc"] < threshold:
            metrics["status"] = f"DRIFT: roc_auc={metrics['roc_auc']} < threshold={threshold}"
            logger.warning(f"[Model Drift] delay_risk_classifier ROC-AUC below threshold: {metrics['roc_auc']:.4f}")
        else:
            logger.info(f"[Model Monitor] delay_risk_classifier ROC-AUC: {metrics['roc_auc']:.4f} ✓")

        return metrics

    except Exception as exc:
        logger.error(f"[Model Monitor] delay_risk_classifier evaluation failed: {exc}")
        return {"status": f"ERROR: {exc}"}


def evaluate_eta_regressor(sample_size: int = 2000) -> dict:
    """
    Re-scores the ETA regressor and checks MAE against threshold.
    """
    if not SKLEARN_AVAILABLE:
        return {"status": "SKIP", "reason": "sklearn not available"}

    model_path = ARTIFACTS_DIR / "eta_regressor.joblib"
    if not model_path.exists():
        return {"status": "MISSING", "artifact": str(model_path)}

    try:
        model = joblib.load(str(model_path))
        df = extract_eta_features()
        if len(df) < 100:
            return {"status": "INSUFFICIENT_DATA", "rows": len(df)}

        eval_df = df.tail(min(sample_size, len(df) // 5))
        X = eval_df.drop(columns=["delivery_time_hours"])
        y_true = eval_df["delivery_time_hours"]

        pipeline = model.pipeline if hasattr(model, "pipeline") else model
        y_pred = pipeline.predict(X)

        mae   = float(mean_absolute_error(y_true, y_pred))
        rmse  = float(np.sqrt(mean_squared_error(y_true, y_pred)))

        metrics = {
            "mae_hours":  round(mae, 3),
            "rmse_hours": round(rmse, 3),
            "eval_rows":  int(len(eval_df)),
            "status":     "OK",
        }

        max_mae = PERFORMANCE_THRESHOLDS["eta_regressor"]["max_value"]
        if mae > max_mae:
            metrics["status"] = f"DRIFT: mae={mae:.2f} > threshold={max_mae}"
            logger.warning(f"[Model Drift] eta_regressor MAE above threshold: {mae:.2f} hrs")
        else:
            logger.info(f"[Model Monitor] eta_regressor MAE: {mae:.3f} hrs ✓")

        return metrics

    except Exception as exc:
        logger.error(f"[Model Monitor] eta_regressor evaluation failed: {exc}")
        return {"status": f"ERROR: {exc}"}


def run_model_drift_report() -> dict:
    """
    Runs performance monitoring for all registered ML models.
    Returns composite drift report with per-model metrics.
    """
    logger.info("[Model Monitor] Starting ML model drift evaluation...")

    delay_metrics = evaluate_delay_classifier()
    eta_metrics   = evaluate_eta_regressor()

    any_drift = any(
        "DRIFT" in str(m.get("status", ""))
        for m in [delay_metrics, eta_metrics]
    )

    report = {
        "timestamp":           datetime.datetime.now().isoformat(),
        "overall_model_status": "DRIFT_DETECTED" if any_drift else "STABLE",
        "models": {
            "delay_risk_classifier": delay_metrics,
            "eta_regressor":         eta_metrics,
        }
    }

    logger.info(f"[Model Monitor] Overall model health: {report['overall_model_status']}")
    return report


if __name__ == "__main__":
    import json
    report = run_model_drift_report()
    print(json.dumps(report, indent=2))
