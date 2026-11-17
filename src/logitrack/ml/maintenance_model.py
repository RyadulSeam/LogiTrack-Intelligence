"""
Fleet Predictive Maintenance Classifier
LogiTrack Intelligence — Phase 8

Predicts vehicle breakdown risk and scheduled maintenance urgency based on
historical breakdowns, fleet age, downtime, and cumulative maintenance expense.
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
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split


class FleetMaintenanceClassifier:
    """Predictive Classifier for Fleet Vehicle Breakdown & Maintenance Urgency."""

    NUMERIC_FEATURES = [
        "lifetime_breakdowns",
        "fleet_age_days",
        "total_maint_events",
        "avg_downtime_hours",
        "total_maint_cost"
    ]

    CATEGORICAL_FEATURES = [
        "vehicle_type"
    ]

    def __init__(
        self,
        n_estimators: int = 80,
        max_depth: int = 3,
        learning_rate: float = 0.1,
        random_state: int = 42,
        **kwargs
    ):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
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

        classifier = GradientBoostingClassifier(**self.params)

        return Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier)
        ])

    def train(self, df: pd.DataFrame, test_size: float = 0.25) -> Tuple[Dict[str, float], Pipeline]:
        """
        Trains model using stratified sampling for fleet vehicle records.
        """
        logger.info(f"Training FleetMaintenanceClassifier on {len(df):,} fleet records...")

        X = df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y = df["maintenance_target"].astype(int)

        # Stratified train/test split
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=self.params["random_state"], stratify=y
        )

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
            f"FleetMaintenanceClassifier Evaluation -> "
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

    def save(self, filepath: str = "models/artifacts/maintenance_classifier.joblib") -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "params": self.params, "version": self.model_version}, filepath)
        logger.info(f"Saved FleetMaintenanceClassifier artifact to {filepath}")
        return filepath

    @classmethod
    def load(cls, filepath: str = "models/artifacts/maintenance_classifier.joblib") -> "FleetMaintenanceClassifier":
        payload = joblib.load(filepath)
        instance = cls(**payload.get("params", {}))
        instance.pipeline = payload["pipeline"]
        instance.model_version = payload.get("version", "1.0.0")
        logger.info(f"Loaded FleetMaintenanceClassifier from {filepath}")
        return instance
