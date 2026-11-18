"""
Stage 3: Export Clean Semantic Model Data for Power BI
Exports verified tables into dashboards/powerbi/data_export/ for instant loading in Power BI Desktop.
"""
import os
import duckdb
import pandas as pd

con = duckdb.connect('data/lake/logitrack.duckdb', read_only=True)
out_dir = 'dashboards/powerbi/data_export'
os.makedirs(out_dir, exist_ok=True)

print("Exporting Semantic Model Tables to CSV...")

# 1. DimDate
df_date = con.execute("SELECT * FROM warehouse.dim_date ORDER BY date_key;").df()
df_date.to_csv(f"{out_dir}/DimDate.csv", index=False)
print(f"  Exported DimDate.csv: {len(df_date):,} rows")

# 2. DimHub
df_hub = con.execute("SELECT * FROM warehouse.dim_hub ORDER BY hub_key;").df()
df_hub.to_csv(f"{out_dir}/DimHub.csv", index=False)
print(f"  Exported DimHub.csv: {len(df_hub):,} rows")

# 3. DimDriver
df_driver = con.execute("SELECT * FROM warehouse.dim_driver ORDER BY driver_key;").df()
df_driver.to_csv(f"{out_dir}/DimDriver.csv", index=False)
print(f"  Exported DimDriver.csv: {len(df_driver):,} rows")

# 4. DimVehicle
df_veh = con.execute("SELECT * FROM warehouse.dim_vehicle ORDER BY vehicle_key;").df()
df_veh.to_csv(f"{out_dir}/DimVehicle.csv", index=False)
print(f"  Exported DimVehicle.csv: {len(df_veh):,} rows")

# 5. FactOrders (Cleaned: drop package_weight_kg since it's 100% null)
df_orders = con.execute("""
    SELECT 
        order_id,
        order_date_key,
        delivery_date_key,
        hub_key,
        driver_key,
        vehicle_key,
        order_status,
        is_delayed,
        is_on_time,
        delay_reason,
        csat_score,
        delivery_time_hours,
        hub_processing_time_hours,
        data_origin
    FROM warehouse.fact_orders 
    ORDER BY order_id;
""").df()
df_orders.to_csv(f"{out_dir}/FactOrders.csv", index=False)
print(f"  Exported FactOrders.csv: {len(df_orders):,} rows")

# 6. FactHubHourly
df_hourly = con.execute("SELECT * FROM warehouse.fact_hub_hourly ORDER BY date_key, hub_key, hour_of_day;").df()
df_hourly.to_csv(f"{out_dir}/FactHubHourly.csv", index=False)
print(f"  Exported FactHubHourly.csv: {len(df_hourly):,} rows")

# 7. FactMaintenance (Joined with dim_vehicle to include vehicle_key FK)
df_maint = con.execute("""
    SELECT 
        m.maintenance_id,
        v.vehicle_key,
        m.vehicle_code,
        m.service_type,
        m.status AS maintenance_status,
        m.scheduled_date,
        m.completed_date,
        m.downtime_hours,
        m.cost_usd,
        m.data_origin
    FROM read_csv_auto('data/synthetic/synthetic_maintenance.csv') m
    JOIN warehouse.dim_vehicle v ON m.vehicle_code = v.vehicle_code
    ORDER BY m.scheduled_date;
""").df()
df_maint.to_csv(f"{out_dir}/FactMaintenance.csv", index=False)
print(f"  Exported FactMaintenance.csv: {len(df_maint):,} rows")

# 8. FactMLPredictions
df_preds = con.execute("""
    SELECT 
        p.prediction_id,
        p.model_id,
        r.model_name,
        p.entity_type,
        CAST(p.entity_id AS BIGINT) AS order_id,
        p.predicted_label,
        p.predicted_score,
        p.prediction_timestamp
    FROM ml.predictions p
    JOIN ml.model_registry r ON p.model_id = r.model_id;
""").df()
df_preds.to_csv(f"{out_dir}/FactMLPredictions.csv", index=False)
print(f"  Exported FactMLPredictions.csv: {len(df_preds):,} rows")

con.close()
print("\nAll Semantic Model data files successfully exported to:", out_dir)
