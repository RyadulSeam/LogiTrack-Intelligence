"""
Stage 4: Independent KPI Validation — SQL Calculations vs Expected DAX Results
Calculates expected baseline values directly from DuckDB for every KPI measure.
This output is the ground-truth for the KPI Validation Report.
"""
import duckdb
import pandas as pd

con = duckdb.connect('data/lake/logitrack.duckdb', read_only=True)

results = {}

print("=" * 70)
print("STAGE 4: INDEPENDENT KPI VALIDATION BASELINE")
print("=" * 70)

# --- SECTION 1: EXECUTIVE KPIs ---
print("\n--- 01. EXECUTIVE KPIs ---")

r = con.execute("SELECT COUNT(DISTINCT order_id) FROM warehouse.fact_orders;").fetchone()[0]
results['Total Orders'] = r
print(f"  Total Orders:               {r:>8,}")

r = con.execute("SELECT COUNT(*) FROM warehouse.fact_orders WHERE order_status = 'Delivered';").fetchone()[0]
results['Delivered Orders'] = r
print(f"  Delivered Orders:           {r:>8,}")

r = con.execute("SELECT COUNT(*) FROM warehouse.fact_orders WHERE order_status = 'Cancelled';").fetchone()[0]
results['Cancelled Orders'] = r
print(f"  Cancelled Orders:           {r:>8,}")

r = round(results['Cancelled Orders'] / results['Total Orders'] * 100, 4)
results['Cancellation Rate %'] = r
print(f"  Cancellation Rate %:        {r:>8.4f}%")

# --- SECTION 2: DELIVERY SLA KPIs ---
print("\n--- 02. DELIVERY SLA KPIs ---")

r = con.execute("""
    SELECT COUNT(*) FROM warehouse.fact_orders 
    WHERE order_status = 'Delivered' AND is_on_time = TRUE;
""").fetchone()[0]
results['On-Time Deliveries'] = r
print(f"  On-Time Deliveries:         {r:>8,}")

r = con.execute("""
    SELECT COUNT(*) FROM warehouse.fact_orders 
    WHERE order_status = 'Delivered' AND is_delayed = TRUE;
""").fetchone()[0]
results['Delayed Deliveries'] = r
print(f"  Delayed Deliveries:         {r:>8,}")

r = round(results['On-Time Deliveries'] / results['Delivered Orders'] * 100, 4)
results['On-Time Delivery Rate %'] = r
print(f"  On-Time Delivery Rate %:    {r:>8.4f}%")

r = round(results['Delayed Deliveries'] / results['Delivered Orders'] * 100, 4)
results['Delay Rate %'] = r
print(f"  Delay Rate %:               {r:>8.4f}%")

r = con.execute("""
    SELECT ROUND(AVG(delivery_time_hours), 4) FROM warehouse.fact_orders 
    WHERE order_status = 'Delivered' AND delivery_time_hours IS NOT NULL;
""").fetchone()[0]
results['Avg Delivery Duration (Hours)'] = float(r)
print(f"  Avg Delivery Duration (hrs):{float(r):>8.4f}")

r = con.execute("""
    SELECT ROUND(AVG(delivery_time_hours), 4) FROM warehouse.fact_orders 
    WHERE order_status = 'Delivered' AND is_delayed = TRUE;
""").fetchone()[0]
results['Avg Delayed Duration (Hours)'] = float(r)
print(f"  Avg Delayed Duration (hrs): {float(r):>8.4f}")

r = con.execute("""
    SELECT ROUND(AVG(csat_score), 4) FROM warehouse.fact_orders 
    WHERE order_status = 'Delivered' AND csat_score IS NOT NULL;
""").fetchone()[0]
results['Avg CSAT Score'] = float(r)
print(f"  Avg CSAT Score:             {float(r):>8.4f}")

# --- SECTION 3: HUB OPERATIONS ---
print("\n--- 03. HUB OPERATIONS ---")

r = con.execute("SELECT COUNT(DISTINCT hub_key) FROM warehouse.dim_hub;").fetchone()[0]
results['Total Hubs'] = r
print(f"  Total Hubs:                 {r:>8,}")

r = con.execute("SELECT SUM(daily_capacity) FROM warehouse.dim_hub;").fetchone()[0]
results['Network Daily Capacity'] = r
print(f"  Network Daily Capacity:     {r:>8,}")

r = con.execute("""
    SELECT ROUND(AVG(hub_processing_time_hours), 4) FROM warehouse.fact_orders;
""").fetchone()[0]
results['Avg Hub Processing Time (Hours)'] = float(r)
print(f"  Avg Hub Processing Time:    {float(r):>8.4f}")

r = con.execute("SELECT SUM(orders_received) FROM warehouse.fact_hub_hourly;").fetchone()[0]
results['Total Orders Received (Hub)'] = r
print(f"  Total Orders Received (Hub):{r:>8,}")

r = con.execute("SELECT SUM(orders_dispatched) FROM warehouse.fact_hub_hourly;").fetchone()[0]
results['Total Orders Dispatched (Hub)'] = r
print(f"  Total Orders Dispatched:    {r:>8,}")

r = con.execute("SELECT SUM(backlog_volume) FROM warehouse.fact_hub_hourly;").fetchone()[0]
results['Total Backlog Volume'] = r
print(f"  Total Backlog Volume:       {r:>8,}")

# --- SECTION 4: FLEET & MAINTENANCE ---
print("\n--- 04. FLEET & MAINTENANCE ---")

r = con.execute("SELECT COUNT(DISTINCT vehicle_key) FROM warehouse.dim_vehicle;").fetchone()[0]
results['Total Fleet Vehicles'] = r
print(f"  Total Fleet Vehicles:       {r:>8,}")

r = con.execute("SELECT COUNT(*) FROM warehouse.dim_vehicle WHERE current_status = 'Active';").fetchone()[0]
results['Active Vehicles'] = r
print(f"  Active Vehicles:            {r:>8,}")

r = con.execute("SELECT COUNT(*) FROM warehouse.dim_vehicle WHERE current_status = 'Maintenance';").fetchone()[0]
results['Vehicles In Maintenance'] = r
print(f"  Vehicles In Maintenance:    {r:>8,}")

r = round(results['Active Vehicles'] / results['Total Fleet Vehicles'] * 100, 4)
results['Fleet Availability Rate %'] = r
print(f"  Fleet Availability Rate %:  {r:>8.4f}%")

r = con.execute("SELECT COUNT(*) FROM warehouse.dim_vehicle WHERE is_maintenance_alert = TRUE;").fetchone()[0]
results['Maintenance Alert Vehicles'] = r
print(f"  Maintenance Alert Vehicles: {r:>8,}")

r = con.execute("""
    SELECT ROUND(AVG(DATEDIFF('day', purchase_date, DATE '2026-11-18')), 1) 
    FROM warehouse.dim_vehicle;
""").fetchone()[0]
results['Avg Fleet Age (Days)'] = float(r)
print(f"  Avg Fleet Age (Days):       {float(r):>8.1f}")

# Synthetic Maintenance from CSV via DuckDB
r = con.execute("SELECT COUNT(*) FROM read_csv_auto('data/synthetic/synthetic_maintenance.csv');").fetchone()[0]
results['Total Maintenance Events'] = r
print(f"  Total Maintenance Events:   {r:>8,}")

r = con.execute("SELECT ROUND(SUM(cost_usd), 2) FROM read_csv_auto('data/synthetic/synthetic_maintenance.csv');").fetchone()[0]
results['Total Maintenance Expense'] = float(r)
print(f"  Total Maintenance Expense:  ${float(r):>10,.2f}")

r = con.execute("SELECT ROUND(SUM(downtime_hours), 1) FROM read_csv_auto('data/synthetic/synthetic_maintenance.csv') WHERE downtime_hours IS NOT NULL;").fetchone()[0]
results['Total Downtime Hours'] = float(r)
print(f"  Total Downtime Hours:       {float(r):>8.1f}")

# --- SECTION 5: DRIVER METRICS ---
print("\n--- 05. DRIVER METRICS ---")

r = con.execute("SELECT COUNT(DISTINCT driver_key) FROM warehouse.dim_driver;").fetchone()[0]
results['Total Drivers'] = r
print(f"  Total Drivers:              {r:>8,}")

r = con.execute("SELECT ROUND(AVG(experience_years), 2) FROM warehouse.dim_driver;").fetchone()[0]
results['Avg Driver Experience (Years)'] = float(r)
print(f"  Avg Driver Experience (Yrs):{float(r):>8.2f}")

r = con.execute("SELECT ROUND(AVG(performance_rating), 4) FROM warehouse.dim_driver WHERE performance_rating IS NOT NULL;").fetchone()[0]
results['Avg Driver Rating'] = float(r)
print(f"  Avg Driver Rating:          {float(r):>8.4f}")

# --- SECTION 6: PARETO DATA ---
print("\n--- 06. DELAY REASON PARETO (Top 10) ---")
pareto = con.execute("""
    SELECT 
        delay_reason,
        COUNT(*) AS incident_count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER(), 2) AS pct,
        ROUND(100.0 * SUM(COUNT(*)) OVER (ORDER BY COUNT(*) DESC ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) 
              / SUM(COUNT(*)) OVER(), 2) AS cumulative_pct
    FROM warehouse.fact_orders
    WHERE delay_reason IS NOT NULL
    GROUP BY delay_reason
    ORDER BY incident_count DESC;
""").df()
print(pareto.to_string(index=False))
results['Pareto'] = pareto.to_dict('records')

# --- SECTION 7: HUB PERFORMANCE MATRIX ---
print("\n--- 07. HUB PERFORMANCE MATRIX ---")
hub_matrix = con.execute("""
    SELECT 
        h.hub_name,
        h.daily_capacity,
        COUNT(f.order_id) AS total_orders,
        COUNT(*) FILTER (WHERE f.is_delayed = TRUE) AS delayed_orders,
        ROUND(100.0 * COUNT(*) FILTER (WHERE f.is_delayed = TRUE) / COUNT(*), 2) AS delay_rate_pct,
        ROUND(AVG(f.csat_score), 2) AS avg_csat,
        ROUND(AVG(f.hub_processing_time_hours), 2) AS avg_proc_time
    FROM warehouse.fact_orders f
    JOIN warehouse.dim_hub h ON f.hub_key = h.hub_key
    GROUP BY h.hub_name, h.daily_capacity
    ORDER BY total_orders DESC;
""").df()
print(hub_matrix.to_string(index=False))

# --- SECTION 8: VEHICLE TYPE PERFORMANCE ---
print("\n--- 08. VEHICLE TYPE vs DELAY RATE ---")
veh_matrix = con.execute("""
    SELECT 
        v.vehicle_type,
        COUNT(f.order_id) AS total_orders,
        COUNT(*) FILTER (WHERE f.is_delayed = TRUE) AS delayed_orders,
        ROUND(100.0 * COUNT(*) FILTER (WHERE f.is_delayed = TRUE) / COUNT(*), 2) AS delay_rate_pct,
        ROUND(AVG(f.delivery_time_hours) FILTER (WHERE f.is_delayed = TRUE), 2) AS avg_delayed_hrs,
        ROUND(AVG(f.delivery_time_hours) FILTER (WHERE f.is_delayed = FALSE), 2) AS avg_ontime_hrs
    FROM warehouse.fact_orders f
    JOIN warehouse.dim_vehicle v ON f.vehicle_key = v.vehicle_key
    WHERE f.order_status = 'Delivered'
    GROUP BY v.vehicle_type
    ORDER BY delay_rate_pct DESC;
""").df()
print(veh_matrix.to_string(index=False))

# --- SECTION 9: DRIVER PERFORMANCE MATRIX ---
print("\n--- 09. DRIVER PERFORMANCE MATRIX (Top 10 by Orders) ---")
driver_matrix = con.execute("""
    SELECT 
        dr.driver_name,
        dr.employment_type,
        dr.experience_years,
        dr.performance_rating,
        COUNT(f.order_id) AS total_orders,
        COUNT(*) FILTER (WHERE f.is_delayed = TRUE) AS delayed_orders,
        ROUND(100.0 * COUNT(*) FILTER (WHERE f.is_on_time = TRUE) / COUNT(*), 2) AS otd_rate_pct,
        ROUND(AVG(f.delivery_time_hours), 2) AS avg_delivery_hrs
    FROM warehouse.fact_orders f
    JOIN warehouse.dim_driver dr ON f.driver_key = dr.driver_key
    WHERE f.order_status = 'Delivered'
    GROUP BY dr.driver_name, dr.employment_type, dr.experience_years, dr.performance_rating
    HAVING COUNT(f.order_id) >= 10
    ORDER BY total_orders DESC
    LIMIT 10;
""").df()
print(driver_matrix.to_string(index=False))

con.close()
print("\n[STAGE 4 INDEPENDENT VALIDATION COMPLETE]")
print(f"Total verified baselines: {len(results)}")
