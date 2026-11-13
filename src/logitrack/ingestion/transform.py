"""
Batch ETL — Transformation & Schema Mapping Module
LogiTrack Intelligence — Phase 4

Transforms cleaned source records into canonical Staging (Silver) schema specifications,
including geospatial hub coordinate enrichment and snake_case standardization.
"""

from datetime import datetime
from typing import Dict
import pandas as pd
from logitrack.simulation.geo_routes import TEXAS_HUBS


def transform_hubs_to_staging(df: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    stg = pd.DataFrame()
    stg["hub_id"] = df["Hub ID"]
    stg["hub_name"] = df["HubName"]
    stg["hub_capacity"] = df["Hub Capacity"]
    
    # Geospatial coordinate enrichment for Texas hubs
    stg["latitude"] = df["HubName"].map(lambda name: TEXAS_HUBS.get(name, (None, None))[0])
    stg["longitude"] = df["HubName"].map(lambda name: TEXAS_HUBS.get(name, (None, None))[1])
    
    stg["ingestion_batch_id"] = batch_id
    stg["data_origin"] = "source: original"
    stg["stg_updated_at"] = datetime.now()
    return stg


def transform_drivers_to_staging(df: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    stg = pd.DataFrame()
    stg["driver_id"] = df["DriverID"]
    stg["driver_name"] = df["DriverName"]
    stg["employment_type"] = df["Employment Type"]
    stg["hire_date"] = pd.to_datetime(df["Hire Date"]).dt.date
    stg["experience_years"] = df["Experience Years"]
    stg["performance_rating"] = df["Performance Rating"]
    
    stg["ingestion_batch_id"] = batch_id
    stg["data_origin"] = "source: original"
    stg["stg_updated_at"] = datetime.now()
    return stg


def transform_vehicles_to_staging(df: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    stg = pd.DataFrame()
    stg["vehicle_id"] = df["Vehicle ID"]
    stg["vehicle_code"] = df["Vehicle Code"]
    stg["vehicle_model"] = df["Vehicle Model"]
    stg["vehicle_status"] = df["Vehicle Status"]
    stg["breakdown_count"] = df["Breakdown"]
    stg["is_maintenance_alert"] = df["Maintenance count Alert"] == 1
    stg["purchase_date"] = pd.to_datetime(df["Purchase Date"]).dt.date
    
    stg["ingestion_batch_id"] = batch_id
    stg["data_origin"] = "source: original"
    stg["stg_updated_at"] = datetime.now()
    return stg


def transform_orders_to_staging(df: pd.DataFrame, batch_id: str) -> pd.DataFrame:
    stg = pd.DataFrame()
    stg["order_id"] = df["Order ID"]
    stg["order_date"] = pd.to_datetime(df["Order Date"]).dt.date
    stg["actual_delivery_date"] = pd.to_datetime(df["Actual Delivery Date"]).dt.date
    stg["order_status"] = df["Order Status"]
    stg["is_delayed"] = df["Is Delayed"]
    stg["is_on_time"] = df["Is On Time"]
    stg["delay_reason"] = df["Delay Reason"]
    stg["driver_id"] = df["Driver ID"]
    stg["driver_name_snapshot"] = df["Driver Name"]
    stg["hub_name"] = df["Hub Name"]
    stg["vehicle_code"] = df["Vehicle Name"]
    stg["vehicle_type"] = df["Vehicle Type"]
    stg["customer_satisfaction_score"] = df["Customer Satisfaction Score"]
    stg["delivery_time_hours"] = df["Delivery Time Hours"]
    stg["hub_processing_time_hours"] = df["Hub Processing Time Hours"]
    
    stg["ingestion_batch_id"] = batch_id
    stg["data_origin"] = "source: original"
    stg["stg_updated_at"] = datetime.now()
    return stg
