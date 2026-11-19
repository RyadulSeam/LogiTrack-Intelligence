"""
Regional Order Demand Forecaster
LogiTrack Intelligence — Phase 9: Forecasting Engineering

Implements multi-horizon (7-day and 30-day) hub demand forecasting with:
- Point Forecast (Mean/Median)
- 95% Confidence Intervals (Quantile Regression at 0.025 and 0.975)
- Non-leaking chronological backtesting
"""

from typing import Dict, Any, Tuple, Optional
import os
import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from loguru import logger


FEATURE_COLUMNS = [
    "day_of_week", "day_of_month", "month", "quarter", "is_weekend", "day_of_year",
    "sin_dow", "cos_dow", "sin_month", "cos_month",
    "lag_1", "lag_2", "lag_3", "lag_7", "lag_14", "lag_21", "lag_28",
    "rolling_mean_7", "rolling_std_7", "rolling_min_7", "rolling_max_7",
    "rolling_mean_14", "rolling_mean_28", "rolling_std_28", "expanding_mean"
]


class RegionalDemandForecaster:
    """
    Forecaster for Texas Regional Hub Order Demand.
    Trains point forecaster + quantile lower/upper interval estimators.
    """

    def __init__(self, n_estimators: int = 150, max_depth: int = 4, learning_rate: int = 0.05):
        self.params = {
            "n_estimators": n_estimators,
            "max_depth": max_depth,
            "learning_rate": learning_rate,
            "random_state": 42
        }
        self.point_model = GradientBoostingRegressor(loss="squared_error", **self.params)
        self.lower_model = GradientBoostingRegressor(loss="quantile", alpha=0.025, **self.params)
        self.upper_model = GradientBoostingRegressor(loss="quantile", alpha=0.975, **self.params)
        self.feature_names = FEATURE_COLUMNS
        self.is_fitted = False

    def train(self, train_df: pd.DataFrame, target_col: str = "order_volume") -> Dict[str, float]:
        """
        Fits point, lower bound (2.5%), and upper bound (97.5%) models.
        """
        logger.info(f"Training RegionalDemandForecaster on {len(train_df)} historical records")
        X_train = train_df[self.feature_names]
        y_train = train_df[target_col]

        self.point_model.fit(X_train, y_train)
        self.lower_model.fit(X_train, y_train)
        self.upper_model.fit(X_train, y_train)
        self.is_fitted = True

        y_pred = self.point_model.predict(X_train)
        metrics = {
            "train_mae": float(mean_absolute_error(y_train, y_pred)),
            "train_rmse": float(np.sqrt(mean_squared_error(y_train, y_pred))),
            "train_r2": float(r2_score(y_train, y_pred)),
            "train_mape": float(np.mean(np.abs((y_train - y_pred) / np.maximum(y_train, 1))) * 100.0)
        }
        logger.info(f"Training Metrics: MAE={metrics['train_mae']:.2f}, R2={metrics['train_r2']:.4f}")
        return metrics

    def evaluate(self, test_df: pd.DataFrame, target_col: str = "order_volume") -> Tuple[Dict[str, float], pd.DataFrame]:
        """
        Evaluates out-of-time chronological performance and interval coverage.
        """
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted yet.")

        X_test = test_df[self.feature_names]
        y_true = test_df[target_col]

        y_point = np.maximum(self.point_model.predict(X_test), 0)
        y_lower = np.maximum(self.lower_model.predict(X_test), 0)
        y_upper = np.maximum(self.upper_model.predict(X_test), y_point)

        mae = mean_absolute_error(y_true, y_point)
        rmse = np.sqrt(mean_squared_error(y_true, y_point))
        r2 = r2_score(y_true, y_point)
        mape = np.mean(np.abs((y_true - y_point) / np.maximum(y_true, 1))) * 100.0
        
        # Empirical 95% Confidence Interval Coverage
        coverage = np.mean((y_true >= y_lower) & (y_true <= y_upper)) * 100.0

        metrics = {
            "test_mae": float(mae),
            "test_rmse": float(rmse),
            "test_r2": float(r2),
            "test_mape": float(mape),
            "interval_coverage_95_pct": float(coverage)
        }

        eval_df = test_df[["ds", "hub_id", "hub_name", target_col]].copy()
        eval_df["predicted_demand"] = np.round(y_point, 1)
        eval_df["lower_bound_95"] = np.round(y_lower, 1)
        eval_df["upper_bound_95"] = np.round(y_upper, 1)

        logger.info(
            f"Evaluation Test Metrics: MAE={mae:.2f}, RMSE={rmse:.2f}, R2={r2:.4f}, "
            f"MAPE={mape:.2f}%, 95% Interval Coverage={coverage:.2f}%"
        )
        return metrics, eval_df

    def forecast_future(self, history_df: pd.DataFrame, horizon_days: int = 30) -> pd.DataFrame:
        """
        Generates recursive out-of-sample forecast for `horizon_days` ahead per hub.
        """
        if not self.is_fitted:
            raise RuntimeError("Model is not fitted yet.")

        future_records = []
        last_date = history_df["ds"].max()

        for hub_id, hub_group in history_df.groupby("hub_id"):
            hub_name = hub_group["hub_name"].iloc[0]
            daily_cap = hub_group["daily_capacity"].iloc[0]
            recent_series = hub_group.sort_values("ds")["order_volume"].tolist()
            
            cur_date = last_date
            for step in range(1, horizon_days + 1):
                cur_date = cur_date + pd.Timedelta(days=1)
                
                # Dynamic feature extraction from current state
                dow = cur_date.dayofweek
                dom = cur_date.day
                month = cur_date.month
                quarter = cur_date.quarter
                is_weekend = 1 if dow >= 5 else 0
                doy = cur_date.dayofyear
                
                feat = {
                    "day_of_week": dow,
                    "day_of_month": dom,
                    "month": month,
                    "quarter": quarter,
                    "is_weekend": is_weekend,
                    "day_of_year": doy,
                    "sin_dow": np.sin(2 * np.pi * dow / 7.0),
                    "cos_dow": np.cos(2 * np.pi * dow / 7.0),
                    "sin_month": np.sin(2 * np.pi * month / 12.0),
                    "cos_month": np.cos(2 * np.pi * month / 12.0),
                    "lag_1": recent_series[-1],
                    "lag_2": recent_series[-2] if len(recent_series) >= 2 else recent_series[-1],
                    "lag_3": recent_series[-3] if len(recent_series) >= 3 else recent_series[-1],
                    "lag_7": recent_series[-7] if len(recent_series) >= 7 else recent_series[-1],
                    "lag_14": recent_series[-14] if len(recent_series) >= 14 else recent_series[-1],
                    "lag_21": recent_series[-21] if len(recent_series) >= 21 else recent_series[-1],
                    "lag_28": recent_series[-28] if len(recent_series) >= 28 else recent_series[-1],
                    "rolling_mean_7": np.mean(recent_series[-7:]),
                    "rolling_std_7": np.std(recent_series[-7:]),
                    "rolling_min_7": np.min(recent_series[-7:]),
                    "rolling_max_7": np.max(recent_series[-7:]),
                    "rolling_mean_14": np.mean(recent_series[-14:]),
                    "rolling_mean_28": np.mean(recent_series[-28:]),
                    "rolling_std_28": np.std(recent_series[-28:]),
                    "expanding_mean": np.mean(recent_series)
                }
                
                feat_df = pd.DataFrame([feat])[self.feature_names]
                point_pred = max(0.0, float(self.point_model.predict(feat_df)[0]))
                lower_pred = max(0.0, float(self.lower_model.predict(feat_df)[0]))
                upper_pred = max(point_pred, float(self.upper_model.predict(feat_df)[0]))
                
                # Append predicted value into running series for next step autoregression
                recent_series.append(point_pred)
                
                future_records.append({
                    "forecast_date": cur_date.strftime("%Y-%m-%d"),
                    "horizon_step": step,
                    "hub_id": hub_id,
                    "hub_name": hub_name,
                    "daily_capacity": daily_cap,
                    "forecast_order_volume": round(point_pred, 1),
                    "lower_bound_95": round(lower_pred, 1),
                    "upper_bound_95": round(upper_pred, 1),
                    "is_synthetic_simulated": True
                })

        return pd.DataFrame(future_records)

    def save(self, artifact_path: str = "models/artifacts/demand_forecaster.joblib") -> str:
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        bundle = {
            "point_model": self.point_model,
            "lower_model": self.lower_model,
            "upper_model": self.upper_model,
            "params": self.params,
            "feature_names": self.feature_names
        }
        joblib.dump(bundle, artifact_path)
        logger.info(f"Saved RegionalDemandForecaster bundle to {artifact_path}")
        return artifact_path
