"""
Hub Workload & Bottleneck Forecaster
LogiTrack Intelligence — Phase 9: Forecasting Engineering

Evaluates forecasted parcel flows against designed physical hub capacity,
projecting daily utilization rates, backlog risks, and throughput bottlenecks.
"""

from typing import Dict, Any, Tuple
import os
import joblib
import numpy as np
import pandas as pd
from loguru import logger


class HubWorkloadForecaster:
    """
    Forecaster for Hub Workload, Backlog Accumulation, and Bottleneck Risks.
    """

    def __init__(self, bottleneck_threshold_pct: float = 85.0):
        self.bottleneck_threshold_pct = bottleneck_threshold_pct
        self.is_fitted = False

    def forecast_workload(self, demand_forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms demand forecasts into workload and capacity bottleneck projections.
        """
        logger.info(f"Computing hub workload forecasts across {len(demand_forecast_df)} demand records")
        df = demand_forecast_df.copy()

        # Capacity utilization percentage
        df["capacity_utilization_pct"] = np.round(
            (df["forecast_order_volume"] / np.maximum(df["daily_capacity"], 1)) * 100.0, 2
        )

        # Bottleneck risk alert condition
        df["is_bottleneck_risk"] = df["capacity_utilization_pct"] >= self.bottleneck_threshold_pct
        df["risk_level"] = np.where(
            df["capacity_utilization_pct"] >= 100.0, "CRITICAL_OVERFLOW",
            np.where(df["capacity_utilization_pct"] >= 85.0, "HIGH_RISK", "NORMAL")
        )

        # Expected daily dispatched volume (bounded by physical throughput capacity)
        df["forecast_dispatched_volume"] = np.round(
            np.minimum(df["forecast_order_volume"], df["daily_capacity"] * 0.98), 1
        )

        # Projected daily backlog accumulation
        df["projected_daily_backlog"] = np.round(
            np.maximum(0.0, df["forecast_order_volume"] - df["forecast_dispatched_volume"]), 1
        )

        self.is_fitted = True
        return df

    def save(self, artifact_path: str = "models/artifacts/hub_workload_forecaster.joblib") -> str:
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        bundle = {
            "bottleneck_threshold_pct": self.bottleneck_threshold_pct,
            "version": "1.0.0"
        }
        joblib.dump(bundle, artifact_path)
        logger.info(f"Saved HubWorkloadForecaster bundle to {artifact_path}")
        return artifact_path
