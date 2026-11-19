import json
import re
import shutil
from pathlib import Path

BASE_DIR = Path("F:/LogiTrack-Intelligence/dashboards/powerbi")
SOURCE_BACKUP_DIR = BASE_DIR / "LogiTrack_Analytics_Compatibility_Test_Backup"
FINAL_DIR = BASE_DIR / "LogiTrack_Analytics_Final"
THEME_SRC = BASE_DIR / "LogiTrack_Corporate_Theme.json"

print(f"Creating complete final PBIP project at: {FINAL_DIR}")

# Prepare folder structure
FINAL_DIR.mkdir(parents=True, exist_ok=True)
SEMANTIC_DIR = FINAL_DIR / "LogiTrack_Analytics_Final.SemanticModel"
REPORT_DIR = FINAL_DIR / "LogiTrack_Analytics_Final.Report"
RESOURCES_DIR = REPORT_DIR / "StaticResources" / "RegisteredResources"

SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)

# 1. PBIP file
pbip_data = {
    "version": "1.0",
    "artifacts": [
        {
            "report": {
                "path": "LogiTrack_Analytics_Final.Report"
            }
        }
    ],
    "settings": {
        "enableAutoRecovery": True
    }
}
with open(FINAL_DIR / "LogiTrack_Analytics_Final.pbip", "w", encoding="utf-8") as f:
    json.dump(pbip_data, f, indent=2)
print("  Created LogiTrack_Analytics_Final.pbip")

# 2. Semantic model definition.pbism
pbism_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
    "version": "1.0",
    "settings": {}
}
with open(SEMANTIC_DIR / "definition.pbism", "w", encoding="utf-8") as f:
    json.dump(pbism_data, f, indent=2)
print("  Created definition.pbism")

# 3. model.bim (from verified backup, updating model name)
model_bim_src = SOURCE_BACKUP_DIR / "LogiTrack_Analytics_Compatibility_Test.SemanticModel" / "model.bim"
model_data = json.loads(model_bim_src.read_text(encoding="utf-8"))
model_data["name"] = "LogiTrack_Analytics_Final"
with open(SEMANTIC_DIR / "model.bim", "w", encoding="utf-8") as f:
    json.dump(model_data, f, indent=2)
print("  Copied and configured model.bim (9 tables, 37 measures, 9 relationships)")

# 4. definition.pbir (pointing to LogiTrack_Analytics_Final.SemanticModel with byConnection: null)
pbir_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
    "version": "1.0",
    "datasetReference": {
        "byPath": {
            "path": "../LogiTrack_Analytics_Final.SemanticModel"
        },
        "byConnection": None
    }
}
with open(REPORT_DIR / "definition.pbir", "w", encoding="utf-8") as f:
    json.dump(pbir_data, f, indent=2)
print("  Created definition.pbir with byConnection: null")

# 5. Corporate Theme JSON placement
shutil.copy(THEME_SRC, RESOURCES_DIR / "LogiTrack_Corporate_Theme.json")
print("  Placed LogiTrack_Corporate_Theme.json in RegisteredResources")

# Helper functions for VertiPaq Version 2 Schema
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

def make_card_visual(page_pfx, x, y, w, h, measure_name, title_text, callout_color="#142B45"):
    safe_slug = re.sub(r"[^a-z0-9_]+", "_", measure_name.lower())
    safe_name = f"{page_pfx}_card_{safe_slug}".strip("_")
    cfg = {
        "name": safe_name,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": f"_Measures.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "m", "Entity": "_Measures", "Type": 0}],
                "Select": [make_meas_select("m", measure_name)]
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

def make_slicer_visual(page_pfx, x, y, w, h, entity, column_name, title_text):
    alias = make_entity_alias(entity)
    safe_name = f"{page_pfx}_slicer_{entity.lower()}_{column_name.lower()}"
    cfg = {
        "name": safe_name,
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

def make_header_textbox(page_pfx, x, y, w, h, title_text, subtitle_text):
    safe_name = f"{page_pfx}_textbox_header_banner"
    cfg = {
        "name": safe_name,
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

def make_chart_visual(page_pfx, safe_slug, x, y, w, h, visual_type, cat_entity, cat_col, measures_list, title_text, order_col=None):
    from_list = []
    select_list = []
    
    cat_alias = make_entity_alias(cat_entity)
    from_list.append({"Name": cat_alias, "Entity": cat_entity, "Type": 0})
    select_list.append(make_col_select(cat_alias, cat_entity, cat_col))
    
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
        
    vtype_lower = visual_type.lower()
    safe_name = f"{page_pfx}_{vtype_lower}_{safe_slug.lower()}"
    cfg = {
        "name": safe_name,
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

def make_table_visual(page_pfx, safe_slug, x, y, w, h, columns_spec, measures_list, title_text):
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
    safe_name = f"{page_pfx}_table_{safe_slug.lower()}"
    
    cfg = {
        "name": safe_name,
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
# 53 DATA-BOUND VISUALS ACROSS 4 PAGES (ALL IDENTIFIERS STRICTLY ^[a-z0-9_]+$)
# ==============================================================================

# Page 1: Executive Control Tower (14 visuals)
p1_visuals = [
    make_header_textbox("p1", 20, 10, 650, 48, "LOGITRACK INTELLIGENCE | Executive Logistics Control Tower", "High-level Operations SLA & Fulfillment Monitoring"),
    make_slicer_visual("p1", 685, 10, 180, 48, "DimDate", "year", "Filter Year"),
    make_slicer_visual("p1", 880, 10, 190, 48, "DimHub", "hub_name", "Filter Hub"),
    make_slicer_visual("p1", 1085, 10, 175, 48, "FactOrders", "order_status", "Filter Status"),
    
    make_card_visual("p1", 20,  68, 195, 82, "Total Orders", "TOTAL ORDERS", "#142B45"),
    make_card_visual("p1", 225, 68, 195, 82, "Delivered Orders", "FULFILLED ORDERS", "#142B45"),
    make_card_visual("p1", 430, 68, 195, 82, "On-Time Delivery Rate %", "ON-TIME RATE (OTD %)", "#2E7D5B"),
    make_card_visual("p1", 635, 68, 195, 82, "Delay Rate %", "DELAY RATE %", "#C65353"),
    make_card_visual("p1", 840, 68, 195, 82, "Avg Delivery Duration (Hours)", "AVG DURATION (HRS)", "#2F5D8A"),
    make_card_visual("p1", 1045, 68, 215, 82, "Fleet Availability Rate %", "FLEET AVAILABILITY %", "#2E7D5B"),
    
    make_chart_visual("p1", "monthly_volume_trajectory", 20, 160, 780, 265, "columnChart", "DimDate", "month_name", ["Total Orders", "Delivered Orders"], "Monthly Order Volume & Fulfillment Trajectory", "month_number"),
    make_chart_visual("p1", "fulfillment_ratio_donut", 815, 160, 445, 265, "pieChart", "FactOrders", "order_status", ["Total Orders"], "Order Fulfillment vs Cancellation Breakdown"),
    make_chart_visual("p1", "volume_by_hub", 20, 435, 545, 270, "barChart", "DimHub", "hub_name", ["Total Orders"], "Order Volume by Texas Regional Hub"),
    make_table_visual(
        "p1", "hub_operational_summary", 580, 435, 680, 270,
        [("DimHub", "hub_name"), ("DimHub", "city")],
        ["Total Orders", "Delivered Orders", "On-Time Delivery Rate %", "Delay Rate %", "Avg Delivery Duration (Hours)"],
        "Regional Hub Operational Summary & SLA Scorecard"
    )
]

# Page 2: Regional Hub Operations (13 visuals)
p2_visuals = [
    make_header_textbox("p2", 20, 10, 700, 48, "LOGITRACK INTELLIGENCE | Regional Hub Operations Monitor", "Network Daily Throughput, Capacity & Backlog Analysis"),
    make_slicer_visual("p2", 735, 10, 255, 48, "DimHub", "hub_name", "Select Regional Hub"),
    make_slicer_visual("p2", 1005, 10, 255, 48, "DimDate", "year", "Select Operating Year"),
    
    make_card_visual("p2", 20,  68, 195, 82, "Total Hubs", "TOTAL HUBS", "#142B45"),
    make_card_visual("p2", 225, 68, 195, 82, "Network Daily Capacity", "DAILY CAPACITY (PARCELS)", "#2F5D8A"),
    make_card_visual("p2", 430, 68, 195, 82, "Avg Hub Processing Time (Hours)", "AVG PROCESSING TIME", "#2F5D8A"),
    make_card_visual("p2", 635, 68, 195, 82, "Total Orders Received (Hub)", "TOTAL ORDERS RECEIVED", "#142B45"),
    make_card_visual("p2", 840, 68, 195, 82, "Total Orders Dispatched (Hub)", "ORDERS DISPATCHED", "#2E7D5B"),
    make_card_visual("p2", 1045, 68, 215, 82, "Total Backlog Volume", "TOTAL BACKLOG VOLUME", "#C58B2A"),
    
    make_chart_visual("p2", "hub_throughput_ranking", 20, 160, 545, 265, "barChart", "DimHub", "hub_name", ["Total Orders Received (Hub)"], "Hub Throughput Ranking (Orders Received)"),
    make_chart_visual("p2", "hub_capacity_vs_volume", 580, 160, 680, 265, "columnChart", "DimHub", "hub_name", ["Network Daily Capacity", "Total Orders"], "Designed Capacity vs Total Order Volume by Hub"),
    make_chart_visual("p2", "hourly_network_flow", 20, 435, 545, 270, "lineChart", "FactHubHourly", "hour_of_day", ["Total Orders Received (Hub)", "Total Orders Dispatched (Hub)"], "Network Hourly Flow: Received vs Dispatched"),
    make_table_visual(
        "p2", "hub_bottleneck_and_performance", 580, 435, 680, 270,
        [("DimHub", "hub_name"), ("DimHub", "city")],
        ["Network Daily Capacity", "Total Orders Received (Hub)", "Total Orders Dispatched (Hub)", "Total Backlog Volume", "Avg Hub Processing Time (Hours)"],
        "Regional Hub Bottleneck & Processing Performance Matrix"
    )
]

# Page 3: Delay & Root-Cause Analytics (13 visuals)
p3_visuals = [
    make_header_textbox("p3", 20, 10, 650, 48, "LOGITRACK INTELLIGENCE | Delay & Root-Cause Analytics", "SLA Exceptions, Root-Cause Drivers & Driver Performance"),
    make_slicer_visual("p3", 685, 10, 280, 48, "FactOrders", "delay_reason", "Filter Delay Reason"),
    make_slicer_visual("p3", 980, 10, 280, 48, "DimHub", "hub_name", "Filter Operating Hub"),
    
    make_card_visual("p3", 20,  68, 195, 82, "Total Orders", "TOTAL DELIVERIES", "#142B45"),
    make_card_visual("p3", 225, 68, 195, 82, "On-Time Deliveries", "ON-TIME DELIVERIES", "#2E7D5B"),
    make_card_visual("p3", 430, 68, 195, 82, "Delayed Deliveries", "DELAYED DELIVERIES", "#C65353"),
    make_card_visual("p3", 635, 68, 195, 82, "On-Time Delivery Rate %", "ON-TIME RATE %", "#2E7D5B"),
    make_card_visual("p3", 840, 68, 195, 82, "Delay Rate %", "DELAY RATE %", "#C65353"),
    make_card_visual("p3", 1045, 68, 215, 82, "Avg Delayed Duration (Hours)", "AVG DELAY DURATION (HRS)", "#C65353"),
    
    make_chart_visual("p3", "delay_reason_distribution", 20, 160, 650, 265, "barChart", "FactOrders", "delay_reason", ["Delay Incidents by Reason"], "Delivery Delay Root-Cause Distribution (10 Verified Reasons)"),
    make_chart_visual("p3", "delay_rate_by_vehicle_type", 685, 160, 575, 265, "columnChart", "DimVehicle", "vehicle_type", ["Delay Rate %"], "Delivery Delay Rate % by Fleet Vehicle Type"),
    make_table_visual(
        "p3", "driver_performance_scorecard", 20, 435, 650, 270,
        [("DimDriver", "driver_name"), ("DimDriver", "employment_type"), ("DimDriver", "experience_years"), ("DimDriver", "performance_rating")],
        ["Driver Completed Deliveries", "On-Time Delivery Rate %", "Delay Rate %"],
        "Driver Performance Scorecard: Experience & SLA Adherence"
    ),
    make_table_visual(
        "p3", "delay_incident_feed_and_sla", 685, 435, 575, 270,
        [("FactOrders", "order_id"), ("DimHub", "hub_name"), ("FactOrders", "delay_reason")],
        ["Avg Delivery Duration (Hours)", "Delivery SLA Variance (Hours)"],
        "Delay Incident Feed & SLA Breach Details"
    )
]

# Page 4: Fleet Telematics & Predictive Maintenance (13 visuals)
p4_visuals = [
    make_header_textbox("p4", 20, 10, 650, 48, "LOGITRACK INTELLIGENCE | Fleet Telematics & Predictive Maintenance", "Vehicle Health, Depots, Downtime & Service Expense"),
    make_slicer_visual("p4", 685, 10, 280, 48, "DimVehicle", "current_status", "Filter Fleet Status"),
    make_slicer_visual("p4", 980, 10, 280, 48, "DimVehicle", "vehicle_type", "Filter Vehicle Type"),
    
    make_card_visual("p4", 20,  68, 195, 82, "Total Fleet Vehicles", "TOTAL FLEET ASSETS", "#142B45"),
    make_card_visual("p4", 225, 68, 195, 82, "Active Vehicles", "ACTIVE ON-ROAD FLEET", "#2E7D5B"),
    make_card_visual("p4", 430, 68, 195, 82, "Vehicles In Maintenance", "VEHICLES IN DEPOT", "#C58B2A"),
    make_card_visual("p4", 635, 68, 195, 82, "Maintenance Alert Vehicles", "CRITICAL RISK ALERTS", "#C65353"),
    make_card_visual("p4", 840, 68, 195, 82, "Total Maintenance Expense ($)", "MAINTENANCE EXPENSE", "#2F5D8A"),
    make_card_visual("p4", 1045, 68, 215, 82, "Total Downtime Hours", "TOTAL DOWNTIME (HRS)", "#C58B2A"),
    
    make_chart_visual("p4", "fleet_availability_breakdown", 20, 160, 480, 265, "pieChart", "DimVehicle", "current_status", ["Total Fleet Vehicles"], "Fleet Operational Availability Breakdown"),
    make_chart_visual("p4", "maintenance_expense_by_service", 515, 160, 745, 265, "barChart", "FactMaintenance", "service_type", ["Total Maintenance Expense ($)"], "Maintenance Expense ($) by Service Category (source: synthetic)"),
    make_chart_visual("p4", "vehicle_fleet_distribution", 20, 435, 545, 270, "columnChart", "DimVehicle", "vehicle_code", ["Total Fleet Vehicles"], "Vehicle Fleet Asset Distribution"),
    make_table_visual(
        "p4", "high_risk_vehicle_watchlist", 580, 435, 680, 270,
        [("DimVehicle", "vehicle_code"), ("DimVehicle", "vehicle_model"), ("DimVehicle", "vehicle_type"), ("DimVehicle", "current_status"), ("DimVehicle", "lifetime_breakdowns"), ("DimVehicle", "is_maintenance_alert")],
        [],
        "High-Risk Vehicle Fleet Maintenance Action Watchlist"
    )
]

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

# Write report.json using the verified PBIR-Legacy envelope schema
report_json_data = {
    "config": json.dumps({
        "version": "5.50",
        "themeCollection": {
            "baseTheme": {
                "name": "CY24SU10",
                "version": "5.50",
                "type": 2
            },
            "customTheme": {
                "name": "LogiTrack_Corporate_Theme.json",
                "type": 1
            }
        }
    }),
    "layoutOptimization": 0,
    "resourcePackages": [
        {
            "resourcePackage": {
                "name": "RegisteredResources",
                "type": 1,
                "items": [
                    {
                        "name": "LogiTrack_Corporate_Theme.json",
                        "path": "StaticResources/RegisteredResources/LogiTrack_Corporate_Theme.json",
                        "type": 201
                    }
                ]
            }
        }
    ],
    "sections": sections
}

report_out = REPORT_DIR / "report.json"
with open(report_out, "w", encoding="utf-8") as f:
    json.dump(report_json_data, f, indent=2)

print(f"\nSuccessfully generated full 4-page dashboard report.json at: {report_out}")
