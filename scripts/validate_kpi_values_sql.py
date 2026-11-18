import pandas as pd
import numpy as np

data_dir = r"F:\LogiTrack-Intelligence\dashboards\powerbi\data_export"

df_orders = pd.read_csv(f"{data_dir}/FactOrders.csv")
df_hubs = pd.read_csv(f"{data_dir}/DimHub.csv")
df_drivers = pd.read_csv(f"{data_dir}/DimDriver.csv")
df_vehicles = pd.read_csv(f"{data_dir}/DimVehicle.csv")
df_hourly = pd.read_csv(f"{data_dir}/FactHubHourly.csv")
df_maint = pd.read_csv(f"{data_dir}/FactMaintenance.csv")
df_ml = pd.read_csv(f"{data_dir}/FactMLPredictions.csv")

print("=== 1. EXECUTIVE KPIS (SQL / PANDAS BASELINE) ===")
total_orders = df_orders['order_id'].nunique()
delivered_orders = df_orders[df_orders['order_status'] == 'Delivered']['order_id'].nunique()
cancelled_orders = df_orders[df_orders['order_status'] == 'Cancelled']['order_id'].nunique()
delayed_deliveries = df_orders[(df_orders['order_status'] == 'Delivered') & (df_orders['is_delayed'] == True)]['order_id'].nunique()
ontime_deliveries = df_orders[(df_orders['order_status'] == 'Delivered') & (df_orders['is_delayed'] == False)]['order_id'].nunique()
otd_rate = (ontime_deliveries / delivered_orders) * 100
delay_rate = (delayed_deliveries / delivered_orders) * 100
avg_delivery_duration = df_orders['delivery_time_hours'].mean()

print(f"Total Orders:                  {total_orders:,}")
print(f"Delivered Orders:              {delivered_orders:,}")
print(f"Cancelled Orders:              {cancelled_orders:,}")
print(f"On-Time Deliveries:            {ontime_deliveries:,}")
print(f"Delayed Deliveries:            {delayed_deliveries:,}")
print(f"On-Time Delivery Rate %:       {otd_rate:.2f}%")
print(f"Delay Rate %:                  {delay_rate:.2f}%")
print(f"Avg Delivery Duration (Hours): {avg_delivery_duration:.2f} hrs")

print("\n=== 2. HUB OPERATIONS KPIS ===")
total_hubs = df_hubs['hub_key'].nunique()
network_daily_capacity = df_hubs['daily_capacity'].sum()
total_received = df_hourly['orders_received'].sum()
total_dispatched = df_hourly['orders_dispatched'].sum()
total_backlog = df_hourly['backlog_volume'].sum()
avg_hub_processing = df_orders['hub_processing_time_hours'].mean()

print(f"Total Hubs:                    {total_hubs}")
print(f"Network Daily Capacity:        {network_daily_capacity:,}")
print(f"Total Orders Received (Hub):   {total_received:,}")
print(f"Total Orders Dispatched (Hub): {total_dispatched:,}")
print(f"Total Backlog Volume:          {total_backlog:,}")
print(f"Avg Hub Processing (Hours):    {avg_hub_processing:.2f} hrs")

print("\n=== 3. DELAY & ROOT CAUSE KPIS ===")
avg_delayed_duration = df_orders[(df_orders['order_status'] == 'Delivered') & (df_orders['is_delayed'] == True)]['delivery_time_hours'].mean()
avg_ontime_duration = df_orders[(df_orders['order_status'] == 'Delivered') & (df_orders['is_delayed'] == False)]['delivery_time_hours'].mean()
sla_variance = avg_delayed_duration - avg_ontime_duration
delay_incidents = df_orders['delay_reason'].dropna().count()

print(f"Avg Delayed Duration:          {avg_delayed_duration:.2f} hrs")
print(f"Avg On-Time Duration:          {avg_ontime_duration:.2f} hrs")
print(f"Delivery SLA Variance:         {sla_variance:+.2f} hrs")
print(f"Delay Incidents Categorized:   {delay_incidents:,}")

print("\n=== 4. FLEET & MAINTENANCE KPIS ===")
total_vehicles = df_vehicles['vehicle_key'].nunique()
active_vehicles = df_vehicles[df_vehicles['current_status'] == 'Active']['vehicle_key'].nunique()
in_maint_vehicles = df_vehicles[df_vehicles['current_status'] == 'Maintenance']['vehicle_key'].nunique()
alert_vehicles = df_vehicles[df_vehicles['is_maintenance_alert'] == True]['vehicle_key'].nunique()
fleet_availability = (active_vehicles / total_vehicles) * 100
total_maint_expense = df_maint['cost_usd'].sum()
total_downtime = df_maint['downtime_hours'].sum()
total_maint_events = len(df_maint)

print(f"Total Fleet Vehicles:          {total_vehicles}")
print(f"Active Vehicles:               {active_vehicles}")
print(f"Vehicles In Maintenance:       {in_maint_vehicles}")
print(f"Maintenance Alert Vehicles:    {alert_vehicles}")
print(f"Fleet Availability Rate %:     {fleet_availability:.2f}%")
print(f"Total Maintenance Expense ($): ${total_maint_expense:,.2f}")
print(f"Total Downtime Hours:          {total_downtime:,.1f} hrs")
print(f"Total Maintenance Events:      {total_maint_events:,}")
