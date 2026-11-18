"""
Stage 1 Part 2: Deep Data Quality & Business Rules Inspection
"""
import duckdb
import pandas as pd

con = duckdb.connect('data/lake/logitrack.duckdb', read_only=True)

print("=" * 70)
print("SECTION A: fact_orders — DATA QUALITY DEEP DIVE")
print("=" * 70)

# A1. Order Status Distribution
print("\n--- A1. Order Status Distribution ---")
print(con.execute("SELECT order_status, COUNT(*) AS cnt, ROUND(100.0*COUNT(*)/SUM(COUNT(*)) OVER(), 2) AS pct FROM warehouse.fact_orders GROUP BY 1 ORDER BY 2 DESC;").df().to_string(index=False))

# A2. Delay Distribution
print("\n--- A2. Delay Distribution ---")
print(con.execute("SELECT is_delayed, COUNT(*) AS cnt FROM warehouse.fact_orders GROUP BY 1;").df().to_string(index=False))

# A3. Delay Reasons
print("\n--- A3. Delay Reasons ---")
print(con.execute("SELECT delay_reason, COUNT(*) AS cnt FROM warehouse.fact_orders WHERE delay_reason IS NOT NULL GROUP BY 1 ORDER BY 2 DESC LIMIT 15;").df().to_string(index=False))

# A4. CSAT Score Distribution
print("\n--- A4. CSAT Score Distribution ---")
print(con.execute("SELECT csat_score, COUNT(*) AS cnt FROM warehouse.fact_orders WHERE csat_score IS NOT NULL GROUP BY 1 ORDER BY 1;").df().to_string(index=False))

# A5. Delivery Time Hours Stats
print("\n--- A5. Delivery Time Hours Stats ---")
print(con.execute("SELECT MIN(delivery_time_hours) AS min_hrs, ROUND(AVG(delivery_time_hours),2) AS avg_hrs, ROUND(QUANTILE_CONT(delivery_time_hours, 0.5),2) AS median_hrs, MAX(delivery_time_hours) AS max_hrs, COUNT(*) FILTER (WHERE delivery_time_hours IS NULL) AS null_count FROM warehouse.fact_orders;").df().to_string(index=False))

# A6. Hub Processing Time Stats
print("\n--- A6. Hub Processing Time Stats ---")
print(con.execute("SELECT MIN(hub_processing_time_hours) AS min_hrs, ROUND(AVG(hub_processing_time_hours),2) AS avg_hrs, MAX(hub_processing_time_hours) AS max_hrs FROM warehouse.fact_orders;").df().to_string(index=False))

# A7. Delivery Priority Distribution
print("\n--- A7. Delivery Priority Distribution ---")
print(con.execute("SELECT delivery_priority, COUNT(*) AS cnt FROM warehouse.fact_orders GROUP BY 1;").df().to_string(index=False))

# A8. Package Weight
print("\n--- A8. Package Weight ---")
print(con.execute("SELECT COUNT(*) FILTER (WHERE package_weight_kg IS NOT NULL) AS has_weight, COUNT(*) FILTER (WHERE package_weight_kg IS NULL) AS no_weight FROM warehouse.fact_orders;").df().to_string(index=False))

# A9. Data Origin
print("\n--- A9. Data Origin ---")
print(con.execute("SELECT data_origin, COUNT(*) AS cnt FROM warehouse.fact_orders GROUP BY 1;").df().to_string(index=False))

# A10. Date Range
print("\n--- A10. Date Range ---")
print(con.execute("SELECT MIN(d.full_date) AS min_date, MAX(d.full_date) AS max_date FROM warehouse.fact_orders f JOIN warehouse.dim_date d ON f.order_date_key = d.date_key;").df().to_string(index=False))

# A11. Null FK checks
print("\n--- A11. FK Null Counts in fact_orders ---")
print(con.execute("SELECT COUNT(*) FILTER (WHERE hub_key IS NULL) AS null_hub, COUNT(*) FILTER (WHERE driver_key IS NULL) AS null_driver, COUNT(*) FILTER (WHERE vehicle_key IS NULL) AS null_vehicle, COUNT(*) FILTER (WHERE order_date_key IS NULL) AS null_order_date, COUNT(*) FILTER (WHERE delivery_date_key IS NULL) AS null_delivery_date FROM warehouse.fact_orders;").df().to_string(index=False))

print("\n" + "=" * 70)
print("SECTION B: DIMENSION TABLES — DATA QUALITY")
print("=" * 70)

# B1. dim_hub
print("\n--- B1. dim_hub All Records ---")
print(con.execute("SELECT hub_key, hub_id, hub_name, city, state, daily_capacity, latitude, longitude, data_origin FROM warehouse.dim_hub;").df().to_string(index=False))

# B2. dim_driver stats
print("\n--- B2. dim_driver Summary ---")
print(con.execute("SELECT employment_type, COUNT(*) AS cnt, ROUND(AVG(experience_years),1) AS avg_exp, ROUND(AVG(performance_rating),1) AS avg_rating FROM warehouse.dim_driver GROUP BY 1;").df().to_string(index=False))

print("\n--- B2b. dim_driver Rating Distribution ---")
print(con.execute("SELECT performance_rating, COUNT(*) FROM warehouse.dim_driver GROUP BY 1 ORDER BY 1;").df().to_string(index=False))

# B3. dim_vehicle stats
print("\n--- B3. dim_vehicle Status Distribution ---")
print(con.execute("SELECT current_status, COUNT(*) AS cnt FROM warehouse.dim_vehicle GROUP BY 1 ORDER BY 2 DESC;").df().to_string(index=False))

print("\n--- B3b. dim_vehicle Type Distribution ---")
print(con.execute("SELECT vehicle_type, COUNT(*) AS cnt FROM warehouse.dim_vehicle GROUP BY 1 ORDER BY 2 DESC;").df().to_string(index=False))

print("\n--- B3c. dim_vehicle Maintenance Alert ---")
print(con.execute("SELECT is_maintenance_alert, COUNT(*) AS cnt FROM warehouse.dim_vehicle GROUP BY 1;").df().to_string(index=False))

print("\n--- B3d. dim_vehicle Breakdown Range ---")
print(con.execute("SELECT MIN(lifetime_breakdowns) AS min_bd, ROUND(AVG(lifetime_breakdowns),1) AS avg_bd, MAX(lifetime_breakdowns) AS max_bd FROM warehouse.dim_vehicle;").df().to_string(index=False))

print("\n--- B3e. dim_vehicle Purchase Date Range ---")
print(con.execute("SELECT MIN(purchase_date) AS min_purchase, MAX(purchase_date) AS max_purchase FROM warehouse.dim_vehicle;").df().to_string(index=False))

# B4. dim_route
print("\n--- B4. dim_route Summary ---")
print(con.execute("SELECT COUNT(*) AS total_routes, ROUND(MIN(distance_km),1) AS min_km, ROUND(AVG(distance_km),1) AS avg_km, ROUND(MAX(distance_km),1) AS max_km FROM warehouse.dim_route;").df().to_string(index=False))

print("\n" + "=" * 70)
print("SECTION C: fact_hub_hourly — DATA QUALITY")
print("=" * 70)
print(con.execute("SELECT COUNT(*) AS total_rows, MIN(h.hub_name) AS sample_hub, MIN(d.full_date) AS min_date, MAX(d.full_date) AS max_date, ROUND(AVG(f.orders_received),2) AS avg_incoming, ROUND(AVG(f.orders_dispatched),2) AS avg_outgoing, ROUND(AVG(f.backlog_volume),2) AS avg_backlog, ROUND(AVG(f.capacity_utilization_pct),2) AS avg_cap_util FROM warehouse.fact_hub_hourly f JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key JOIN warehouse.dim_date d ON f.date_key = d.date_key;").df().to_string(index=False))

print("\n--- Hub Hourly by Hub ---")
print(con.execute("SELECT h.hub_name, COUNT(*) AS hourly_rows, ROUND(AVG(f.orders_received),2) AS avg_incoming, ROUND(AVG(f.backlog_volume),2) AS avg_backlog FROM warehouse.fact_hub_hourly f JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key GROUP BY 1 ORDER BY 2 DESC;").df().to_string(index=False))

print("\n" + "=" * 70)
print("SECTION D: ML SCHEMA — PREDICTIONS & REGISTRY CONTENT")
print("=" * 70)
print("\n--- D1. Model Registry ---")
print(con.execute("SELECT model_id, model_name, version, algorithm, training_dataset_size, is_active FROM ml.model_registry;").df().to_string(index=False))

print("\n--- D2. Model Evaluations ---")
print(con.execute("SELECT r.model_name, e.metric_name, e.metric_value FROM ml.model_evaluations e JOIN ml.model_registry r ON e.model_id = r.model_id ORDER BY r.model_name, e.metric_name;").df().to_string(index=False))

print("\n--- D3. Predictions Sample ---")
print(con.execute("SELECT entity_type, predicted_label, predicted_score, prediction_timestamp FROM ml.predictions LIMIT 5;").df().to_string(index=False))

print("\n" + "=" * 70)
print("SECTION E: SYNTHETIC MAINTENANCE DATA (CSV)")
print("=" * 70)
import os
maint_path = 'data/synthetic/synthetic_maintenance.csv'
if os.path.exists(maint_path):
    mdf = pd.read_csv(maint_path)
    print(f"Row Count: {len(mdf)}")
    print(f"Columns: {mdf.columns.tolist()}")
    print(f"\nService Type Distribution:")
    print(mdf['service_type'].value_counts().to_string())
    print(f"\nStatus Distribution:")
    print(mdf['status'].value_counts().to_string())
    print(f"\nDowntime Stats: min={mdf['downtime_hours'].min()}, mean={mdf['downtime_hours'].mean():.1f}, max={mdf['downtime_hours'].max()}")
    print(f"Cost Stats: min={mdf['cost_usd'].min()}, mean={mdf['cost_usd'].mean():.1f}, max={mdf['cost_usd'].max()}")
else:
    print("File not found.")

print("\n" + "=" * 70)
print("SECTION F: warehouse.fact_maintenance STATUS")
print("=" * 70)
cnt = con.execute("SELECT COUNT(*) FROM warehouse.fact_maintenance;").fetchone()[0]
print(f"warehouse.fact_maintenance row count: {cnt}")
if cnt == 0:
    print("WARNING: fact_maintenance is EMPTY. Maintenance data not loaded into warehouse.")

con.close()
print("\n[DEEP INSPECTION COMPLETE]")
