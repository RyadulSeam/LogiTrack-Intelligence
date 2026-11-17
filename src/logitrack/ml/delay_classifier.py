"""
Order Delay Risk Classifier
LogiTrack Intelligence — Phase 8

Predicts whether an order will experience a delivery delay based on
hub processing time, driver profile, vehicle telemetry, and temporal factors.
"""

from typing import Dict, Any, Tuple, Optional
import os
import joblib
import pandas as pd
import numpy as np
from loguru import logger
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    classification_report
)
import xgboost as xgb


class DelayRiskClassifier:
    """Production-grade XGBoost Classifier for Delivery Delay Risk."""

    NUMERIC_FEATURES = [
        "hub_capacity",
        "driver_experience",
        "driver_rating",
        "lifetime_breakdowns",
        "hub_processing_time_hours"
    ]

    CATEGORICAL_FEATURES = [
        "day_of_week",
        "month_number",
        "hub_name",
        "employment_type",
        "vehicle_type"
    ]

    def __init__(
        self,
        n_estimators: int = 120,
        max_depth: int = 5,
        learning_rate: float = 0.08,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        scale_pos_weight: Optional[float] = None,
        random_state: int = 42,
        eval_metric: str = "logloss",
        **kwargs
    ):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "subsample": subsample,
            "colsample_bytree": colsample_bytree,
            "random_state": random_state,
            "eval_metric": eval_metric
        }
        if scale_pos_weight is not None:
            self.params["scale_pos_weight"] = scale_pos_weight
        self.pipeline: Optional[Pipeline] = None
        self.model_version = "1.0.0"

    def _build_pipeline(self, scale_pos_weight: Optional[float] = None) -> Pipeline:
        numeric_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler())
        ])

        categorical_transformer = Pipeline(steps=[
            ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
            ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
        ])

        preprocessor = ColumnTransformer(transformers=[
            ("num", numeric_transformer, self.NUMERIC_FEATURES),
            ("cat", categorical_transformer, self.CATEGORICAL_FEATURES)
        ])

        params = dict(self.params)
        if scale_pos_weight is not None:
            params["scale_pos_weight"] = scale_pos_weight

        classifier = xgb.XGBClassifier(**params)

        return Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ])

    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Tuple[Dict[str, float], Pipeline]:
        """
        Trains model using a time-aware split (past 80% train, recent 20% test).
        """
        logger.info(f"Training DelayRiskClassifier on {len(df):,} records with time-aware split ({1-test_size:.0%}/{test_size:.0%})...")
        
        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

        X_train = train_df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y_train = train_df["is_delayed"].astype(int)

        X_test = test_df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y_test = test_df["is_delayed"].astype(int)

        # Dynamic class imbalance balancing
        neg_count = (y_train == 0).sum()
        pos_count = (y_train == 1).sum()
        scale_pos = float(neg_count / max(pos_count, 1))

        self.pipeline = self._build_pipeline(scale_pos_weight=scale_pos)
        self.pipeline.fit(X_train, y_train)

        # Evaluate on out-of-time test set
        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, y_proba))
        }

        logger.info(
            f"DelayRiskClassifier Evaluation -> "
            f"ROC-AUC: {metrics['roc_auc']:.4f} | F1: {metrics['f1_score']:.4f} | "
            f"Precision: {metrics['precision']:.4f} | Recall: {metrics['recall']:.4f}"
        )
        return metrics, self.pipeline

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self.pipeline is None:
            raise ValueError("Model pipeline is not fitted or loaded.")
        X = df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        return self.pipeline.predict(X)

    def predict_proba(self, df: pd.DataFrame) -> np.ndarray:
        if self.pipeline is None:
            raise ValueError("Model pipeline is not fitted or loaded.")
        X = df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        return self.pipeline.predict_proba(X)[:, 1]

    def save(self, filepath: str = "models/artifacts/delay_risk_classifier.joblib") -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "params": self.params, "version": self.model_version}, filepath)
        logger.info(f"Saved DelayRiskClassifier artifact to {filepath}")
        return filepath

    @classmethod
    def load(cls, filepath: str = "models/artifacts/delay_risk_classifier.joblib") -> "DelayRiskClassifier":
        payload = joblib.load(filepath)
        instance = cls(**payload.get("params", {}))
        instance.pipeline = payload["pipeline"]
        instance.model_version = payload.get("version", "1.0.0")
        logger.info(f"Loaded DelayRiskClassifier from {filepath}")
        return instance
