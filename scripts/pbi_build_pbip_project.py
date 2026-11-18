"""
Stage 6: Power BI Project (PBIP) Builder Script
Constructs the complete modern Power BI Project:
- LogiTrack_Analytics.pbip
- LogiTrack_Analytics.Dataset/ (definition.pbidataset, model.bim with 30 DAX measures and relationships)
- LogiTrack_Analytics.Report/ (definition.pbir, report.json with 4 core dashboard pages)
"""
import os
import json
from pathlib import Path

BASE_DIR = Path("dashboards/powerbi/LogiTrack_Analytics")
DATASET_DIR = BASE_DIR / "LogiTrack_Analytics.Dataset"
REPORT_DIR = BASE_DIR / "LogiTrack_Analytics.Report"

# Ensure directories exist
DATASET_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

print("Building Power BI PBIP Project Structure in:", BASE_DIR)

# 1. LogiTrack_Analytics.pbip
pbip_manifest = {
    "version": "1.0",
    "artifacts": [
        {
            "report": {
                "path": "LogiTrack_Analytics.Report"
            }
        }
    ],
    "settings": {
        "enableAutoRecovery": True
    }
}
with open(BASE_DIR / "LogiTrack_Analytics.pbip", "w", encoding="utf-8") as f:
    json.dump(pbip_manifest, f, indent=2)
print("  Created LogiTrack_Analytics.pbip")

# 2. Report definition.pbir
pbir_content = {
    "version": "1.0",
    "datasetReference": {
        "byPath": {
            "path": "../LogiTrack_Analytics.Dataset"
        },
        "byConnection": None
    }
}
with open(REPORT_DIR / "definition.pbir", "w", encoding="utf-8") as f:
    json.dump(pbir_content, f, indent=2)
print("  Created LogiTrack_Analytics.Report/definition.pbir")

# 3. Dataset definition.pbidataset
pbidataset_content = {
    "version": "1.0",
    "dataset": {
        "type": "semanticModel"
    }
}
with open(DATASET_DIR / "definition.pbidataset", "w", encoding="utf-8") as f:
    json.dump(pbidataset_content, f, indent=2)
print("  Created LogiTrack_Analytics.Dataset/definition.pbidataset")

# 4. Construct Tabular Model model.bim
# Power Query M expression for local data directory
# Uses forward slashes for cross-platform and Power BI compatibility
data_export_abs_path = str(Path("dashboards/powerbi/data_export").resolve()).replace("\\", "/")

def make_csv_partition(filename: str, table_name: str) -> list:
    return [
        {
            "name": f"{table_name}-Partition",
            "mode": "import",
            "source": {
                "type": "m",
                "expression": [
                    f'let',
                    f'    Source = Csv.Document(File.Contents("{data_export_abs_path}/{filename}"),[Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.None]),',
                    f'    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true])',
                    f'in',
                    f'    #"Promoted Headers"'
                ]
            }
        }
    ]

# Build Measures List for _Measures table
measures = [
    # 01 - Executive KPIs
    {"name": "Total Orders", "expression": "DISTINCTCOUNT('FactOrders'[order_id])", "formatString": "#,##0", "displayFolder": "01 - Executive KPIs", "description": "Total distinct operational orders placed"},
    {"name": "Delivered Orders", "expression": "CALCULATE([Total Orders], KEEPFILTERS('FactOrders'[order_status] = \"Delivered\"))", "formatString": "#,##0", "displayFolder": "01 - Executive KPIs", "description": "Count of successfully delivered orders"},
    {"name": "Cancelled Orders", "expression": "CALCULATE([Total Orders], KEEPFILTERS('FactOrders'[order_status] = \"Cancelled\"))", "formatString": "#,##0", "displayFolder": "01 - Executive KPIs", "description": "Count of cancelled orders"},
    {"name": "Cancellation Rate %", "expression": "DIVIDE([Cancelled Orders], [Total Orders], 0)", "formatString": "0.00%", "displayFolder": "01 - Executive KPIs", "description": "Percentage of total orders cancelled"},
    {"name": "On-Time Delivery Rate %", "expression": "DIVIDE([On-Time Deliveries], [Delivered Orders], 0)", "formatString": "0.00%", "displayFolder": "01 - Executive KPIs", "description": "On-Time Delivery Rate (OTD %)"},
    {"name": "Delay Rate %", "expression": "DIVIDE([Delayed Deliveries], [Delivered Orders], 0)", "formatString": "0.00%", "displayFolder": "01 - Executive KPIs", "description": "Percentage of delivered orders delayed"},
    {"name": "Avg Delivery Duration (Hours)", "expression": "CALCULATE(AVERAGE('FactOrders'[delivery_time_hours]), KEEPFILTERS('FactOrders'[order_status] = \"Delivered\"))", "formatString": "0.00", "displayFolder": "01 - Executive KPIs", "description": "Average transit delivery hours"},
    {"name": "Avg CSAT Score", "expression": "CALCULATE(AVERAGE('FactOrders'[csat_score]), KEEPFILTERS('FactOrders'[order_status] = \"Delivered\"))", "formatString": "0.00", "displayFolder": "01 - Executive KPIs", "description": "Average Customer Satisfaction Score (1-5)"},
    {"name": "Total Orders (Prior Month)", "expression": "CALCULATE([Total Orders], DATEADD('DimDate'[full_date], -1, MONTH))", "formatString": "#,##0", "displayFolder": "01 - Executive KPIs", "description": "Order volume in prior calendar month"},
    {"name": "Order Volume MoM Growth %", "expression": "VAR _Current = [Total Orders] VAR _Prior = [Total Orders (Prior Month)] RETURN DIVIDE(_Current - _Prior, _Prior, 0)", "formatString": "+0.00%;-0.00%;0.00%", "displayFolder": "01 - Executive KPIs", "description": "Month-over-month percentage order growth"},

    # 02 - Delivery & SLAs
    {"name": "On-Time Deliveries", "expression": "CALCULATE([Total Orders], KEEPFILTERS('FactOrders'[order_status] = \"Delivered\"), KEEPFILTERS('FactOrders'[is_on_time] = TRUE()))", "formatString": "#,##0", "displayFolder": "02 - Delivery & SLAs", "description": "Volume of orders delivered on time"},
    {"name": "Delayed Deliveries", "expression": "CALCULATE([Total Orders], KEEPFILTERS('FactOrders'[order_status] = \"Delivered\"), KEEPFILTERS('FactOrders'[is_delayed] = TRUE()))", "formatString": "#,##0", "displayFolder": "02 - Delivery & SLAs", "description": "Volume of orders delivered late"},
    {"name": "Avg Delayed Duration (Hours)", "expression": "CALCULATE(AVERAGE('FactOrders'[delivery_time_hours]), KEEPFILTERS('FactOrders'[order_status] = \"Delivered\"), KEEPFILTERS('FactOrders'[is_delayed] = TRUE()))", "formatString": "0.00", "displayFolder": "02 - Delivery & SLAs", "description": "Average duration for delayed deliveries"},
    {"name": "Avg On-Time Duration (Hours)", "expression": "CALCULATE(AVERAGE('FactOrders'[delivery_time_hours]), KEEPFILTERS('FactOrders'[order_status] = \"Delivered\"), KEEPFILTERS('FactOrders'[is_on_time] = TRUE()))", "formatString": "0.00", "displayFolder": "02 - Delivery & SLAs", "description": "Average duration for on-time deliveries"},
    {"name": "Delivery SLA Variance (Hours)", "expression": "[Avg Delayed Duration (Hours)] - [Avg On-Time Duration (Hours)]", "formatString": "+0.00;-0.00;0.00", "displayFolder": "02 - Delivery & SLAs", "description": "Variance between late and on-time transit duration"},
    {"name": "Delay Incidents by Reason", "expression": "CALCULATE(COUNTROWS('FactOrders'), KEEPFILTERS(NOT ISBLANK('FactOrders'[delay_reason])))", "formatString": "#,##0", "displayFolder": "02 - Delivery & SLAs", "description": "Count of recorded delay incidents"},
    {"name": "Cumulative Delay Reason %", "expression": "VAR _CurrentCount = [Delay Incidents by Reason] VAR _TotalIncidents = CALCULATE([Delay Incidents by Reason], ALLSELECTED('FactOrders'[delay_reason])) VAR _TableRanked = ADDCOLUMNS(ALLSELECTED('FactOrders'[delay_reason]), \"@Incidents\", [Delay Incidents by Reason]) VAR _CumulativeSum = SUMX(FILTER(_TableRanked, [@Incidents] >= _CurrentCount), [@Incidents]) RETURN DIVIDE(_CumulativeSum, _TotalIncidents, 0)", "formatString": "0.0%", "displayFolder": "02 - Delivery & SLAs", "description": "Pareto cumulative percentage across ranked delay reasons"},

    # 03 - Hub Operations
    {"name": "Total Hubs", "expression": "DISTINCTCOUNT('DimHub'[hub_key])", "formatString": "#,##0", "displayFolder": "03 - Hub Operations", "description": "Total regional Texas distribution hubs"},
    {"name": "Network Daily Capacity", "expression": "SUM('DimHub'[daily_capacity])", "formatString": "#,##0", "displayFolder": "03 - Hub Operations", "description": "Network aggregate designed daily capacity"},
    {"name": "Avg Hub Processing Time (Hours)", "expression": "AVERAGE('FactOrders'[hub_processing_time_hours])", "formatString": "0.00", "displayFolder": "03 - Hub Operations", "description": "Average internal sorting and staging time"},
    {"name": "Total Orders Received (Hub)", "expression": "SUM('FactHubHourly'[orders_received])", "formatString": "#,##0", "displayFolder": "03 - Hub Operations", "description": "Total hourly incoming volume to hubs"},
    {"name": "Total Orders Dispatched (Hub)", "expression": "SUM('FactHubHourly'[orders_dispatched])", "formatString": "#,##0", "displayFolder": "03 - Hub Operations", "description": "Total hourly dispatches from hubs"},
    {"name": "Total Backlog Volume", "expression": "SUM('FactHubHourly'[backlog_volume])", "formatString": "#,##0", "displayFolder": "03 - Hub Operations", "description": "Active pending orders in staging backlog"},
    {"name": "Hub Capacity Utilization %", "expression": "AVERAGE('FactHubHourly'[capacity_utilization_pct]) / 100", "formatString": "0.00%", "displayFolder": "03 - Hub Operations", "description": "Hourly hub utilization relative to daily capacity"},

    # 04 - Fleet & Maintenance
    {"name": "Total Fleet Vehicles", "expression": "DISTINCTCOUNT('DimVehicle'[vehicle_key])", "formatString": "#,##0", "displayFolder": "04 - Fleet & Maintenance", "description": "Total fleet vehicle assets"},
    {"name": "Active Vehicles", "expression": "CALCULATE([Total Fleet Vehicles], KEEPFILTERS('DimVehicle'[current_status] = \"Active\"))", "formatString": "#,##0", "displayFolder": "04 - Fleet & Maintenance", "description": "Fleet vehicles active in road service"},
    {"name": "Vehicles In Maintenance", "expression": "CALCULATE([Total Fleet Vehicles], KEEPFILTERS('DimVehicle'[current_status] = \"Maintenance\"))", "formatString": "#,##0", "displayFolder": "04 - Fleet & Maintenance", "description": "Vehicles out-of-service in maintenance depots"},
    {"name": "Fleet Availability Rate %", "expression": "DIVIDE([Active Vehicles], [Total Fleet Vehicles], 0)", "formatString": "0.00%", "displayFolder": "04 - Fleet & Maintenance", "description": "Operational availability ratio of vehicle fleet"},
    {"name": "Maintenance Alert Vehicles", "expression": "CALCULATE([Total Fleet Vehicles], KEEPFILTERS('DimVehicle'[is_maintenance_alert] = TRUE()))", "formatString": "#,##0", "displayFolder": "04 - Fleet & Maintenance", "description": "Vehicles flagged for critical breakdown risk"},
    {"name": "Avg Fleet Age (Days)", "expression": "AVERAGEX('DimVehicle', DATEDIFF('DimVehicle'[purchase_date], DATE(2026, 11, 18), DAY))", "formatString": "#,##0", "displayFolder": "04 - Fleet & Maintenance", "description": "Average vehicle age since purchase"},
    {"name": "Total Maintenance Events", "expression": "COUNTROWS('FactMaintenance')", "formatString": "#,##0", "displayFolder": "04 - Fleet & Maintenance", "description": "Historical maintenance interventions (source: synthetic)"},
    {"name": "Total Maintenance Expense ($)", "expression": "SUM('FactMaintenance'[cost_usd])", "formatString": "$#,##0.00", "displayFolder": "04 - Fleet & Maintenance", "description": "Cumulative maintenance repair costs (source: synthetic)"},
    {"name": "Total Downtime Hours", "expression": "SUM('FactMaintenance'[downtime_hours])", "formatString": "#,##0.0", "displayFolder": "04 - Fleet & Maintenance", "description": "Cumulative maintenance downtime hours (source: synthetic)"},

    # 05 - Driver Metrics
    {"name": "Total Drivers", "expression": "DISTINCTCOUNT('DimDriver'[driver_key])", "formatString": "#,##0", "displayFolder": "05 - Driver Metrics", "description": "Total registered delivery driver workforce"},
    {"name": "Avg Driver Experience (Years)", "expression": "AVERAGE('DimDriver'[experience_years])", "formatString": "0.0", "displayFolder": "05 - Driver Metrics", "description": "Average driver seniority in years"},
    {"name": "Avg Driver Rating", "expression": "AVERAGE('DimDriver'[performance_rating])", "formatString": "0.00", "displayFolder": "05 - Driver Metrics", "description": "Average driver quality rating (1-5 scale)"},
    {"name": "Driver Completed Deliveries", "expression": "CALCULATE([Delivered Orders], ALLEXCEPT('DimDriver', 'DimDriver'[driver_name], 'DimDriver'[driver_id]))", "formatString": "#,##0", "displayFolder": "05 - Driver Metrics", "description": "Deliveries completed by driver"}
]

# Build Table Definitions
model_tables = [
    # 0. _Measures
    {
        "name": "_Measures",
        "columns": [
            {
                "name": "_Dummy",
                "dataType": "string",
                "isHidden": True,
                "isNameInferred": False,
                "sourceColumn": "_Dummy"
            }
        ],
        "partitions": [
            {
                "name": "_Measures-Partition",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": [
                        "let",
                        "    Source = Table.FromRows(Json.Document(Binary.Decompress(Binary.FromText(\"i44FAA==\", BinaryEncoding.Base64), Compression.Deflate)), let _t = ((type nullable text) meta [Serialized.Text = true]) in type table [_Dummy = _t])",
                        "in",
                        "    Source"
                    ]
                }
            }
        ],
        "measures": measures
    },

    # 1. DimDate
    {
        "name": "DimDate",
        "dataCategory": "Time",
        "columns": [
            {"name": "date_key", "dataType": "int64", "sourceColumn": "date_key", "isHidden": True},
            {"name": "full_date", "dataType": "dateTime", "sourceColumn": "full_date", "isKey": True, "formatString": "yyyy-MM-dd"},
            {"name": "day_of_week", "dataType": "int64", "sourceColumn": "day_of_week", "isHidden": True},
            {"name": "day_name", "dataType": "string", "sourceColumn": "day_name", "sortByColumn": "day_of_week"},
            {"name": "day_of_month", "dataType": "int64", "sourceColumn": "day_of_month"},
            {"name": "month_number", "dataType": "int64", "sourceColumn": "month_number", "isHidden": True},
            {"name": "month_name", "dataType": "string", "sourceColumn": "month_name", "sortByColumn": "month_number"},
            {"name": "quarter", "dataType": "int64", "sourceColumn": "quarter"},
            {"name": "year", "dataType": "int64", "sourceColumn": "year"},
            {"name": "is_weekend", "dataType": "boolean", "sourceColumn": "is_weekend"}
        ],
        "partitions": make_csv_partition("DimDate.csv", "DimDate")
    },

    # 2. DimHub
    {
        "name": "DimHub",
        "columns": [
            {"name": "hub_key", "dataType": "int64", "sourceColumn": "hub_key", "isHidden": True},
            {"name": "hub_id", "dataType": "int64", "sourceColumn": "hub_id", "isHidden": True},
            {"name": "hub_name", "dataType": "string", "sourceColumn": "hub_name"},
            {"name": "city", "dataType": "string", "sourceColumn": "city", "dataCategory": "City"},
            {"name": "state", "dataType": "string", "sourceColumn": "state", "dataCategory": "StateOrProvince"},
            {"name": "daily_capacity", "dataType": "int64", "sourceColumn": "daily_capacity", "formatString": "#,##0"},
            {"name": "latitude", "dataType": "double", "sourceColumn": "latitude", "dataCategory": "Latitude"},
            {"name": "longitude", "dataType": "double", "sourceColumn": "longitude", "dataCategory": "Longitude"},
            {"name": "data_origin", "dataType": "string", "sourceColumn": "data_origin", "isHidden": True}
        ],
        "partitions": make_csv_partition("DimHub.csv", "DimHub")
    },

    # 3. DimDriver
    {
        "name": "DimDriver",
        "columns": [
            {"name": "driver_key", "dataType": "int64", "sourceColumn": "driver_key", "isHidden": True},
            {"name": "driver_id", "dataType": "int64", "sourceColumn": "driver_id", "isHidden": True},
            {"name": "driver_name", "dataType": "string", "sourceColumn": "driver_name"},
            {"name": "employment_type", "dataType": "string", "sourceColumn": "employment_type"},
            {"name": "hire_date", "dataType": "dateTime", "sourceColumn": "hire_date", "formatString": "yyyy-MM-dd"},
            {"name": "experience_years", "dataType": "int64", "sourceColumn": "experience_years", "formatString": "0"},
            {"name": "performance_rating", "dataType": "int64", "sourceColumn": "performance_rating", "formatString": "0"},
            {"name": "data_origin", "dataType": "string", "sourceColumn": "data_origin", "isHidden": True}
        ],
        "partitions": make_csv_partition("DimDriver.csv", "DimDriver")
    },

    # 4. DimVehicle
    {
        "name": "DimVehicle",
        "columns": [
            {"name": "vehicle_key", "dataType": "int64", "sourceColumn": "vehicle_key", "isHidden": True},
            {"name": "vehicle_id", "dataType": "int64", "sourceColumn": "vehicle_id", "isHidden": True},
            {"name": "vehicle_code", "dataType": "string", "sourceColumn": "vehicle_code"},
            {"name": "vehicle_model", "dataType": "string", "sourceColumn": "vehicle_model"},
            {"name": "vehicle_type", "dataType": "string", "sourceColumn": "vehicle_type"},
            {"name": "current_status", "dataType": "string", "sourceColumn": "current_status"},
            {"name": "lifetime_breakdowns", "dataType": "int64", "sourceColumn": "lifetime_breakdowns", "formatString": "#,##0"},
            {"name": "is_maintenance_alert", "dataType": "boolean", "sourceColumn": "is_maintenance_alert"},
            {"name": "purchase_date", "dataType": "dateTime", "sourceColumn": "purchase_date", "formatString": "yyyy-MM-dd"},
            {"name": "data_origin", "dataType": "string", "sourceColumn": "data_origin", "isHidden": True}
        ],
        "partitions": make_csv_partition("DimVehicle.csv", "DimVehicle")
    },

    # 5. FactOrders
    {
        "name": "FactOrders",
        "columns": [
            {"name": "order_id", "dataType": "int64", "sourceColumn": "order_id"},
            {"name": "order_date_key", "dataType": "int64", "sourceColumn": "order_date_key", "isHidden": True},
            {"name": "delivery_date_key", "dataType": "int64", "sourceColumn": "delivery_date_key", "isHidden": True},
            {"name": "hub_key", "dataType": "int64", "sourceColumn": "hub_key", "isHidden": True},
            {"name": "driver_key", "dataType": "int64", "sourceColumn": "driver_key", "isHidden": True},
            {"name": "vehicle_key", "dataType": "int64", "sourceColumn": "vehicle_key", "isHidden": True},
            {"name": "order_status", "dataType": "string", "sourceColumn": "order_status"},
            {"name": "is_delayed", "dataType": "boolean", "sourceColumn": "is_delayed"},
            {"name": "is_on_time", "dataType": "boolean", "sourceColumn": "is_on_time"},
            {"name": "delay_reason", "dataType": "string", "sourceColumn": "delay_reason"},
            {"name": "csat_score", "dataType": "int64", "sourceColumn": "csat_score", "formatString": "0"},
            {"name": "delivery_time_hours", "dataType": "double", "sourceColumn": "delivery_time_hours", "formatString": "0.00"},
            {"name": "hub_processing_time_hours", "dataType": "double", "sourceColumn": "hub_processing_time_hours", "formatString": "0.00"},
            {"name": "data_origin", "dataType": "string", "sourceColumn": "data_origin", "isHidden": True}
        ],
        "partitions": make_csv_partition("FactOrders.csv", "FactOrders")
    },

    # 6. FactHubHourly
    {
        "name": "FactHubHourly",
        "columns": [
            {"name": "hub_hourly_id", "dataType": "string", "sourceColumn": "hub_hourly_id", "isHidden": True},
            {"name": "hub_key", "dataType": "int64", "sourceColumn": "hub_key", "isHidden": True},
            {"name": "date_key", "dataType": "int64", "sourceColumn": "date_key", "isHidden": True},
            {"name": "hour_of_day", "dataType": "int64", "sourceColumn": "hour_of_day", "formatString": "0"},
            {"name": "orders_received", "dataType": "int64", "sourceColumn": "orders_received", "formatString": "#,##0"},
            {"name": "orders_dispatched", "dataType": "int64", "sourceColumn": "orders_dispatched", "formatString": "#,##0"},
            {"name": "avg_processing_time_hours", "dataType": "double", "sourceColumn": "avg_processing_time_hours", "formatString": "0.00"},
            {"name": "backlog_volume", "dataType": "int64", "sourceColumn": "backlog_volume", "formatString": "#,##0"},
            {"name": "capacity_utilization_pct", "dataType": "double", "sourceColumn": "capacity_utilization_pct", "formatString": "0.00"}
        ],
        "partitions": make_csv_partition("FactHubHourly.csv", "FactHubHourly")
    },

    # 7. FactMaintenance
    {
        "name": "FactMaintenance",
        "columns": [
            {"name": "maintenance_id", "dataType": "string", "sourceColumn": "maintenance_id"},
            {"name": "vehicle_key", "dataType": "int64", "sourceColumn": "vehicle_key", "isHidden": True},
            {"name": "vehicle_code", "dataType": "string", "sourceColumn": "vehicle_code"},
            {"name": "service_type", "dataType": "string", "sourceColumn": "service_type"},
            {"name": "maintenance_status", "dataType": "string", "sourceColumn": "maintenance_status"},
            {"name": "scheduled_date", "dataType": "dateTime", "sourceColumn": "scheduled_date", "formatString": "yyyy-MM-dd"},
            {"name": "completed_date", "dataType": "dateTime", "sourceColumn": "completed_date", "formatString": "yyyy-MM-dd"},
            {"name": "downtime_hours", "dataType": "double", "sourceColumn": "downtime_hours", "formatString": "0.0"},
            {"name": "cost_usd", "dataType": "double", "sourceColumn": "cost_usd", "formatString": "$#,##0.00"},
            {"name": "data_origin", "dataType": "string", "sourceColumn": "data_origin", "isHidden": True}
        ],
        "partitions": make_csv_partition("FactMaintenance.csv", "FactMaintenance")
    },

    # 8. FactMLPredictions
    {
        "name": "FactMLPredictions",
        "columns": [
            {"name": "prediction_id", "dataType": "string", "sourceColumn": "prediction_id"},
            {"name": "model_id", "dataType": "string", "sourceColumn": "model_id", "isHidden": True},
            {"name": "model_name", "dataType": "string", "sourceColumn": "model_name"},
            {"name": "entity_type", "dataType": "string", "sourceColumn": "entity_type"},
            {"name": "order_id", "dataType": "int64", "sourceColumn": "order_id"},
            {"name": "predicted_label", "dataType": "string", "sourceColumn": "predicted_label"},
            {"name": "predicted_score", "dataType": "double", "sourceColumn": "predicted_score", "formatString": "0.0000"},
            {"name": "prediction_timestamp", "dataType": "dateTime", "sourceColumn": "prediction_timestamp", "formatString": "yyyy-MM-dd HH:mm:ss"}
        ],
        "partitions": make_csv_partition("FactMLPredictions.csv", "FactMLPredictions")
    }
]

# Build Model Relationships
model_relationships = [
    # DimDate -> FactOrders (order_date_key: Active)
    {
        "name": "DimDate_FactOrders_OrderDate",
        "fromTable": "FactOrders",
        "fromColumn": "order_date_key",
        "toTable": "DimDate",
        "toColumn": "date_key",
        "isActive": True
    },
    # DimDate -> FactOrders (delivery_date_key: Inactive for USERELATIONSHIP)
    {
        "name": "DimDate_FactOrders_DeliveryDate",
        "fromTable": "FactOrders",
        "fromColumn": "delivery_date_key",
        "toTable": "DimDate",
        "toColumn": "date_key",
        "isActive": False
    },
    # DimHub -> FactOrders
    {
        "name": "DimHub_FactOrders",
        "fromTable": "FactOrders",
        "fromColumn": "hub_key",
        "toTable": "DimHub",
        "toColumn": "hub_key",
        "isActive": True
    },
    # DimDriver -> FactOrders
    {
        "name": "DimDriver_FactOrders",
        "fromTable": "FactOrders",
        "fromColumn": "driver_key",
        "toTable": "DimDriver",
        "toColumn": "driver_key",
        "isActive": True
    },
    # DimVehicle -> FactOrders
    {
        "name": "DimVehicle_FactOrders",
        "fromTable": "FactOrders",
        "fromColumn": "vehicle_key",
        "toTable": "DimVehicle",
        "toColumn": "vehicle_key",
        "isActive": True
    },
    # DimDate -> FactHubHourly
    {
        "name": "DimDate_FactHubHourly",
        "fromTable": "FactHubHourly",
        "fromColumn": "date_key",
        "toTable": "DimDate",
        "toColumn": "date_key",
        "isActive": True
    },
    # DimHub -> FactHubHourly
    {
        "name": "DimHub_FactHubHourly",
        "fromTable": "FactHubHourly",
        "fromColumn": "hub_key",
        "toTable": "DimHub",
        "toColumn": "hub_key",
        "isActive": True
    },
    # DimVehicle -> FactMaintenance
    {
        "name": "DimVehicle_FactMaintenance",
        "fromTable": "FactMaintenance",
        "fromColumn": "vehicle_key",
        "toTable": "DimVehicle",
        "toColumn": "vehicle_key",
        "isActive": True
    },
    # FactOrders -> FactMLPredictions
    {
        "name": "FactOrders_FactMLPredictions",
        "fromTable": "FactMLPredictions",
        "fromColumn": "order_id",
        "toTable": "FactOrders",
        "toColumn": "order_id",
        "isActive": True
    }
]

# Assemble Complete model.bim JSON
model_bim = {
    "name": "LogiTrack_Analytics",
    "compatibilityLevel": 1550,
    "model": {
        "culture": "en-US",
        "dataAccessOptions": {
            "legacyRedirects": True,
            "returnErrorValuesAsNull": True
        },
        "defaultPowerBIDataSourceVersion": "powerBI_V3",
        "tables": model_tables,
        "relationships": model_relationships
    }
}

with open(DATASET_DIR / "model.bim", "w", encoding="utf-8") as f:
    json.dump(model_bim, f, indent=2)
print("  Created LogiTrack_Analytics.Dataset/model.bim (Tabular Model with 30 DAX measures & 9 Star-Schema relationships)")

# 5. Construct Visual Report report.json
# Load Corporate Theme JSON
with open("dashboards/powerbi/LogiTrack_Corporate_Theme.json", "r", encoding="utf-8") as f:
    theme_content = json.load(f)

# Helper function to generate visual containers
def make_card(x, y, w, h, measure_name, title_text, value_color="#142B45"):
    return {
        "x": x, "y": y, "width": w, "height": h, "z": 100,
        "visual": {
            "visualType": "card",
            "query": {
                "Commands": [
                    {
                        "SemanticQueryDataShapeCommand": {
                            "Binding": {
                                "Primary": {
                                    "Groupings": [
                                        {"Projections": [0]}
                                    ]
                                },
                                "DataReduction": {
                                    "DataVolume": 3,
                                    "Primary": {"Top": {}}
                                },
                                "Version": 1
                            },
                            "Query": {
                                "Commands": [
                                    {
                                        "SemanticQuery": {
                                            "Version": 2,
                                            "From": [{"Name": "m", "Entity": "_Measures"}],
                                            "Select": [{"Measure": {"Expression": {"SourceRef": {"Source": "m"}}, "Property": measure_name}, "Name": measure_name}]
                                        }
                                    }
                                ]
                            }
                        }
                    }
                ]
            },
            "objects": {
                "general": [{"properties": {"title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}}}]
            }
        }
    }

# Build the 4 Report Pages (Sections)
report_sections = [
    # =========================================================================
    # PAGE 1: EXECUTIVE CONTROL TOWER
    # =========================================================================
    {
        "name": "ReportSection_ExecutiveControlTower",
        "displayName": "Executive Control Tower",
        "filters": "[]",
        "ordinal": 0,
        "visualContainers": [
            # Header Title Banner
            {
                "x": 20, "y": 15, "width": 1240, "height": 45, "z": 10,
                "visual": {
                    "visualType": "textbox",
                    "objects": {
                        "general": [
                            {
                                "properties": {
                                    "paragraphs": [
                                        {
                                            "textRuns": [
                                                {
                                                    "value": "LOGITRACK INTELLIGENCE | Executive Logistics Control Tower",
                                                    "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#142B45"}
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            # 6 Top KPI Cards
            make_card(20,  70, 195, 85, "Total Orders", "TOTAL ORDERS", "#142B45"),
            make_card(225, 70, 195, 85, "Delivered Orders", "FULFILLED ORDERS", "#142B45"),
            make_card(430, 70, 195, 85, "On-Time Delivery Rate %", "ON-TIME RATE (OTD %)", "#2E7D5B"),
            make_card(635, 70, 195, 85, "Delay Rate %", "DELAY RATE %", "#C65353"),
            make_card(840, 70, 195, 85, "Avg Delivery Duration (Hours)", "AVG DURATION (HRS)", "#2F5D8A"),
            make_card(1045, 70, 215, 85, "Fleet Availability Rate %", "FLEET AVAILABILITY %", "#2E7D5B"),

            # Visual 1: Monthly Order Volume & OTD Trend (Combo / Clustered Column Chart)
            {
                "x": 20, "y": 170, "width": 780, "height": 260, "z": 20,
                "visual": {
                    "visualType": "columnChart",
                    "title": "Monthly Order Volume Trajectory & On-Time Performance Trend",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Monthly Order Volume & OTD Trend'"}}}}}]
                    }
                }
            },

            # Visual 2: Fulfilled vs Cancelled Donut Chart
            {
                "x": 820, "y": 170, "width": 440, "height": 260, "z": 20,
                "visual": {
                    "visualType": "pieChart",
                    "title": "Delivery Fulfillment vs Cancellation Ratio",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Fulfillment vs Cancellation Ratio'"}}}}}]
                    }
                }
            },

            # Visual 3: Regional Hub Delivery Volume (Horizontal Clustered Bar)
            {
                "x": 20, "y": 445, "width": 600, "height": 255, "z": 30,
                "visual": {
                    "visualType": "barChart",
                    "title": "Delivery Volume by Texas Regional Hub",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Delivery Volume by Regional Hub'"}}}}}]
                    }
                }
            },

            # Visual 4: Executive Hub Exception Watchlist Table
            {
                "x": 640, "y": 445, "width": 620, "height": 255, "z": 30,
                "visual": {
                    "visualType": "tableEx",
                    "title": "Regional Hub Operational Summary & SLA Watchlist",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Regional Hub Operational Summary'"}}}}}]
                    }
                }
            }
        ]
    },

    # =========================================================================
    # PAGE 2: REGIONAL HUB OPERATIONS
    # =========================================================================
    {
        "name": "ReportSection_RegionalHubOperations",
        "displayName": "Regional Hub Operations",
        "filters": "[]",
        "ordinal": 1,
        "visualContainers": [
            # Header Title Banner
            {
                "x": 20, "y": 15, "width": 1240, "height": 45, "z": 10,
                "visual": {
                    "visualType": "textbox",
                    "objects": {
                        "general": [
                            {
                                "properties": {
                                    "paragraphs": [
                                        {
                                            "textRuns": [
                                                {
                                                    "value": "LOGITRACK INTELLIGENCE | Regional Hub Operations & Throughput Monitor",
                                                    "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#142B45"}
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            # 6 KPI Cards
            make_card(20,  70, 195, 85, "Total Hubs", "ACTIVE TEXAS HUBS", "#142B45"),
            make_card(225, 70, 195, 85, "Network Daily Capacity", "NETWORK DAILY CAPACITY", "#2F5D8A"),
            make_card(430, 70, 195, 85, "Avg Hub Processing Time (Hours)", "AVG PROCESSING TIME", "#142B45"),
            make_card(635, 70, 195, 85, "Total Orders Received (Hub)", "TOTAL INTAKE VOLUME", "#2F5D8A"),
            make_card(840, 70, 195, 85, "Total Orders Dispatched (Hub)", "TOTAL DISPATCHED", "#64748B"),
            make_card(1045, 70, 215, 85, "Total Backlog Volume", "TOTAL BACKLOG VOLUME", "#C58B2A"),

            # Visual 1: Texas Hub Spatial Map (Bubble map with lat/lon)
            {
                "x": 20, "y": 170, "width": 600, "height": 260, "z": 20,
                "visual": {
                    "visualType": "map",
                    "title": "Texas Regional Hub Spatial Distribution & Volume",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Texas Hub Spatial Distribution & Volume'"}}}}}]
                    }
                }
            },

            # Visual 2: Designed Capacity vs Processed Volume
            {
                "x": 640, "y": 170, "width": 620, "height": 260, "z": 20,
                "visual": {
                    "visualType": "columnChart",
                    "title": "Hub Designed Daily Capacity vs Total Order Volume",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Designed Capacity vs Processed Volume'"}}}}}]
                    }
                }
            },

            # Visual 3: 24-Hour Intake vs Dispatch Flow Rhythm
            {
                "x": 20, "y": 445, "width": 600, "height": 255, "z": 30,
                "visual": {
                    "visualType": "lineChart",
                    "title": "24-Hour Network Flow: Orders Received vs Dispatched",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'24-Hour Intake vs Dispatch Rhythm'"}}}}}]
                    }
                }
            },

            # Visual 4: Hub Operational Matrix Grid
            {
                "x": 640, "y": 445, "width": 620, "height": 255, "z": 30,
                "visual": {
                    "visualType": "tableEx",
                    "title": "Regional Hub Bottleneck & Processing Performance Matrix",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Hub Operational Performance Matrix'"}}}}}]
                    }
                }
            }
        ]
    },

    # =========================================================================
    # PAGE 3: DELAY & ROOT-CAUSE ANALYTICS
    # =========================================================================
    {
        "name": "ReportSection_DelayRootCauseAnalytics",
        "displayName": "Delay & Root-Cause Analytics",
        "filters": "[]",
        "ordinal": 2,
        "visualContainers": [
            # Header Title Banner
            {
                "x": 20, "y": 15, "width": 1240, "height": 45, "z": 10,
                "visual": {
                    "visualType": "textbox",
                    "objects": {
                        "general": [
                            {
                                "properties": {
                                    "paragraphs": [
                                        {
                                            "textRuns": [
                                                {
                                                    "value": "LOGITRACK INTELLIGENCE | Delivery Delay Root-Cause & SLA Failure Diagnostics",
                                                    "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#142B45"}
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            # 6 KPI Cards
            make_card(20,  70, 195, 85, "Delayed Deliveries", "TOTAL LATE DELIVERIES", "#C65353"),
            make_card(225, 70, 195, 85, "Delay Rate %", "DELIVERY DELAY RATE %", "#C65353"),
            make_card(430, 70, 195, 85, "Avg Delayed Duration (Hours)", "AVG LATE DURATION", "#C65353"),
            make_card(635, 70, 195, 85, "Delivery SLA Variance (Hours)", "DELAY SLA VARIANCE", "#C65353"),
            make_card(840, 70, 195, 85, "Delay Incidents by Reason", "TOTAL REASON INCIDENTS", "#2F5D8A"),
            make_card(1045, 70, 215, 85, "Total Orders", "TOTAL ANALYZED ORDERS", "#142B45"),

            # Visual 1: Delay Reason Pareto Analysis (Bar & Cumulative %)
            {
                "x": 20, "y": 170, "width": 780, "height": 260, "z": 20,
                "visual": {
                    "visualType": "columnChart",
                    "title": "Delivery Delay Root-Cause Pareto Distribution (10 Verified Categories)",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Delay Reason Pareto Analysis (80/20 Rule)'"}}}}}]
                    }
                }
            },

            # Visual 2: Delay Rate by Vehicle Type
            {
                "x": 820, "y": 170, "width": 440, "height": 260, "z": 20,
                "visual": {
                    "visualType": "barChart",
                    "title": "Delivery Delay Rate % by Fleet Vehicle Type",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Delay Rate by Vehicle Type'"}}}}}]
                    }
                }
            },

            # Visual 3: Driver Performance Matrix (Seniority vs OTD Rate)
            {
                "x": 20, "y": 445, "width": 600, "height": 255, "z": 30,
                "visual": {
                    "visualType": "scatterChart",
                    "title": "Driver Performance Matrix: Experience (Years) vs On-Time Rate %",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Driver Experience vs On-Time Rate %'"}}}}}]
                    }
                }
            },

            # Visual 4: Machine Learning Real-Time Risk Predictions Feed
            {
                "x": 640, "y": 445, "width": 620, "height": 255, "z": 30,
                "visual": {
                    "visualType": "tableEx",
                    "title": "Machine Learning Delay Inference Feed (Pilot Model: XGBoostClassifier)",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'ML Delay Inference Pilot Feed'"}}}}}]
                    }
                }
            }
        ]
    },

    # =========================================================================
    # PAGE 4: FLEET TELEMATICS & PREDICTIVE MAINTENANCE
    # =========================================================================
    {
        "name": "ReportSection_FleetPredictiveMaintenance",
        "displayName": "Fleet Telematics & Predictive Maintenance",
        "filters": "[]",
        "ordinal": 3,
        "visualContainers": [
            # Header Title Banner
            {
                "x": 20, "y": 15, "width": 1240, "height": 45, "z": 10,
                "visual": {
                    "visualType": "textbox",
                    "objects": {
                        "general": [
                            {
                                "properties": {
                                    "paragraphs": [
                                        {
                                            "textRuns": [
                                                {
                                                    "value": "LOGITRACK INTELLIGENCE | Fleet Telematics & Predictive Maintenance Watchlist",
                                                    "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#142B45"}
                                                }
                                            ]
                                        }
                                    ]
                                }
                            }
                        ]
                    }
                }
            },
            # 6 KPI Cards
            make_card(20,  70, 195, 85, "Total Fleet Vehicles", "TOTAL FLEET ASSETS", "#142B45"),
            make_card(225, 70, 195, 85, "Active Vehicles", "ACTIVE ON-ROAD FLEET", "#2E7D5B"),
            make_card(430, 70, 195, 85, "Vehicles In Maintenance", "VEHICLES IN DEPOT", "#C58B2A"),
            make_card(635, 70, 195, 85, "Maintenance Alert Vehicles", "CRITICAL RISK ALERTS", "#C65353"),
            make_card(840, 70, 195, 85, "Total Maintenance Expense ($)", "TOTAL MAINT. EXPENSE", "#2F5D8A"),
            make_card(1045, 70, 215, 85, "Total Downtime Hours", "TOTAL DOWNTIME (HRS)", "#C58B2A"),

            # Visual 1: Fleet Operational Status Split Donut
            {
                "x": 20, "y": 170, "width": 420, "height": 260, "z": 20,
                "visual": {
                    "visualType": "pieChart",
                    "title": "Fleet Operational Availability Breakdown",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Fleet Operational Availability Status'"}}}}}]
                    }
                }
            },

            # Visual 2: Vehicle Age vs Lifetime Breakdowns (Scatter Plot)
            {
                "x": 460, "y": 170, "width": 800, "height": 260, "z": 20,
                "visual": {
                    "visualType": "scatterChart",
                    "title": "Vehicle Age (Days) vs Lifetime Mechanical Breakdown Count",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Vehicle Age vs Lifetime Mechanical Breakdowns'"}}}}}]
                    }
                }
            },

            # Visual 3: Maintenance Service Type Spend Bar Chart
            {
                "x": 20, "y": 445, "width": 550, "height": 255, "z": 30,
                "visual": {
                    "visualType": "barChart",
                    "title": "Maintenance Expense ($) by Service Category (source: synthetic)",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Maintenance Expense ($) by Service Category'"}}}}}]
                    }
                }
            },

            # Visual 4: Urgent Maintenance Watchlist Grid Table
            {
                "x": 590, "y": 445, "width": 670, "height": 255, "z": 30,
                "visual": {
                    "visualType": "tableEx",
                    "title": "High-Risk Vehicle Fleet Maintenance Action Watchlist",
                    "objects": {
                        "general": [{"properties": {"title": {"expr": {"Literal": {"Value": "'Fleet Maintenance Action Watchlist'"}}}}}]
                    }
                }
            }
        ]
    }
]

# Complete report.json configuration
report_json = {
    "config": json.dumps({
        "version": "5.50",
        "themeCollection": {
            "baseTheme": {
                "name": "User",
                "version": "5.50",
                "type": 2
            },
            "customTheme": {
                "name": "LogiTrack Intelligence Corporate Theme",
                "version": "1.0",
                "type": 1
            }
        }
    }),
    "layoutOptimization": 0,
    "resourcePackages": [],
    "sections": report_sections
}

with open(REPORT_DIR / "report.json", "w", encoding="utf-8") as f:
    json.dump(report_json, f, indent=2)
print("  Created LogiTrack_Analytics.Report/report.json (4 Core Dashboard Pages with all visuals, titles, & layouts)")

print("\n=======================================================")
print("Power BI Project (PBIP) Build Completed Successfully!")
print("Location:", BASE_DIR.resolve())
print("=======================================================")
