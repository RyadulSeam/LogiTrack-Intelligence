"""
Delivery ETA Regressor
LogiTrack Intelligence — Phase 8

Predicts expected delivery duration (in hours) based on hub processing time,
driver attributes, vehicle type, and temporal parameters.
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
    mean_absolute_error,
    root_mean_squared_error,
    r2_score,
    median_absolute_error
)
import xgboost as xgb


class ETARegressor:
    """Production-grade XGBoost Regressor for Delivery Duration (ETA in hours)."""

    NUMERIC_FEATURES = [
        "hub_capacity",
        "driver_experience",
        "driver_rating",
        "hub_processing_time_hours"
    ]

    CATEGORICAL_FEATURES = [
        "day_of_week",
        "month_number",
        "hub_name",
        "vehicle_type"
    ]

    def __init__(
        self,
        n_estimators: int = 120,
        max_depth: int = 6,
        learning_rate: float = 0.08,
        subsample: float = 0.85,
        random_state: int = 42,
        **kwargs
    ):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "subsample": subsample,
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

        regressor = xgb.XGBRegressor(**self.params)

        return Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor)
        ])

    def train(self, df: pd.DataFrame, test_size: float = 0.2) -> Tuple[Dict[str, float], Pipeline]:
        """
        Trains model using a time-aware split (past 80% train, recent 20% test).
        """
        logger.info(f"Training ETARegressor on {len(df):,} records with time-aware split ({1-test_size:.0%}/{test_size:.0%})...")

        split_idx = int(len(df) * (1 - test_size))
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

        X_train = train_df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y_train = train_df["delivery_time_hours"].astype(float)

        X_test = test_df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        y_test = test_df["delivery_time_hours"].astype(float)

        self.pipeline = self._build_pipeline()
        self.pipeline.fit(X_train, y_train)

        # Evaluate on out-of-time test set
        y_pred = self.pipeline.predict(X_test)

        metrics = {
            "mae": float(mean_absolute_error(y_test, y_pred)),
            "rmse": float(root_mean_squared_error(y_test, y_pred)),
            "r2": float(r2_score(y_test, y_pred)),
            "median_ae": float(median_absolute_error(y_test, y_pred))
        }

        logger.info(
            f"ETARegressor Evaluation -> "
            f"MAE: {metrics['mae']:.2f} hrs | RMSE: {metrics['rmse']:.2f} hrs | "
            f"R2: {metrics['r2']:.4f} | MedAE: {metrics['median_ae']:.2f} hrs"
        )
        return metrics, self.pipeline

    def predict(self, df: pd.DataFrame) -> np.ndarray:
        if self.pipeline is None:
            raise ValueError("Model pipeline is not fitted or loaded.")
        X = df[self.NUMERIC_FEATURES + self.CATEGORICAL_FEATURES]
        return self.pipeline.predict(X)

    def save(self, filepath: str = "models/artifacts/eta_regressor.joblib") -> str:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        joblib.dump({"pipeline": self.pipeline, "params": self.params, "version": self.model_version}, filepath)
        logger.info(f"Saved ETARegressor artifact to {filepath}")
        return filepath

    @classmethod
    def load(cls, filepath: str = "models/artifacts/eta_regressor.joblib") -> "ETARegressor":
        payload = joblib.load(filepath)
        instance = cls(**payload.get("params", {}))
        instance.pipeline = payload["pipeline"]
        instance.model_version = payload.get("version", "1.0.0")
        logger.info(f"Loaded ETARegressor from {filepath}")
        return instance
