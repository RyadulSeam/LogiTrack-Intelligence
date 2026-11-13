"""
Simulation Orchestrator
LogiTrack Intelligence — Phase 2

Command-line orchestrator that executes the full synthetic generation workflow
and outputs reproducible CSV datasets to data/synthetic/.
"""

import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import yaml
from loguru import logger

from logitrack.simulation.order_generator import OrderGenerator
from logitrack.simulation.event_generator import EventGenerator
from logitrack.simulation.telemetry_generator import TelemetryGenerator
from logitrack.simulation.maintenance_generator import MaintenanceGenerator


def run_simulation(config_path: str = "configs/simulation_config.yaml"):
    logger.info("Initializing LogiTrack Synthetic Generation Orchestrator...")
    
    # 1. Load config
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    seed = config.get("seed", 42)
    scales = config.get("scales", {})
    num_orders = scales.get("orders", 10000)
    num_maintenance = scales.get("maintenance_records", 500)
    
    output_dir = Path("data/synthetic")
    output_dir.mkdir(parents=True, exist_ok=True)

    # 2. Extract driver IDs & vehicle codes from source master
    drivers_df = pd.read_csv("data/source/Drivers.csv")
    vehicles_df = pd.read_csv("data/source/Vehicles.csv")
    
    driver_ids = list(drivers_df["DriverID"].unique())
    vehicle_codes = list(vehicles_df["Vehicle Code"].unique())

    logger.info(f"Loaded master references: {len(driver_ids)} drivers, {len(vehicle_codes)} vehicles")

    # Date range for synthetic baseline: Jan 1, 2024 to Nov 13, 2026
    start_date = datetime(2024, 1, 1, 8, 0, 0)
    end_date = datetime(2026, 11, 13, 18, 0, 0)

    # 3. Generate Orders
    logger.info(f"Generating {num_orders:,} synthetic orders...")
    order_gen = OrderGenerator(seed=seed)
    orders = order_gen.generate_orders(
        num_orders=num_orders,
        start_date=start_date,
        end_date=end_date,
        driver_ids=driver_ids,
        vehicle_codes=vehicle_codes
    )
    orders_df = pd.DataFrame(orders)
    orders_path = output_dir / "synthetic_orders.csv"
    orders_df.to_csv(orders_path, index=False)
    logger.success(f"Saved synthetic orders to {orders_path} ({len(orders_df):,} records)")

    # 4. Generate Order Lifecycle Events (for a sample of orders to keep local size bounded)
    logger.info("Generating granular order lifecycle events...")
    event_gen = EventGenerator(seed=seed)
    all_events = []
    
    # Generate events for first 2,000 orders to keep immediate footprint lean (~15K events)
    sample_orders = orders[:2000]
    for ord_dict in sample_orders:
        events = event_gen.generate_order_events(ord_dict)
        all_events.extend(events)

    events_df = pd.DataFrame(all_events)
    events_path = output_dir / "synthetic_order_events.csv"
    events_df.to_csv(events_path, index=False)
    logger.success(f"Saved order lifecycle events to {events_path} ({len(events_df):,} events)")

    # 5. Generate Vehicle Telemetry Pings
    logger.info("Generating vehicle IoT GPS telematics pings...")
    telem_gen = TelemetryGenerator(seed=seed)
    all_telemetry = []
    
    # Generate trips for delivered orders sample
    delivered_sample = [o for o in orders if o["order_status"] == "Delivered"][:400]
    for o in delivered_sample:
        trip_start = datetime.strptime(o["order_timestamp"], "%Y-%m-%d %H:%M:%S")
        pings = telem_gen.generate_trip_telemetry(
            vehicle_code=o["vehicle_code"],
            origin_hub=o["origin_hub"],
            dest_hub=o["destination_hub"],
            start_time=trip_start,
            trip_duration_hours=o["delivery_time_hours"] or 3.5
        )
        all_telemetry.extend(pings)

    telemetry_df = pd.DataFrame(all_telemetry)
    telemetry_path = output_dir / "synthetic_telemetry.csv"
    telemetry_df.to_csv(telemetry_path, index=False)
    logger.success(f"Saved GPS telematics to {telemetry_path} ({len(telemetry_df):,} pings)")

    # 6. Generate Maintenance Logs
    logger.info(f"Generating {num_maintenance:,} vehicle maintenance records...")
    maint_gen = MaintenanceGenerator(seed=seed)
    maintenance_records = maint_gen.generate_maintenance_logs(
        vehicle_codes=vehicle_codes,
        num_records=num_maintenance,
        start_date=start_date,
        end_date=end_date
    )
    maint_df = pd.DataFrame(maintenance_records)
    maint_path = output_dir / "synthetic_maintenance.csv"
    maint_df.to_csv(maint_path, index=False)
    logger.success(f"Saved maintenance logs to {maint_path} ({len(maint_df):,} records)")

    print("\n" + "=" * 60)
    print("SYNTHETIC GENERATION SUMMARY")
    print("=" * 60)
    print(f"[*] Synthetic Orders:      {len(orders_df):,} rows")
    print(f"[*] Lifecycle Events:      {len(events_df):,} rows")
    print(f"[*] Telemetry GPS Pings:   {len(telemetry_df):,} rows")
    print(f"[*] Maintenance Records:   {len(maint_df):,} rows")
    print(f"[*] Destination:           {output_dir}")
    print(f"[*] Random Seed:           {seed} (Fully reproducible)")
    print("=" * 60)


if __name__ == "__main__":
    run_simulation()
