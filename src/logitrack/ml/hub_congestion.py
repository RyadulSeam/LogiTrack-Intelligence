"""
Hub Congestion Risk Classifier
LogiTrack Intelligence — Phase 8

Predicts whether a regional distribution hub will encounter operational congestion
based on hourly throughput, dispatch rate, backlog, and capacity utilization.
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
    roc_auc_score
)
from sklearn.ensemble import RandomForestClassifier


class HubCongestionClassifier:
    """Predictive Classifier for Hub Operational Bottlenecks and Congestion."""

    NUMERIC_FEATURES = [
        "hour_of_day",
        "daily_capacity",
        "orders_received",
        "orders_dispatched",
        "avg_processing_time_hours",
        "capacity_utilization_pct"
    ]

    CATEGORICAL_FEATURES = [
        "day_of_week",
        "hub_name"
    ]

    def __init__(
        self,
        n_estimators: int = 100,
        max_depth: int = 6,
        min_samples_split: int = 5,
        random_state: int = 42,
        **kwargs
    ):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "min_samples_split": min_samples_split,
            "random_state": random_state
        }
        self.pipeline: Optional[Pipeline] = None
        self.model_version = "1.0.0"

    def _build_pipeline(self) -> Pipeline:
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

        classifier = RandomForestClassifier(**self.params)

        return Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ])

    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Tuple[Dict[str, float], Pipeline]:
        """
        Trains model using a time-aware split on hourly observation sequence.
        """
        logger.info(f"Training HubCongestionClassifier on {len(df):,} hourly records...")

        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

        X_train = train_df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y_train = train_df["is_congested"].astype(int)

        X_test = test_df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y_test = test_df["is_congested"].astype(int)

        self.pipeline = self._build_pipeline()
        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)[:, 1]

        metrics = {
            "accuracy": float(accuracy_score(y_test, y_pred)),
            "precision": float(precision_score(y_test, y_pred, zero_division=0)),
            "recall": float(recall_score(y_test, y_pred, zero_division=0)),
            "f1_score": float(f1_score(y_test, y_pred, zero_division=0)),
            "roc_auc": float(roc_auc_score(y_test, y_proba)) if len(np.unique(y_test)) > 1 else 1.0
        }

        logger.info(
            f"HubCongestionClassifier Evaluation -> "
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

    def save(self, filepath: str = "models/artifacts/hub_congestion_model.joblib") -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "params": self.params, "version": self.model_version}, filepath)
        logger.info(f"Saved HubCongestionClassifier artifact to {filepath}")
        return filepath

    @classmethod
    def load(cls, filepath: str = "models/artifacts/hub_congestion_model.joblib") -> "HubCongestionClassifier":
        payload = joblib.load(filepath)
        instance = cls(**payload.get("params", {}))
        instance.pipeline = payload["pipeline"]
        instance.model_version = payload.get("version", "1.0.0")
        logger.info(f"Loaded HubCongestionClassifier from {filepath}")
        return instance
