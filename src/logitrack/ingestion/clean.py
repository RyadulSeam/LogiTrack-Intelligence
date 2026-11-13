"""
Batch ETL — Cleaning & Standardization Module
LogiTrack Intelligence — Phase 4

Applies whitespace trimming, mixed date standardization (to ISO YYYY-MM-DD),
and categorical normalization across raw DataFrames.
"""

from typing import Optional
import pandas as pd
from loguru import logger


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Strips leading/trailing whitespaces and converts empty strings to NaN."""
    cleaned = df.copy()
    str_cols = cleaned.select_dtypes(include=["object", "string"]).columns
    for col in str_cols:
        cleaned[col] = cleaned[col].astype(str).str.strip()
        cleaned[col] = cleaned[col].replace({"": None, "nan": None, "None": None, "NULL": None})
    return cleaned


def standardize_date_series(series: pd.Series) -> pd.Series:
    """
    Standardizes heterogeneous date strings (DD-MM-YYYY and M/D/YYYY)
    into ISO-8601 YYYY-MM-DD string representation.
    """
    # Use pandas mixed format parsing with dayfirst=True for DD-MM-YYYY compatibility
    parsed = pd.to_datetime(series, format="mixed", dayfirst=True, errors="coerce")
    return parsed.dt.strftime("%Y-%m-%d")


def clean_hubs(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_string_columns(df)
    cleaned["Hub ID"] = pd.to_numeric(cleaned["Hub ID"], errors="coerce").astype(int)
    cleaned["Hub Capacity"] = pd.to_numeric(cleaned["Hub Capacity"], errors="coerce").astype(int)
    return cleaned


def clean_drivers(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_string_columns(df)
    cleaned["DriverID"] = pd.to_numeric(cleaned["DriverID"], errors="coerce").astype(int)
    cleaned["Hire Date"] = standardize_date_series(cleaned["Hire Date"])
    cleaned["Experience Years"] = pd.to_numeric(cleaned["Experience Years"], errors="coerce").astype(int)
    cleaned["Performance Rating"] = pd.to_numeric(cleaned["Performance Rating"], errors="coerce").astype(int)
    return cleaned


def clean_vehicles(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_string_columns(df)
    cleaned["Vehicle ID"] = pd.to_numeric(cleaned["Vehicle ID"], errors="coerce").astype(int)
    cleaned["Purchase Date"] = standardize_date_series(cleaned["Purchase Date"])
    cleaned["Breakdown"] = pd.to_numeric(cleaned["Breakdown"], errors="coerce").fillna(0).astype(int)
    cleaned["Maintenance count Alert"] = (
        pd.to_numeric(cleaned["Maintenance count Alert"], errors="coerce").fillna(0).astype(int)
    )
    return cleaned


def clean_orders(df: pd.DataFrame) -> pd.DataFrame:
    cleaned = clean_string_columns(df)
    cleaned["Order ID"] = pd.to_numeric(cleaned["Order ID"], errors="coerce").astype(int)
    cleaned["Order Date"] = standardize_date_series(cleaned["Order Date"])
    cleaned["Actual Delivery Date"] = standardize_date_series(cleaned["Actual Delivery Date"])
    
    # Booleans
    cleaned["Is Delayed"] = cleaned["Is Delayed"].astype(str).str.upper() == "TRUE"
    cleaned["Is On Time"] = cleaned["Is On Time"].astype(str).str.upper() == "TRUE"
    
    # Numerics
    cleaned["Driver ID"] = pd.to_numeric(cleaned["Driver ID"], errors="coerce").astype(int)
    cleaned["Customer Satisfaction Score"] = pd.to_numeric(cleaned["Customer Satisfaction Score"], errors="coerce")
    cleaned["Delivery Time Hours"] = pd.to_numeric(cleaned["Delivery Time Hours"], errors="coerce")
    cleaned["Hub Processing Time Hours"] = pd.to_numeric(cleaned["Hub Processing Time Hours"], errors="coerce")
    
    return cleaned
