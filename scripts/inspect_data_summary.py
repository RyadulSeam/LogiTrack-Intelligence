import pandas as pd
import glob

data_dir = r"F:\LogiTrack-Intelligence\dashboards\powerbi\data_export"

df_orders = pd.read_csv(f"{data_dir}/FactOrders.csv")
print("FactOrders count:", len(df_orders))
print("order_status values:", df_orders['order_status'].value_counts().to_dict())
print("delay_reason top 5:", df_orders['delay_reason'].value_counts().head(5).to_dict())
print("null delay reasons:", df_orders['delay_reason'].isna().sum())

df_hubs = pd.read_csv(f"{data_dir}/DimHub.csv")
print("\nDimHub count:", len(df_hubs))
print("Hub names:", list(df_hubs['hub_name']))

df_veh = pd.read_csv(f"{data_dir}/DimVehicle.csv")
print("\nDimVehicle count:", len(df_veh))
print("vehicle_type values:", df_veh['vehicle_type'].value_counts().to_dict())
print("current_status values:", df_veh['current_status'].value_counts().to_dict())

df_maint = pd.read_csv(f"{data_dir}/FactMaintenance.csv")
print("\nFactMaintenance count:", len(df_maint))
print("service_type values:", df_maint['service_type'].value_counts().to_dict())
print("maintenance_status values:", df_maint['maintenance_status'].value_counts().to_dict())

df_ml = pd.read_csv(f"{data_dir}/FactMLPredictions.csv")
print("\nFactMLPredictions count:", len(df_ml))
print("model_name:", df_ml['model_name'].value_counts().to_dict())
print("prediction_label:", df_ml['prediction_label'].value_counts().to_dict())
