"""
Time-Series Feature Engineering for Forecasting Pipeline
LogiTrack Intelligence — Phase 9: Forecasting Engineering
"""

from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
import duckdb
from loguru import logger


def extract_daily_demand_series(db_path: str = "data/lake/logitrack.duckdb", conn: Optional[duckdb.DuckDBPyConnection] = None) -> pd.DataFrame:
    """
    Extracts daily order counts and metrics per regional hub from DuckDB lakehouse.
    Returns a continuous time-series DataFrame indexed by date and hub.
    """
    logger.info(f"Extracting daily time-series from {db_path}")
    should_close = False
    if conn is None:
        conn = duckdb.connect(db_path)
        should_close = True
    
    query = """
    SELECT 
        d.full_date AS ds,
        h.hub_id,
        h.hub_name,
        h.city,
        h.daily_capacity,
        COUNT(f.order_id) AS order_volume,
        COUNT(CASE WHEN f.delivery_priority = 'High' THEN 1 END) AS high_priority_count,
        AVG(f.package_weight_kg) AS avg_package_weight,
        AVG(f.delivery_time_hours) AS avg_delivery_time,
        COUNT(CASE WHEN f.is_delayed THEN 1 END) AS delayed_count
    FROM warehouse.fact_orders f
    JOIN warehouse.dim_date d ON f.order_date_key = d.date_key
    JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
    GROUP BY d.full_date, h.hub_id, h.hub_name, h.city, h.daily_capacity
    ORDER BY h.hub_id, d.full_date;
    """
    df = conn.execute(query).fetchdf()
    if should_close:
        conn.close()
    
    df["ds"] = pd.to_datetime(df["ds"])
    logger.info(f"Extracted {len(df)} daily hub records across {df['hub_name'].nunique()} hubs.")
    return df


def build_time_series_features(df: pd.DataFrame, target_col: str = "order_volume") -> pd.DataFrame:
    """
    Generates non-leaking calendar, cyclical, lag, and rolling window features.
    Features are computed strictly per hub group.
    """
    features_list = []
    
    for hub_id, group in df.groupby("hub_id"):
        g = group.sort_values("ds").copy()
        
        # 1. Calendar Features
        g["day_of_week"] = g["ds"].dt.dayofweek
        g["day_of_month"] = g["ds"].dt.day
        g["month"] = g["ds"].dt.month
        g["quarter"] = g["ds"].dt.quarter
        g["is_weekend"] = (g["day_of_week"] >= 5).astype(int)
        g["day_of_year"] = g["ds"].dt.dayofyear
        
        # 2. Cyclical Trigonometric Encodings
        g["sin_dow"] = np.sin(2 * np.pi * g["day_of_week"] / 7.0)
        g["cos_dow"] = np.cos(2 * np.pi * g["day_of_week"] / 7.0)
        g["sin_month"] = np.sin(2 * np.pi * g["month"] / 12.0)
        g["cos_month"] = np.cos(2 * np.pi * g["month"] / 12.0)
        
        # 3. Lags (Past order demand)
        for lag in [1, 2, 3, 7, 14, 21, 28]:
            g[f"lag_{lag}"] = g[target_col].shift(lag)
            
        # 4. Rolling Window Features (strictly shifted by 1 to prevent target leakage)
        target_shifted = g[target_col].shift(1)
        g["rolling_mean_7"] = target_shifted.rolling(window=7, min_periods=1).mean()
        g["rolling_std_7"] = target_shifted.rolling(window=7, min_periods=1).std().fillna(0)
        g["rolling_min_7"] = target_shifted.rolling(window=7, min_periods=1).min()
        g["rolling_max_7"] = target_shifted.rolling(window=7, min_periods=1).max()
        
        g["rolling_mean_14"] = target_shifted.rolling(window=14, min_periods=1).mean()
        g["rolling_mean_28"] = target_shifted.rolling(window=28, min_periods=1).mean()
        g["rolling_std_28"] = target_shifted.rolling(window=28, min_periods=1).std().fillna(0)
        
        # 5. Expanding Mean
        g["expanding_mean"] = target_shifted.expanding(min_periods=1).mean()
        
        features_list.append(g)
        
    result_df = pd.concat(features_list, ignore_index=True)
    # Drop warm-up rows where lag features are NaN (e.g. first 28 days)
    lag_cols = [f"lag_{lag}" for lag in [1, 2, 3, 7, 14, 21, 28]]
    result_df = result_df.dropna(subset=lag_cols + [target_col]).reset_index(drop=True)
    return result_df


def split_chronological(df: pd.DataFrame, test_days: int = 92) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Performs a strict chronological, non-leaking train/test split.
    Test set consists of the last `test_days` days of the time-series.
    """
    cutoff_date = df["ds"].max() - pd.Timedelta(days=test_days)
    train_df = df[df["ds"] <= cutoff_date].copy()
    test_df = df[df["ds"] > cutoff_date].copy()
    
    logger.info(
        f"Chronological split at {cutoff_date.date()}: "
        f"Train={len(train_df)} records ({train_df['ds'].min().date()} to {train_df['ds'].max().date()}), "
        f"Test={len(test_df)} records ({test_df['ds'].min().date()} to {test_df['ds'].max().date()})"
    )
    return train_df, test_df
