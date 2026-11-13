"""
Source Data Profiling & Audit Script
LogiTrack Intelligence - Phase 1

Audits all raw CSV files in data/source/ for completeness, types,
nulls, duplicates, anomalies, and cross-table foreign key relationships.
"""

import os
import re
from pathlib import Path
import pandas as pd
import numpy as np

DATA_DIR = Path("data/source")
FILES = {
    "hubs": DATA_DIR / "Hubs.csv",
    "drivers": DATA_DIR / "Drivers.csv",
    "vehicles": DATA_DIR / "Vehicles.csv",
    "orders": DATA_DIR / "Orders.csv",
}


def audit_file_basics():
    print("=" * 60)
    print("1. DATASET INVENTORY & SHAPES")
    print("=" * 60)
    dfs = {}
    for name, path in FILES.items():
        if not path.exists():
            print(f"[-] Missing: {path}")
            continue
        df = pd.read_csv(path)
        dfs[name] = df
        size_kb = os.path.getsize(path) / 1024
        print(f"[*] {name.upper()}: {len(df):,} rows, {len(df.columns)} cols ({size_kb:.1f} KB)")
        print(f"    Columns: {list(df.columns)}")
        print()
    return dfs


def audit_missing_and_duplicates(dfs):
    print("=" * 60)
    print("2. NULL VALUES & DUPLICATES CHECK")
    print("=" * 60)
    for name, df in dfs.items():
        print(f"--- {name.upper()} ---")
        full_dups = df.duplicated().sum()
        print(f"Full duplicate rows: {full_dups}")
        
        # Check primary key duplicates
        pk_candidates = {
            "hubs": "Hub ID",
            "drivers": "DriverID",
            "vehicles": "Vehicle ID",
            "orders": "Order ID"
        }
        pk = pk_candidates.get(name)
        if pk and pk in df.columns:
            pk_dups = df[pk].duplicated().sum()
            print(f"PK '{pk}' duplicates: {pk_dups} (unique: {df[pk].nunique():,})")
            
        nulls = df.isnull().sum()
        null_cols = nulls[nulls > 0]
        if len(null_cols) == 0:
            print("Missing values: None (100% clean)")
        else:
            print("Columns with missing values:")
            for col, count in null_cols.items():
                pct = (count / len(df)) * 100
                print(f"  - {col}: {count:,} ({pct:.2f}%)")
        print()


def audit_date_formats(dfs):
    print("=" * 60)
    print("3. DATE FORMAT CONSISTENCY & RANGES")
    print("=" * 60)
    date_cols = {
        "drivers": ["Hire Date"],
        "vehicles": ["Purchase Date"],
        "orders": ["Order Date", "Actual Delivery Date"]
    }
    for name, cols in date_cols.items():
        df = dfs[name]
        print(f"--- {name.upper()} ---")
        for col in cols:
            if col not in df.columns:
                continue
            sample = df[col].dropna().astype(str)
            # Detect slash vs dash
            dashes = sample.str.contains("-").sum()
            slashes = sample.str.contains("/").sum()
            print(f"Column '{col}':")
            print(f"  Dash formatted (e.g. DD-MM-YYYY): {dashes:,}")
            print(f"  Slash formatted (e.g. M/D/YYYY): {slashes:,}")
            
            # Try parsing
            parsed = pd.to_datetime(sample, dayfirst=True, errors="coerce")
            invalid = parsed.isnull().sum()
            print(f"  Successfully parsed: {len(parsed) - invalid:,}")
            print(f"  Invalid/Unparseable: {invalid}")
            if invalid == 0:
                print(f"  Min date: {parsed.min().strftime('%Y-%m-%d')}")
                print(f"  Max date: {parsed.max().strftime('%Y-%m-%d')}")
        print()


def audit_referential_integrity(dfs):
    print("=" * 60)
    print("4. REFERENTIAL INTEGRITY (FOREIGN KEYS)")
    print("=" * 60)
    orders = dfs["orders"]
    drivers = dfs["drivers"]
    hubs = dfs["hubs"]
    vehicles = dfs["vehicles"]
    
    # 1. Driver ID check
    orders_driver_ids = set(orders["Driver ID"].dropna().unique())
    source_driver_ids = set(drivers["DriverID"].dropna().unique())
    orphaned_drivers = orders_driver_ids - source_driver_ids
    print(f"[*] Driver ID Relationship:")
    print(f"    Unique Driver IDs in Orders: {len(orders_driver_ids)}")
    print(f"    Unique Driver IDs in Drivers.csv: {len(source_driver_ids)}")
    print(f"    Orphaned Driver IDs in Orders: {orphaned_drivers if orphaned_drivers else 'None (100% matched)'}")
    
    # Check Driver Name consistency
    driver_map = dict(zip(drivers["DriverID"], drivers["DriverName"]))
    mismatched_names = 0
    for _, row in orders.iterrows():
        d_id = row["Driver ID"]
        d_name = row["Driver Name"]
        if d_id in driver_map and driver_map[d_id] != d_name:
            mismatched_names += 1
    print(f"    Orders with mismatched Driver Name vs Driver ID: {mismatched_names}")

    # 2. Hub Name check
    orders_hubs = set(orders["Hub Name"].dropna().unique())
    source_hubs = set(hubs["HubName"].dropna().unique())
    orphaned_hubs = orders_hubs - source_hubs
    print(f"\n[*] Hub Name Relationship:")
    print(f"    Hubs in Orders: {orders_hubs}")
    print(f"    Hubs in Hubs.csv: {source_hubs}")
    print(f"    Orphaned Hubs: {orphaned_hubs if orphaned_hubs else 'None (100% matched)'}")

    # 3. Vehicle Reference check
    orders_vehicles = set(orders["Vehicle Name"].dropna().unique())
    # Is Vehicle Name matching Vehicle Code or Vehicle ID?
    vehicle_codes = set(vehicles["Vehicle Code"].dropna().unique())
    vehicle_models = set(vehicles["Vehicle Model"].dropna().unique())
    
    orphaned_codes = orders_vehicles - vehicle_codes
    print(f"\n[*] Vehicle Reference Relationship:")
    print(f"    Unique 'Vehicle Name' values in Orders: {len(orders_vehicles)}")
    print(f"    Unique 'Vehicle Code' in Vehicles.csv: {len(vehicle_codes)} (e.g. FT-001)")
    print(f"    Orders Vehicle Names not in Vehicles.csv: {len(orphaned_codes)}")
    if orphaned_codes:
        print(f"    Sample orphaned vehicle codes in Orders: {sorted(list(orphaned_codes))[:10]}")


def audit_distributions(dfs):
    print("=" * 60)
    print("5. CATEGORICAL DISTRIBUTIONS & METRICS")
    print("=" * 60)
    orders = dfs["orders"]
    print("[*] Order Status breakdown:")
    print(orders["Order Status"].value_counts(dropna=False).to_string())
    print("\n[*] Delay Flag breakdown:")
    print(orders["Is Delayed"].value_counts(dropna=False).to_string())
    print("\n[*] Vehicle Types in Orders:")
    print(orders["Vehicle Type"].value_counts(dropna=False).to_string())
    print("\n[*] Delay Reasons (Top 10):")
    print(orders["Delay Reason"].value_counts(dropna=False).head(10).to_string())
    print("\n[*] Numeric Columns Summary (Orders):")
    num_cols = ["Customer Satisfaction Score", "Delivery Time Hours", "Hub Processing Time Hours"]
    print(orders[num_cols].describe().round(2).to_string())


if __name__ == "__main__":
    dfs = audit_file_basics()
    audit_missing_and_duplicates(dfs)
    audit_date_formats(dfs)
    audit_referential_integrity(dfs)
    audit_distributions(dfs)
