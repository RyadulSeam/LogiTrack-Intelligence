import duckdb
import pandas as pd

db_path = r"F:\LogiTrack-Intelligence\data\lake\logitrack.duckdb"
con = duckdb.connect(db_path, read_only=True)

print("=== CRITICAL DATA INTEGRITY AUDIT ===")

# 1. FactOrders Denominator & Status check
print("\n--- 1. FactOrders Delivery & Delay Verification ---")
df_orders = con.execute("""
    SELECT 
        COUNT(*) as total_orders,
        COUNT(CASE WHEN order_status = 'Delivered' THEN 1 END) as delivered_orders,
        COUNT(CASE WHEN order_status = 'Cancelled' THEN 1 END) as cancelled_orders,
        COUNT(CASE WHEN order_status = 'Delivered' AND is_on_time = true THEN 1 END) as on_time_deliveries,
        COUNT(CASE WHEN order_status = 'Delivered' AND is_delayed = true THEN 1 END) as delayed_deliveries,
        COUNT(CASE WHEN is_delayed = true THEN 1 END) as total_delayed_any_status,
        COUNT(CASE WHEN delay_reason IS NOT NULL THEN 1 END) as non_null_delay_reasons,
        AVG(CASE WHEN order_status = 'Delivered' THEN delivery_time_hours END) as avg_delivery_time_delivered,
        AVG(CASE WHEN order_status = 'Delivered' AND is_delayed = true THEN delivery_time_hours END) as avg_delayed_time,
        AVG(CASE WHEN order_status = 'Delivered' AND is_on_time = true THEN delivery_time_hours END) as avg_ontime_time
    FROM warehouse.fact_orders
""").df()
print(df_orders.T)

# 2. FactOrders Delay Reasons breakdown
print("\n--- 2. Delay Reasons Distribution ---")
df_reasons = con.execute("""
    SELECT delay_reason, COUNT(*) as count, 
           ROUND(COUNT(*) * 100.0 / SUM(COUNT(*)) OVER(), 2) as pct
    FROM warehouse.fact_orders
    WHERE delay_reason IS NOT NULL
    GROUP BY delay_reason
    ORDER BY count DESC
""").df()
print(df_reasons)

# 3. DimHub Capacity check
print("\n--- 3. DimHub Capacity ---")
df_hubs = con.execute("""
    SELECT hub_id, hub_name, city, state, daily_capacity
    FROM warehouse.dim_hub
    ORDER BY hub_id
""").df()
print(df_hubs)
print("Total Network Daily Capacity:", df_hubs['daily_capacity'].sum())

# 4. DimVehicle fields check
print("\n--- 4. DimVehicle Audit ---")
df_veh = con.execute("""
    SELECT 
        COUNT(*) as total_vehicles,
        COUNT(CASE WHEN current_status = 'Active' THEN 1 END) as active_vehicles,
        COUNT(CASE WHEN current_status = 'Maintenance' THEN 1 END) as in_maintenance,
        COUNT(CASE WHEN is_maintenance_alert = true THEN 1 END) as alert_vehicles,
        AVG(lifetime_breakdowns) as avg_breakdowns,
        MIN(lifetime_breakdowns) as min_breakdowns,
        MAX(lifetime_breakdowns) as max_breakdowns
    FROM warehouse.dim_vehicle
""").df()
print(df_veh.T)

df_veh_types = con.execute("""
    SELECT vehicle_type, COUNT(*) as count
    FROM warehouse.dim_vehicle
    GROUP BY vehicle_type
""").df()
print("Vehicle Types:", df_veh_types.to_dict(orient='records'))

# 5. DimDriver fields check
print("\n--- 5. DimDriver Audit ---")
df_drv = con.execute("""
    SELECT 
        COUNT(*) as total_drivers,
        AVG(experience_years) as avg_exp,
        MIN(experience_years) as min_exp,
        MAX(experience_years) as max_exp,
        AVG(performance_rating) as avg_rating,
        MIN(performance_rating) as min_rating,
        MAX(performance_rating) as max_rating
    FROM warehouse.dim_driver
""").df()
print(df_drv.T)

# 6. FactMaintenance Expense & Downtime check
print("\n--- 6. FactMaintenance Expense & Downtime ---")
df_maint = con.execute("""
    SELECT 
        COUNT(*) as total_events,
        SUM(cost_usd) as total_expense_usd,
        AVG(cost_usd) as avg_cost_usd,
        SUM(downtime_hours) as total_downtime_hours,
        AVG(downtime_hours) as avg_downtime_hours,
        COUNT(completed_timestamp) as completed_events,
        COUNT(CASE WHEN status = 'Completed' THEN 1 END) as status_completed,
        COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as status_in_progress,
        COUNT(CASE WHEN status = 'Scheduled' THEN 1 END) as status_scheduled
    FROM warehouse.fact_maintenance
""").df()
print(df_maint.T)

con.close()
