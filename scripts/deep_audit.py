"""
Deep Data Profiler & Discrepancy Analyzer
LogiTrack Intelligence - Phase 1 Audit
"""
import pandas as pd
from pathlib import Path

drivers = pd.read_csv("data/source/Drivers.csv")
orders = pd.read_csv("data/source/Orders.csv")
vehicles = pd.read_csv("data/source/Vehicles.csv")
hubs = pd.read_csv("data/source/Hubs.csv")

print("=== 1. DRIVER NAME VS ID IN ORDERS ===")
driver_map = dict(zip(drivers["DriverID"], drivers["DriverName"]))
unique_pairs = orders[["Driver ID", "Driver Name"]].drop_duplicates()
print(f"Total unique (Driver ID, Driver Name) combinations in Orders: {len(unique_pairs)}")

mismatches = []
for _, r in unique_pairs.iterrows():
    d_id = r["Driver ID"]
    ord_name = str(r["Driver Name"]).strip()
    master_name = str(driver_map.get(d_id)).strip()
    if ord_name != master_name:
        mismatches.append((d_id, ord_name, master_name))

print(f"Number of mismatched pairs: {len(mismatches)}")
print("Sample mismatches (Driver ID, In Orders, In Master):")
for item in mismatches[:10]:
    print(f"  ID {item[0]}: Orders='{item[1]}' vs Master='{item[2]}'")

# Check if Driver Name in Orders actually corresponds to another Driver ID
name_to_id_master = dict(zip(drivers["DriverName"], drivers["DriverID"]))
aligned_by_name = 0
for d_id, ord_name, master_name in mismatches:
    if ord_name in name_to_id_master:
        aligned_by_name += 1
print(f"Driver names in Orders that exist in Master under a DIFFERENT ID: {aligned_by_name}/{len(mismatches)}")

print("\n=== 2. VEHICLES AUDIT ===")
used_vehicles = set(orders["Vehicle Name"].unique())
all_vehicles = set(vehicles["Vehicle Code"].unique())
unused = all_vehicles - used_vehicles
print(f"Vehicles in Master: {len(all_vehicles)}")
print(f"Vehicles used in Orders: {len(used_vehicles)}")
print(f"Unused vehicles in Orders: {unused}")
print("\nUnused vehicle details:")
print(vehicles[vehicles["Vehicle Code"].isin(unused)][["Vehicle ID", "Vehicle Code", "Vehicle Model", "Vehicle Status", "Maintenance count Alert"]])

print("\n=== 3. DATE COLUMNS INSPECTION ===")
def inspect_dates(series, col_name):
    clean = series.dropna().astype(str)
    # Check format examples
    sample_dash = [x for x in clean if "-" in x][:3]
    sample_slash = [x for x in clean if "/" in x][:3]
    print(f"Column '{col_name}':")
    print(f"  Sample dash entries: {sample_dash}")
    print(f"  Sample slash entries: {sample_slash}")
    # Flexible parsing
    parsed = pd.to_datetime(clean, format="mixed", dayfirst=True)
    print(f"  Parsed range: {parsed.min().date()} to {parsed.max().date()}")

inspect_dates(orders["Order Date"], "Order Date")
inspect_dates(orders["Actual Delivery Date"], "Actual Delivery Date")
inspect_dates(drivers["Hire Date"], "Hire Date")
inspect_dates(vehicles["Purchase Date"], "Purchase Date")

print("\n=== 4. CANCELLED ORDERS & DELAY CONSISTENCY ===")
cancelled = orders[orders["Order Status"] == "Cancelled"]
print(f"Cancelled orders count: {len(cancelled)}")
print(f"Cancelled with null Delivery Date: {cancelled['Actual Delivery Date'].isnull().sum()}")
print(f"Cancelled with null Delivery Time: {cancelled['Delivery Time Hours'].isnull().sum()}")
print(f"Cancelled customer satisfaction scores: {cancelled['Customer Satisfaction Score'].value_counts().to_dict()}")

delayed = orders[orders["Is Delayed"] == True]
print(f"\nDelayed orders count: {len(delayed)}")
print(f"Delayed orders with Delay Reason: {delayed['Delay Reason'].notnull().sum()}")
print(f"Non-delayed orders with Delay Reason: {orders[orders['Is Delayed'] == False]['Delay Reason'].notnull().sum()}")
