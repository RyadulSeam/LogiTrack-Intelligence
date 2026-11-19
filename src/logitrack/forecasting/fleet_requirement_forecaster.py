"""
Fleet Requirement & Vehicle Allocation Forecaster
LogiTrack Intelligence — Phase 9: Forecasting Engineering

Projects daily required vehicle counts per vehicle type (Van, Truck, Pickup, Box Truck)
based on forecasted regional demand, payload constraints, and operating capacity.
Computes deficit/surplus gaps against the 33 active fleet baseline.
"""

from typing import Dict, Any, List
import os
import joblib
import numpy as np
import pandas as pd
from loguru import logger


# Historical baseline parameters from logistics warehouse
VEHICLE_CONFIG = {
    "Van": {
        "share_pct": 0.6503,
        "daily_parcel_capacity": 35,  # Avg parcels delivered per van/day
        "active_fleet_supply": 22
    },
    "Truck": {
        "share_pct": 0.1929,
        "daily_parcel_capacity": 25,
        "active_fleet_supply": 6
    },
    "Pickup": {
        "share_pct": 0.1031,
        "daily_parcel_capacity": 40,
        "active_fleet_supply": 2
    },
    "Box Truck": {
        "share_pct": 0.0537,
        "daily_parcel_capacity": 20,
        "active_fleet_supply": 3
    }
}


class FleetRequirementForecaster:
    """
    Forecaster for fleet vehicle allocation and deficit/surplus risk.
    """

    def __init__(self, vehicle_configs: Dict[str, Any] = VEHICLE_CONFIG):
        self.vehicle_configs = vehicle_configs
        self.is_fitted = True

    def forecast_fleet_needs(self, demand_forecast_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculates required vehicle counts per vehicle type for each forecasted day and hub.
        """
        logger.info(f"Computing fleet requirement projections from {len(demand_forecast_df)} demand records")
        records = []

        for _, row in demand_forecast_df.iterrows():
            total_forecast = row["forecast_order_volume"]
            f_date = row["forecast_date"]
            hub_name = row["hub_name"]

            for vtype, cfg in self.vehicle_configs.items():
                expected_parcels = total_forecast * cfg["share_pct"]
                # Vehicles needed = parcels / daily vehicle capacity
                vehicles_needed = int(np.ceil(expected_parcels / cfg["daily_parcel_capacity"]))
                vehicles_needed = max(1, vehicles_needed)
                
                # Active supply allocated to this hub (proportional approximation or statewide)
                active_supply = cfg["active_fleet_supply"]
                gap = active_supply - vehicles_needed
                
                records.append({
                    "forecast_date": f_date,
                    "hub_name": hub_name,
                    "vehicle_type": vtype,
                    "projected_parcels": round(expected_parcels, 1),
                    "vehicles_required": vehicles_needed,
                    "active_fleet_baseline": active_supply,
                    "surplus_or_deficit": gap,
                    "is_fleet_deficit": gap < 0,
                    "utilization_rate_pct": round((vehicles_needed / active_supply) * 100.0, 1)
                })

        return pd.DataFrame(records)

    def save(self, artifact_path: str = "models/artifacts/fleet_requirement_forecaster.joblib") -> str:
        os.makedirs(os.path.dirname(artifact_path), exist_ok=True)
        bundle = {
            "vehicle_configs": self.vehicle_configs,
            "version": "1.0.0"
        }
        joblib.dump(bundle, artifact_path)
        logger.info(f"Saved FleetRequirementForecaster bundle to {artifact_path}")
        return artifact_path
