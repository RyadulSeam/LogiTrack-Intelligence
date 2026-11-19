import json
import shutil
from pathlib import Path

TEST_DIR = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test")
REPORT_DIR = TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.Report"
RESOURCES_DIR = REPORT_DIR / "StaticResources" / "RegisteredResources"
THEME_SRC = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Corporate_Theme.json")

print(f"Building Phase 3 Controlled Test for: {REPORT_DIR}")

# 1. Ensure Theme is placed in StaticResources/RegisteredResources/
RESOURCES_DIR.mkdir(parents=True, exist_ok=True)
if THEME_SRC.exists():
    shutil.copy(THEME_SRC, RESOURCES_DIR / "LogiTrack_Corporate_Theme.json")
    print("  Theme copied to RegisteredResources/LogiTrack_Corporate_Theme.json")

# 2. Update definition.pbir to ensure no byConnection: null
pbir_path = REPORT_DIR / "definition.pbir"
pbir_data = {
    "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/1.0.0/schema.json",
    "version": "1.0",
    "datasetReference": {
        "byPath": {
            "path": "../LogiTrack_Analytics_Compatibility_Test.SemanticModel"
        }
    }
}
with open(pbir_path, "w", encoding="utf-8") as f:
    json.dump(pbir_data, f, indent=2)
print("  Updated definition.pbir")

# 3. Helpers for Visuals
def make_textbox(page_pfx, name_slug, x, y, w, h, title, subtitle):
    vname = f"{page_pfx}_textbox_{name_slug}"
    cfg = {
        "name": vname,
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
                                            "value": title,
                                            "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "15pt", "color": "#142B45"}
                                        },
                                        {
                                            "value": f"  |  {subtitle}",
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

def make_slicer(page_pfx, name_slug, x, y, w, h, entity, column, title):
    vname = f"{page_pfx}_slicer_{name_slug}"
    alias = entity[:2].lower()
    cfg = {
        "name": vname,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 200, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": f"{entity}.{column}", "active": True}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": alias, "Entity": entity, "Type": 0}],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": alias}},
                            "Property": column
                        },
                        "Name": f"{entity}.{column}",
                        "NativeReferenceName": column
                    }
                ]
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": f"'{title}'"}}}
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

def make_card(page_pfx, name_slug, x, y, w, h, measure_name, title, callout_color="#142B45"):
    vname = f"{page_pfx}_card_{name_slug}"
    cfg = {
        "name": vname,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 100, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": f"_Measures.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "m", "Entity": "_Measures", "Type": 0}],
                "Select": [
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "m"}},
                            "Property": measure_name
                        },
                        "Name": f"_Measures.{measure_name}",
                        "NativeReferenceName": measure_name
                    }
                ]
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": f"'{title}'"}}}
                        }
                    }
                ],
                "labels": [
                    {
                        "properties": {
                            "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{callout_color}'"}}}}},
                            "fontSize": {"expr": {"Literal": {"Value": "22D"}}}
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

def make_bar_chart(page_pfx, name_slug, x, y, w, h, cat_entity, cat_col, measure_name, title):
    vname = f"{page_pfx}_barchart_{name_slug}"
    cat_alias = cat_entity[:2].lower()
    cfg = {
        "name": vname,
        "layouts": [{"id": 0, "position": {"x": x, "y": y, "z": 30, "width": w, "height": h}}],
        "singleVisual": {
            "visualType": "barChart",
            "projections": {
                "Category": [{"queryRef": f"{cat_entity}.{cat_col}", "active": True}],
                "Y": [{"queryRef": f"_Measures.{measure_name}"}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": cat_alias, "Entity": cat_entity, "Type": 0},
                    {"Name": "m", "Entity": "_Measures", "Type": 0}
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": cat_alias}},
                            "Property": cat_col
                        },
                        "Name": f"{cat_entity}.{cat_col}",
                        "NativeReferenceName": cat_col
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "m"}},
                            "Property": measure_name
                        },
                        "Name": f"_Measures.{measure_name}",
                        "NativeReferenceName": measure_name
                    }
                ]
            },
            "objects": {
                "general": [
                    {
                        "properties": {
                            "title": {"expr": {"Literal": {"Value": f"'{title}'"}}}
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

# 4. Build Sections
# Page 1: Controlled Test (Exact 5 Visuals)
p1_visuals = [
    make_textbox("p1", "header_banner", 20, 10, 800, 48, "LOGITRACK INTELLIGENCE | Executive Logistics Control Tower", "Texas Operations SLA & Fulfillment Monitoring"),
    make_slicer("p1", "dimdate_year", 840, 10, 200, 48, "DimDate", "year", "Filter Operating Year"),
    make_card("p1", "total_orders", 20, 70, 300, 95, "Total Orders", "TOTAL ORDERS", "#142B45"),
    make_card("p1", "on_time_delivery_rate_pct", 340, 70, 300, 95, "On-Time Delivery Rate %", "ON-TIME DELIVERY RATE (OTD %)", "#2E7D5B"),
    make_bar_chart("p1", "volume_by_hub", 20, 180, 620, 500, "DimHub", "hub_name", "Total Orders", "Order Volume by Texas Regional Hub")
]

# Pages 2, 3, 4: Safe Shell Placeholders for Controlled Stage
p2_visuals = [
    make_textbox("p2", "header_banner", 20, 10, 1240, 48, "LOGITRACK INTELLIGENCE | Regional Hub Operations Monitor", "Network Daily Throughput, Capacity & Backlog Analysis")
]
p3_visuals = [
    make_textbox("p3", "header_banner", 20, 10, 1240, 48, "LOGITRACK INTELLIGENCE | Delay & Root-Cause Analytics", "SLA Exceptions, Root-Cause Drivers & Driver Performance")
]
p4_visuals = [
    make_textbox("p4", "header_banner", 20, 10, 1240, 48, "LOGITRACK INTELLIGENCE | Fleet Telematics & Predictive Maintenance", "Vehicle Health, Depots, Downtime & Service Expense")
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

# 5. Build report.json with correct resourcePackages structure
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
                "reportVersionAtImport": "5.50",
                "type": "RegisteredResources"
            }
        }
    }),
    "layoutOptimization": 0,
    "resourcePackages": [
        {
            "name": "RegisteredResources",
            "type": "RegisteredResources",
            "items": [
                {
                    "name": "LogiTrack_Corporate_Theme.json",
                    "path": "LogiTrack_Corporate_Theme.json",
                    "type": "CustomTheme"
                }
            ]
        }
    ],
    "sections": sections
}

report_out = REPORT_DIR / "report.json"
with open(report_out, "w", encoding="utf-8") as f:
    json.dump(report_json_data, f, indent=2)

print(f"\nSuccessfully generated Phase 3 Controlled Test report.json at: {report_out}")
