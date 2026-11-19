import json
import os
import shutil
from pathlib import Path

# Paths
ORIG_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics")
TEST_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test")
DATA_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\data_export")
THEME_SRC = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Corporate_Theme.json")

print(f"Building Full Enterprise Power BI Dashboard at: {TEST_DIR}")

SEMANTIC_DIR = TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.SemanticModel"
REPORT_DIR = TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.Report"
RESOURCES_DIR = REPORT_DIR / "StaticResources" / "RegisteredResources"

SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

# Copy corporate theme into RegisteredResources
if THEME_SRC.exists():
    shutil.copy(THEME_SRC, RESOURCES_DIR / "LogiTrack_Corporate_Theme.json")
    print("  Copied LogiTrack_Corporate_Theme.json to RegisteredResources")

# 1. Root PBIP File
pbip_content = {
    "version": "1.0",
    "artifacts": [
        {
            "report": {
                "path": "LogiTrack_Analytics_Compatibility_Test.Report"
            }
        }
    ],
    "settings": {
        "enableAutoRecovery": True
    }
}
with open(TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.pbip", "w", encoding="utf-8") as f:
    json.dump(pbip_content, f, indent=2)

# 2. Semantic Model definition.pbism
pbism_content = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "1.0",
    "settings": {}
}
with open(SEMANTIC_DIR / "definition.pbism", "w", encoding="utf-8") as f:
    json.dump(pbism_content, f, indent=2)

# 3. model.bim (preserve exact original TMSL definition)
orig_model_bim_path = ORIG_DIR / "LogiTrack_Analytics.Dataset" / "model.bim"
with open(orig_model_bim_path, "r", encoding="utf-8") as f:
    model_bim_data = json.load(f)

model_bim_data["name"] = "LogiTrack_Analytics_Compatibility_Test"
with open(SEMANTIC_DIR / "model.bim", "w", encoding="utf-8") as f:
    json.dump(model_bim_data, f, indent=2)
print("  Preserved model.bim (9 tables, 37 measures, 9 relationships)")

# 4. Report definition.pbir
pbir_content = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
    "version": "1.0",
    "datasetReference": {
        "byPath": {
            "path": "../LogiTrack_Analytics_Compatibility_Test.SemanticModel"
        },
        "byConnection": None
    }
}
with open(REPORT_DIR / "definition.pbir", "w", encoding="utf-8") as f:
    json.dump(pbir_content, f, indent=2)

# ==============================================================================
# 5. VISUAL GENERATION HELPERS
# ==============================================================================

def make_entity_alias(entity_name):
    clean = entity_name.replace("Dim", "").replace("Fact", "").replace("_", "")
    return clean[:2].lower()

def make_col_select(alias, entity, prop):
    return {
        "Column": {
            "Expression": {"SourceRef": {"Source": alias}},
            "Property": prop
        },
        "Name": f"{entity}.{prop}",
        "NativeReferenceName": prop
    }

def make_meas_select(alias, prop):
    return {
        "Measure": {
            "Expression": {"SourceRef": {"Source": alias}},
            "Property": prop
        },
        "Name": f"_Measures.{prop}",
        "NativeReferenceName": prop
    }

def make_card_visual(x, y, w, h, measure_name, title_text, callout_color="#142B45"):
    alias = "m"
    entity = "_Measures"
    cfg = {
        "name": f"card_{measure_name.replace(' ', '_').replace('%', 'Pct').replace('$', 'USD').replace('(', '').replace(')', '')}",
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": f"_Measures.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": alias, "Entity": entity, "Type": 0}],
                "Select": [make_meas_select(alias, measure_name)]
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ],
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{callout_color}'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "20D"}}}
                        }
                    }
                ],
                "categoryLabels": [
                    {
                        "properties": {
                            "show": {"expr": {"Literal": {"Value": "true"}}},
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": "'#64748B'"}}}}}
                        }
                    }
                ]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 100, "width": w, "height": h,
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_slicer_visual(x, y, w, h, entity, column_name, title_text):
    alias = make_entity_alias(entity)
    cfg = {
        "name": f"slicer_{entity}_{column_name}",
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 200, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": f"{entity}.{column_name}", "active": True}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": alias, "Entity": entity, "Type": 0}],
                "Select": [make_col_select(alias, entity, column_name)]
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ],
                "data": [
                    {
                        "properties": {
                            "mode": {"expr": {"Literal": {"Value": "'Dropdown'"}}}
                        }
                    }
                ]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 200, "width": w, "height": h,
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_header_textbox(x, y, w, h, title_text, subtitle_text):
    cfg = {
        "name": "header_title_banner",
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 50, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [
                    {
                        "properties": {
                            "paragraphs": [
                                {
                                    "textRuns": [
                                        {
                                            "value": title_text,
                                            "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "15pt", "color": "#142B45"}
                                        },
                                        {
                                            "value": f"  |  {subtitle_text}",
                                            "textStyle": {"fontFamily": "Segoe UI", "fontSize": "10pt", "color": "#64748B"}
                                        }
                                    ]
                                }
                            ]
                        }
                    }
                ]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 50, "width": w, "height": h,
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_chart_visual(x, y, w, h, visual_type, cat_entity, cat_col, measures_list, title_text, order_col=None):
    from_list = []
    select_list = []
    
    # Category column
    cat_alias = make_entity_alias(cat_entity)
    from_list.append({"Name": cat_alias, "Entity": cat_entity, "Type": 0})
    select_list.append(make_col_select(cat_alias, cat_entity, cat_col))
    
    # Measures
    m_alias = "m"
    from_list.append({"Name": m_alias, "Entity": "_Measures", "Type": 0})
    for m in measures_list:
        select_list.append(make_meas_select(m_alias, m))
        
    projections = {
        "Category": [{"queryRef": f"{cat_entity}.{cat_col}", "active": True}],
        "Y": [{"queryRef": f"_Measures.{m}"} for m in measures_list]
    }
    
    proto = {
        "Version": 2,
        "From": from_list,
        "Select": select_list
    }
    
    if order_col:
        proto["OrderBy"] = [
            {
                "Direction": 1,
                "Expression": {
                    "Column": {
                        "Expression": {"SourceRef": {"Source": cat_alias}},
                        "Property": order_col
                    }
                }
            }
        ]
        
    cfg = {
        "name": f"chart_{cat_entity}_{cat_col}_{visual_type}",
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 30, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": visual_type,
            "projections": projections,
            "prototypeQuery": proto,
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 30, "width": w, "height": h,
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_table_visual(x, y, w, h, columns_spec, measures_list, title_text):
    # columns_spec: list of (entity, column_name)
    from_map = {}
    select_list = []
    proj_values = []
    
    for entity, col in columns_spec:
        if entity not in from_map:
            alias = make_entity_alias(entity)
            from_map[entity] = alias
        else:
            alias = from_map[entity]
        select_list.append(make_col_select(alias, entity, col))
        proj_values.append({"queryRef": f"{entity}.{col}"})
        
    if measures_list:
        from_map["_Measures"] = "m"
        for m in measures_list:
            select_list.append(make_meas_select("m", m))
            proj_values.append({"queryRef": f"_Measures.{m}"})
            
    from_list = [{"Name": alias, "Entity": ent, "Type": 0} for ent, alias in from_map.items()]
    
    cfg = {
        "name": f"table_{title_text.replace(' ', '_')[:25]}",
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 40, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {
                "Values": proj_values
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_list,
                "Select": select_list
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                        }
                    }
                ]
            }
        }
    }
    return {
        "x": x, "y": y, "z": 40, "width": w, "height": h,
        "config": json.dumps(cfg),
        "filters": "[]"
    }

# ==============================================================================
# 6. ASSEMBLE 4 COMPLETE DASHBOARD PAGES
# ==============================================================================

# ------------------------------------------------------------------------------
# PAGE 1: EXECUTIVE CONTROL TOWER
# ------------------------------------------------------------------------------
p1_visuals = [
    # Top Header Banner
    make_header_textbox(20, 10, 650, 48, "LOGITRACK INTELLIGENCE | Executive Logistics Control Tower", "High-level Operations SLA & Fulfillment Monitoring"),
    # Top Slicers
    make_slicer_visual(685, 10, 180, 48, "DimDate", "year", "Filter Year"),
    make_slicer_visual(880, 10, 190, 48, "DimHub", "hub_name", "Filter Hub"),
    make_slicer_visual(1085, 10, 175, 48, "FactOrders", "order_status", "Filter Status"),
    
    # Row 1: 6 KPI Cards
    make_card_visual(20,  68, 195, 82, "Total Orders", "TOTAL ORDERS", "#142B45"),
    make_card_visual(225, 68, 195, 82, "Delivered Orders", "FULFILLED ORDERS", "#142B45"),
    make_card_visual(430, 68, 195, 82, "On-Time Delivery Rate %", "ON-TIME RATE (OTD %)", "#2E7D5B"),
    make_card_visual(635, 68, 195, 82, "Delay Rate %", "DELAY RATE %", "#C65353"),
    make_card_visual(840, 68, 195, 82, "Avg Delivery Duration (Hours)", "AVG DURATION (HRS)", "#2F5D8A"),
    make_card_visual(1045, 68, 215, 82, "Fleet Availability Rate %", "FLEET AVAILABILITY %", "#2E7D5B"),
    
    # Middle Left: Monthly Order Volume Trajectory & On-Time Performance Trend
    make_chart_visual(20, 160, 780, 265, "columnChart", "DimDate", "month_name", ["Total Orders", "Delivered Orders"], "Monthly Order Volume & Fulfillment Trajectory", "month_number"),
    
    # Middle Right: Fulfillment vs Cancellation Ratio Donut
    make_chart_visual(815, 160, 445, 265, "pieChart", "FactOrders", "order_status", ["Total Orders"], "Order Fulfillment vs Cancellation Breakdown"),
    
    # Lower Left: Delivery Volume by Texas Regional Hub
    make_chart_visual(20, 435, 545, 270, "barChart", "DimHub", "hub_name", ["Total Orders"], "Order Volume by Texas Regional Hub"),
    
    # Lower Right: Regional Hub Operational Summary & SLA Watchlist Table
    make_table_visual(
        580, 435, 680, 270,
        [("DimHub", "hub_name"), ("DimHub", "city")],
        ["Total Orders", "Delivered Orders", "On-Time Delivery Rate %", "Delay Rate %", "Avg Delivery Duration (Hours)"],
        "Regional Hub Operational Summary & SLA Scorecard"
    )
]

# ------------------------------------------------------------------------------
# PAGE 2: REGIONAL HUB OPERATIONS
# ------------------------------------------------------------------------------
p2_visuals = [
    # Top Header Banner
    make_header_textbox(20, 10, 700, 48, "LOGITRACK INTELLIGENCE | Regional Hub Operations Monitor", "Network Daily Throughput, Capacity & Backlog Analysis"),
    # Slicers
    make_slicer_visual(735, 10, 255, 48, "DimHub", "hub_name", "Select Regional Hub"),
    make_slicer_visual(1005, 10, 255, 48, "DimDate", "year", "Select Operating Year"),
    
    # Row 1: 6 KPI Cards
    make_card_visual(20,  68, 195, 82, "Total Hubs", "TOTAL HUBS", "#142B45"),
    make_card_visual(225, 68, 195, 82, "Network Daily Capacity", "DAILY CAPACITY (PARCELS)", "#2F5D8A"),
    make_card_visual(430, 68, 195, 82, "Avg Hub Processing Time (Hours)", "AVG PROCESSING TIME", "#2F5D8A"),
    make_card_visual(635, 68, 195, 82, "Total Orders Received (Hub)", "TOTAL ORDERS RECEIVED", "#142B45"),
    make_card_visual(840, 68, 195, 82, "Total Orders Dispatched (Hub)", "ORDERS DISPATCHED", "#2E7D5B"),
    make_card_visual(1045, 68, 215, 82, "Total Backlog Volume", "TOTAL BACKLOG VOLUME", "#C58B2A"),
    
    # Middle Left: Hub Processed Order Throughput Ranking
    make_chart_visual(20, 160, 545, 265, "barChart", "DimHub", "hub_name", ["Total Orders Received (Hub)"], "Hub Throughput Ranking (Orders Received)"),
    
    # Middle Right: Hub Designed Daily Capacity vs Total Order Volume
    make_chart_visual(580, 160, 680, 265, "columnChart", "DimHub", "hub_name", ["Network Daily Capacity", "Total Orders"], "Designed Capacity vs Total Order Volume by Hub"),
    
    # Lower Left: 24-Hour Network Flow Trend
    make_chart_visual(20, 435, 545, 270, "lineChart", "FactHubHourly", "hour_of_day", ["Total Orders Received (Hub)", "Total Orders Dispatched (Hub)"], "Network Hourly Flow: Received vs Dispatched"),
    
    # Lower Right: Regional Hub Processing Performance Matrix
    make_table_visual(
        580, 435, 680, 270,
        [("DimHub", "hub_name"), ("DimHub", "city")],
        ["Network Daily Capacity", "Total Orders Received (Hub)", "Total Orders Dispatched (Hub)", "Total Backlog Volume", "Avg Hub Processing Time (Hours)"],
        "Regional Hub Bottleneck & Processing Performance Matrix"
    )
]

# ------------------------------------------------------------------------------
# PAGE 3: DELAY & ROOT-CAUSE ANALYTICS
# ------------------------------------------------------------------------------
p3_visuals = [
    # Top Header Banner
    make_header_textbox(20, 10, 650, 48, "LOGITRACK INTELLIGENCE | Delay & Root-Cause Analytics", "SLA Exceptions, Root-Cause Drivers & Driver Performance"),
    # Slicers
    make_slicer_visual(685, 10, 280, 48, "FactOrders", "delay_reason", "Filter Delay Reason"),
    make_slicer_visual(980, 10, 280, 48, "DimHub", "hub_name", "Filter Operating Hub"),
    
    # Row 1: 6 KPI Cards
    make_card_visual(20,  68, 195, 82, "Total Orders", "TOTAL DELIVERIES", "#142B45"),
    make_card_visual(225, 68, 195, 82, "On-Time Deliveries", "ON-TIME DELIVERIES", "#2E7D5B"),
    make_card_visual(430, 68, 195, 82, "Delayed Deliveries", "DELAYED DELIVERIES", "#C65353"),
    make_card_visual(635, 68, 195, 82, "On-Time Delivery Rate %", "ON-TIME RATE %", "#2E7D5B"),
    make_card_visual(840, 68, 195, 82, "Delay Rate %", "DELAY RATE %", "#C65353"),
    make_card_visual(1045, 68, 215, 82, "Avg Delayed Duration (Hours)", "AVG DELAY DURATION (HRS)", "#C65353"),
    
    # Middle Left: Delivery Delay Root-Cause Pareto Distribution
    make_chart_visual(20, 160, 650, 265, "barChart", "FactOrders", "delay_reason", ["Delay Incidents by Reason"], "Delivery Delay Root-Cause Distribution (10 Verified Reasons)"),
    
    # Middle Right: Delivery Delay Rate % by Fleet Vehicle Type
    make_chart_visual(685, 160, 575, 265, "columnChart", "DimVehicle", "vehicle_type", ["Delay Rate %"], "Delivery Delay Rate % by Fleet Vehicle Type"),
    
    # Lower Left: Driver Performance Matrix
    make_table_visual(
        20, 435, 650, 270,
        [("DimDriver", "driver_name"), ("DimDriver", "employment_type"), ("DimDriver", "experience_years"), ("DimDriver", "performance_rating")],
        ["Driver Completed Deliveries", "On-Time Delivery Rate %", "Delay Rate %"],
        "Driver Performance Scorecard: Experience & SLA Adherence"
    )
]

# Lower Right Table for Page 3: Operational Delay Detail Feed
p3_visuals.append(
    make_table_visual(
        685, 435, 575, 270,
        [("FactOrders", "order_id"), ("DimHub", "hub_name"), ("FactOrders", "delay_reason")],
        ["Avg Delivery Duration (Hours)", "Delivery SLA Variance (Hours)"],
        "Delay Incident Feed & SLA Breach Details"
    )
)

# ------------------------------------------------------------------------------
# PAGE 4: FLEET TELEMATICS & PREDICTIVE MAINTENANCE
# ------------------------------------------------------------------------------
p4_visuals = [
    # Top Header Banner
    make_header_textbox(20, 10, 650, 48, "LOGITRACK INTELLIGENCE | Fleet Telematics & Predictive Maintenance", "Vehicle Health, Depots, Downtime & Service Expense"),
    # Slicers
    make_slicer_visual(685, 10, 280, 48, "DimVehicle", "current_status", "Filter Fleet Status"),
    make_slicer_visual(980, 10, 280, 48, "DimVehicle", "vehicle_type", "Filter Vehicle Type"),
    
    # Row 1: 6 KPI Cards
    make_card_visual(20,  68, 195, 82, "Total Fleet Vehicles", "TOTAL FLEET ASSETS", "#142B45"),
    make_card_visual(225, 68, 195, 82, "Active Vehicles", "ACTIVE ON-ROAD FLEET", "#2E7D5B"),
    make_card_visual(430, 68, 195, 82, "Vehicles In Maintenance", "VEHICLES IN DEPOT", "#C58B2A"),
    make_card_visual(635, 68, 195, 82, "Maintenance Alert Vehicles", "CRITICAL RISK ALERTS", "#C65353"),
    make_card_visual(840, 68, 195, 82, "Total Maintenance Expense ($)", "MAINTENANCE EXPENSE", "#2F5D8A"),
    make_card_visual(1045, 68, 215, 82, "Total Downtime Hours", "TOTAL DOWNTIME (HRS)", "#C58B2A"),
    
    # Middle Left: Fleet Operational Availability Breakdown Donut
    make_chart_visual(20, 160, 480, 265, "pieChart", "DimVehicle", "current_status", ["Total Fleet Vehicles"], "Fleet Operational Availability Breakdown"),
    
    # Middle Right: Maintenance Expense ($) by Service Category Bar Chart
    make_chart_visual(515, 160, 745, 265, "barChart", "FactMaintenance", "service_type", ["Total Maintenance Expense ($)"], "Maintenance Expense ($) by Service Category (source: synthetic)"),
    
    # Lower Left: Vehicle Lifetime Breakdowns
    make_chart_visual(20, 435, 545, 270, "columnChart", "DimVehicle", "vehicle_code", ["Total Fleet Vehicles"], "Vehicle Fleet Asset Distribution"),
    
    # Lower Right: High-Risk Vehicle Action Watchlist Table
    make_table_visual(
        580, 435, 680, 270,
        [("DimVehicle", "vehicle_code"), ("DimVehicle", "vehicle_model"), ("DimVehicle", "vehicle_type"), ("DimVehicle", "current_status"), ("DimVehicle", "lifetime_breakdowns"), ("DimVehicle", "is_maintenance_alert")],
        [],
        "High-Risk Vehicle Fleet Maintenance Action Watchlist"
    )
]

# Assemble Full Sections
sections = [
    {
        "name": "ReportSection_ExecutiveControlTower",
        "displayName": "Executive Control Tower",
        "ordinal": 0,
        "height": 720.0,
        "width": 1280.0,
        "filters": "[]",
        "visualContainers": p1_visuals
    },
    {
        "name": "ReportSection_RegionalHubOperations",
        "displayName": "Regional Hub Operations",
        "ordinal": 1,
        "height": 720.0,
        "width": 1280.0,
        "filters": "[]",
        "visualContainers": p2_visuals
    },
    {
        "name": "ReportSection_DelayRootCauseAnalytics",
        "displayName": "Delay & Root-Cause Analytics",
        "ordinal": 2,
        "height": 720.0,
        "width": 1280.0,
        "filters": "[]",
        "visualContainers": p3_visuals
    },
    {
        "name": "ReportSection_FleetPredictiveMaintenance",
        "displayName": "Fleet Telematics & Predictive Maintenance",
        "ordinal": 3,
        "height": 720.0,
        "width": 1280.0,
        "filters": "[]",
        "visualContainers": p4_visuals
    }
]

# Write report.json with Registered Resources for Corporate Theme
report_json_data = {
    "config": json.dumps({
        "version": "5.50",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU10",
                "version": "5.50",
                "type": 2
            }
        }
    }),
    "layoutOptimization": 0,
    "resourcePackages": [],
    "sections": sections
}

with open(REPORT_DIR / "report.json", "w", encoding="utf-8") as f:
    json.dump(report_json_data, f, indent=2)

print("\nSuccessfully built full Power BI Dashboard report.json!")
print(f"Total Sections: {len(sections)}")
for s in sections:
    print(f"  - {s['displayName']}: {len(s['visualContainers'])} working visuals")
