import json
import os
from pathlib import Path

# Paths
TARGET_REPORT_JSON = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test\LogiTrack_Analytics_Compatibility_Test.Report\report.json")

def make_textbox(x, y, w, h, title_text, tab_order):
    cfg = {
        "name": f"banner_{tab_order}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 10.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "textbox",
            "drillFilterOtherVisuals": True,
            "objects": {
                "general": [{
                    "properties": {
                        "paragraphs": [{
                            "textRuns": [{
                                "value": title_text,
                                "textStyle": {"fontFamily": "Segoe UI Semibold", "fontSize": "16pt", "color": "#142B45"}
                            }]
                        }]
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 10.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_card(x, y, w, h, measure_name, title_text, value_color, tab_order):
    query_ref = f"_Measures.{measure_name}"
    cfg = {
        "name": f"card_{tab_order}_{measure_name.replace(' ', '_').replace('%', 'pct')}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 100.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "card",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "m", "Entity": "_Measures", "Type": 0}],
                "Select": [{
                    "Measure": {
                        "Expression": {"SourceRef": {"Source": "m"}},
                        "Property": measure_name
                    },
                    "Name": query_ref
                }]
            },
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {
                                "Measure": {
                                    "Expression": {"SourceRef": {"Entity": "_Measures"}},
                                    "Property": measure_name
                                }
                            },
                            "queryRef": query_ref,
                            "nativeQueryRef": measure_name
                        }]
                    }
                }
            },
            "objects": {
                "general": [{
                    "properties": {
                        "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }],
                "labels": [{
                    "properties": {
                        "color": {"solid": {"color": {"expr": {"Literal": {"Value": f"'{value_color}'"}}}}},
                        "fontSize": {"expr": {"Literal": {"Value": "24D"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 100.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_slicer(x, y, w, h, entity, property_name, title_text, tab_order):
    query_ref = f"{entity}.{property_name}"
    cfg = {
        "name": f"slicer_{tab_order}_{property_name}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 10.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "slicer",
            "projections": {
                "Values": [{"queryRef": query_ref}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [{"Name": "s", "Entity": entity, "Type": 0}],
                "Select": [{
                    "Column": {
                        "Expression": {"SourceRef": {"Source": "s"}},
                        "Property": property_name
                    },
                    "Name": query_ref
                }]
            },
            "query": {
                "queryState": {
                    "Values": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": entity}},
                                    "Property": property_name
                                }
                            },
                            "queryRef": query_ref,
                            "nativeQueryRef": property_name
                        }]
                    }
                }
            },
            "objects": {
                "general": [{
                    "properties": {
                        "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 10.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_column_chart(x, y, w, h, cat_entity, cat_prop, y_measures, title_text, tab_order):
    cat_qref = f"{cat_entity}.{cat_prop}"
    from_list = [{"Name": "c", "Entity": cat_entity, "Type": 0}]
    select_list = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "c"}},
            "Property": cat_prop
        },
        "Name": cat_qref
    }]
    
    y_proj_list = []
    y_state_list = []
    
    for idx, m_name in enumerate(y_measures):
        m_qref = f"_Measures.{m_name}"
        from_list.append({"Name": f"m{idx}", "Entity": "_Measures", "Type": 0})
        select_list.append({
            "Measure": {
                "Expression": {"SourceRef": {"Source": f"m{idx}"}},
                "Property": m_name
            },
            "Name": m_qref
        })
        y_proj_list.append({"queryRef": m_qref})
        y_state_list.append({
            "field": {
                "Measure": {
                    "Expression": {"SourceRef": {"Entity": "_Measures"}},
                    "Property": m_name
                }
            },
            "queryRef": m_qref,
            "nativeQueryRef": m_name
        })

    cfg = {
        "name": f"col_chart_{tab_order}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "columnChart",
            "projections": {
                "Category": [{"queryRef": cat_qref, "active": True}],
                "Y": y_proj_list
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_list,
                "Select": select_list
            },
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": cat_entity}},
                                    "Property": cat_prop
                                }
                            },
                            "queryRef": cat_qref,
                            "nativeQueryRef": cat_prop,
                            "active": True
                        }]
                    },
                    "Y": {
                        "projections": y_state_list
                    }
                }
            },
            "objects": {
                "general": [{
                    "properties": {
                        "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_bar_chart(x, y, w, h, cat_entity, cat_prop, y_measures, title_text, tab_order):
    cat_qref = f"{cat_entity}.{cat_prop}"
    from_list = [{"Name": "c", "Entity": cat_entity, "Type": 0}]
    select_list = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "c"}},
            "Property": cat_prop
        },
        "Name": cat_qref
    }]
    
    y_proj_list = []
    y_state_list = []
    
    for idx, m_name in enumerate(y_measures):
        m_qref = f"_Measures.{m_name}"
        from_list.append({"Name": f"m{idx}", "Entity": "_Measures", "Type": 0})
        select_list.append({
            "Measure": {
                "Expression": {"SourceRef": {"Source": f"m{idx}"}},
                "Property": m_name
            },
            "Name": m_qref
        })
        y_proj_list.append({"queryRef": m_qref})
        y_state_list.append({
            "field": {
                "Measure": {
                    "Expression": {"SourceRef": {"Entity": "_Measures"}},
                    "Property": m_name
                }
            },
            "queryRef": m_qref,
            "nativeQueryRef": m_name
        })

    cfg = {
        "name": f"bar_chart_{tab_order}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "barChart",
            "projections": {
                "Category": [{"queryRef": cat_qref, "active": True}],
                "Y": y_proj_list
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_list,
                "Select": select_list
            },
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": cat_entity}},
                                    "Property": cat_prop
                                }
                            },
                            "queryRef": cat_qref,
                            "nativeQueryRef": cat_prop,
                            "active": True
                        }]
                    },
                    "Y": {
                        "projections": y_state_list
                    }
                }
            },
            "objects": {
                "general": [{
                    "properties": {
                        "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_pie_chart(x, y, w, h, cat_entity, cat_prop, y_measure, title_text, tab_order):
    cat_qref = f"{cat_entity}.{cat_prop}"
    m_qref = f"_Measures.{y_measure}"

    cfg = {
        "name": f"pie_chart_{tab_order}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "pieChart",
            "projections": {
                "Category": [{"queryRef": cat_qref, "active": True}],
                "Y": [{"queryRef": m_qref}]
            },
            "prototypeQuery": {
                "Version": 2,
                "From": [
                    {"Name": "c", "Entity": cat_entity, "Type": 0},
                    {"Name": "m", "Entity": "_Measures", "Type": 0}
                ],
                "Select": [
                    {
                        "Column": {
                            "Expression": {"SourceRef": {"Source": "c"}},
                            "Property": cat_prop
                        },
                        "Name": cat_qref
                    },
                    {
                        "Measure": {
                            "Expression": {"SourceRef": {"Source": "m"}},
                            "Property": y_measure
                        },
                        "Name": m_qref
                    }
                ]
            },
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": cat_entity}},
                                    "Property": cat_prop
                                }
                            },
                            "queryRef": cat_qref,
                            "nativeQueryRef": cat_prop,
                            "active": True
                        }]
                    },
                    "Y": {
                        "projections": [{
                            "field": {
                                "Measure": {
                                    "Expression": {"SourceRef": {"Entity": "_Measures"}},
                                    "Property": y_measure
                                }
                            },
                            "queryRef": m_qref,
                            "nativeQueryRef": y_measure
                        }]
                    }
                }
            },
            "objects": {
                "general": [{
                    "properties": {
                        "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_line_chart(x, y, w, h, cat_entity, cat_prop, y_measures, title_text, tab_order):
    cat_qref = f"{cat_entity}.{cat_prop}"
    from_list = [{"Name": "c", "Entity": cat_entity, "Type": 0}]
    select_list = [{
        "Column": {
            "Expression": {"SourceRef": {"Source": "c"}},
            "Property": cat_prop
        },
        "Name": cat_qref
    }]
    
    y_proj_list = []
    y_state_list = []
    
    for idx, m_name in enumerate(y_measures):
        m_qref = f"_Measures.{m_name}"
        from_list.append({"Name": f"m{idx}", "Entity": "_Measures", "Type": 0})
        select_list.append({
            "Measure": {
                "Expression": {"SourceRef": {"Source": f"m{idx}"}},
                "Property": m_name
            },
            "Name": m_qref
        })
        y_proj_list.append({"queryRef": m_qref})
        y_state_list.append({
            "field": {
                "Measure": {
                    "Expression": {"SourceRef": {"Entity": "_Measures"}},
                    "Property": m_name
                }
            },
            "queryRef": m_qref,
            "nativeQueryRef": m_name
        })

    cfg = {
        "name": f"line_chart_{tab_order}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "lineChart",
            "projections": {
                "Category": [{"queryRef": cat_qref, "active": True}],
                "Y": y_proj_list
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_list,
                "Select": select_list
            },
            "query": {
                "queryState": {
                    "Category": {
                        "projections": [{
                            "field": {
                                "Column": {
                                    "Expression": {"SourceRef": {"Entity": cat_entity}},
                                    "Property": cat_prop
                                }
                            },
                            "queryRef": cat_qref,
                            "nativeQueryRef": cat_prop,
                            "active": True
                        }]
                    },
                    "Y": {
                        "projections": y_state_list
                    }
                }
            },
            "objects": {
                "general": [{
                    "properties": {
                        "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 20.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

def make_table(x, y, w, h, items, title_text, tab_order):
    from_list = []
    select_list = []
    values_proj_list = []
    values_state_list = []
    
    entities_seen = {}
    for idx, (is_measure, entity, prop) in enumerate(items):
        if entity not in entities_seen:
            alias = f"e{len(entities_seen)}"
            entities_seen[entity] = alias
            from_list.append({"Name": alias, "Entity": entity, "Type": 0})
        else:
            alias = entities_seen[entity]
        
        qref = f"{entity}.{prop}"
        if is_measure:
            select_list.append({
                "Measure": {
                    "Expression": {"SourceRef": {"Source": alias}},
                    "Property": prop
                },
                "Name": qref
            })
            values_state_list.append({
                "field": {
                    "Measure": {
                        "Expression": {"SourceRef": {"Entity": entity}},
                        "Property": prop
                    }
                },
                "queryRef": qref,
                "nativeQueryRef": prop
            })
        else:
            select_list.append({
                "Column": {
                    "Expression": {"SourceRef": {"Source": alias}},
                    "Property": prop
                },
                "Name": qref
            })
            values_state_list.append({
                "field": {
                    "Column": {
                        "Expression": {"SourceRef": {"Entity": entity}},
                        "Property": prop
                    }
                },
                "queryRef": qref,
                "nativeQueryRef": prop
            })
        values_proj_list.append({"queryRef": qref})

    cfg = {
        "name": f"table_{tab_order}",
        "layouts": [{
            "id": 0,
            "position": {"x": float(x), "y": float(y), "z": 30.0, "width": float(w), "height": float(h), "tabOrder": tab_order}
        }],
        "singleVisual": {
            "visualType": "tableEx",
            "projections": {
                "Values": values_proj_list
            },
            "prototypeQuery": {
                "Version": 2,
                "From": from_list,
                "Select": select_list
            },
            "query": {
                "queryState": {
                    "Values": {
                        "projections": values_state_list
                    }
                }
            },
            "objects": {
                "general": [{
                    "properties": {
                        "title": {"expr": {"Literal": {"Value": f"'{title_text}'"}}}
                    }
                }]
            }
        }
    }
    return {
        "x": float(x), "y": float(y), "z": 30.0, "width": float(w), "height": float(h),
        "config": json.dumps(cfg),
        "filters": "[]"
    }

# =============================================================================
# BUILD THE 4 ENTERPRISE PAGES
# =============================================================================

# PAGE 1: EXECUTIVE CONTROL TOWER
p1_vcs = [
    # 0. Title Header
    make_textbox(20, 15, 950, 45, "LOGITRACK INTELLIGENCE | Executive Logistics Control Tower", 0),
    # 1. Hub Slicer
    make_slicer(990, 15, 270, 45, "DimHub", "hub_name", "Select Hub", 1),
    # 2-7. KPI Cards
    make_card(20,   70, 195, 85, "Total Orders", "TOTAL ORDERS", "#142B45", 2),
    make_card(225,  70, 195, 85, "Delivered Orders", "FULFILLED ORDERS", "#142B45", 3),
    make_card(430,  70, 195, 85, "On-Time Delivery Rate %", "ON-TIME RATE (OTD %)", "#2E7D5B", 4),
    make_card(635,  70, 195, 85, "Delay Rate %", "DELAY RATE %", "#C65353", 5),
    make_card(840,  70, 195, 85, "Avg Delivery Duration (Hours)", "AVG DURATION (HRS)", "#2F5D8A", 6),
    make_card(1045, 70, 215, 85, "Fleet Availability Rate %", "FLEET AVAILABILITY %", "#2E7D5B", 7),
    # 8. Monthly Volume & Fulfillment Trend
    make_column_chart(20, 165, 780, 260, "DimDate", "month_name", ["Total Orders", "Delivered Orders"], "Monthly Order Volume & Fulfillment Trajectory", 8),
    # 9. Order Status Split
    make_pie_chart(820, 165, 440, 260, "FactOrders", "order_status", "Total Orders", "Order Status Distribution (Fulfilled vs Cancelled)", 9),
    # 10. Regional Hub Volume Bar Chart
    make_bar_chart(20, 435, 550, 265, "DimHub", "hub_name", ["Total Orders"], "Order Intake Volume by Texas Regional Hub", 10),
    # 11. Executive SLA Summary Matrix Table
    make_table(590, 435, 670, 265, [
        (False, "DimHub", "hub_name"),
        (False, "DimHub", "city"),
        (True, "_Measures", "Total Orders"),
        (True, "_Measures", "Delivered Orders"),
        (True, "_Measures", "On-Time Delivery Rate %"),
        (True, "_Measures", "Delay Rate %")
    ], "Regional Hub Operational Performance & SLA Matrix", 11)
]

# PAGE 2: REGIONAL HUB OPERATIONS
p2_vcs = [
    # 0. Title Header
    make_textbox(20, 15, 950, 45, "LOGITRACK INTELLIGENCE | Regional Hub Operations & Capacity Management", 0),
    # 1. Hub Slicer
    make_slicer(990, 15, 270, 45, "DimHub", "hub_name", "Select Hub", 1),
    # 2-7. KPI Cards
    make_card(20,   70, 195, 85, "Total Hubs", "ACTIVE TEXAS HUBS", "#142B45", 2),
    make_card(225,  70, 195, 85, "Network Daily Capacity", "DAILY CAPACITY (PKGS)", "#142B45", 3),
    make_card(430,  70, 195, 85, "Total Orders Received (Hub)", "TOTAL RECEIVED", "#2F5D8A", 4),
    make_card(635,  70, 195, 85, "Total Orders Dispatched (Hub)", "TOTAL DISPATCHED", "#2E7D5B", 5),
    make_card(840,  70, 195, 85, "Total Backlog Volume", "TOTAL BACKLOG", "#C58B2A", 6),
    make_card(1045, 70, 215, 85, "Avg Hub Processing Time (Hours)", "AVG PROCESSING (HRS)", "#142B45", 7),
    # 8. Capacity vs Processed Volume
    make_column_chart(20, 165, 780, 260, "DimHub", "hub_name", ["Network Daily Capacity", "Total Orders"], "Hub Designed Capacity vs Actual Order Intake", 8),
    # 9. Hub Throughput Ranking
    make_bar_chart(820, 165, 440, 260, "DimHub", "hub_name", ["Delivered Orders"], "Hub Fulfillment Throughput Ranking", 9),
    # 10. 24-Hour Network Rhythm (Line Chart)
    make_line_chart(20, 435, 550, 265, "FactHubHourly", "hour_of_day", ["Total Orders Received (Hub)", "Total Orders Dispatched (Hub)"], "24-Hour Network Rhythm: Hourly Intake vs Dispatch", 10),
    # 11. Hub Detail Performance Matrix Table
    make_table(590, 435, 670, 265, [
        (False, "DimHub", "hub_name"),
        (False, "DimHub", "city"),
        (True, "_Measures", "Network Daily Capacity"),
        (True, "_Measures", "Total Orders Received (Hub)"),
        (True, "_Measures", "Total Orders Dispatched (Hub)"),
        (True, "_Measures", "Total Backlog Volume")
    ], "Regional Hub Intake, Dispatch & Workload Balance", 11)
]

# PAGE 3: DELAY & ROOT-CAUSE ANALYTICS
p3_vcs = [
    # 0. Title Header
    make_textbox(20, 15, 950, 45, "LOGITRACK INTELLIGENCE | Delivery Delay Investigation & Root-Cause Analytics", 0),
    # 1. Hub Slicer
    make_slicer(990, 15, 270, 45, "DimHub", "hub_name", "Select Hub", 1),
    # 2-7. KPI Cards
    make_card(20,   70, 195, 85, "Delayed Deliveries", "LATE DELIVERIES", "#C65353", 2),
    make_card(225,  70, 195, 85, "Delay Rate %", "DELIVERY DELAY RATE %", "#C65353", 3),
    make_card(430,  70, 195, 85, "Avg Delayed Duration (Hours)", "AVG DELAY DURATION", "#C65353", 4),
    make_card(635,  70, 195, 85, "Delivery SLA Variance (Hours)", "SLA VARIANCE (HRS)", "#C58B2A", 5),
    make_card(840,  70, 195, 85, "Delay Incidents by Reason", "CATEGORIZED INCIDENTS", "#2F5D8A", 6),
    make_card(1045, 70, 215, 85, "On-Time Deliveries", "ON-TIME DELIVERIES", "#2E7D5B", 7),
    # 8. Delay Root-Cause Pareto Chart
    make_column_chart(20, 165, 780, 260, "FactOrders", "delay_reason", ["Delay Incidents by Reason"], "Delivery Delay Root-Cause Incident Distribution", 8),
    # 9. Delay Rate by Vehicle Type
    make_bar_chart(820, 165, 440, 260, "DimVehicle", "vehicle_type", ["Delay Rate %"], "Delay Rate % by Fleet Vehicle Type", 9),
    # 10. Driver Deliveries Bar Chart
    make_bar_chart(20, 435, 550, 265, "DimDriver", "driver_name", ["Delivered Orders"], "Top Delivery Drivers by Completed Shipments", 10),
    # 11. ML Delay Risk Inference Feed Table
    make_table(590, 435, 670, 265, [
        (False, "FactMLPredictions", "order_id"),
        (False, "FactMLPredictions", "predicted_label"),
        (False, "FactMLPredictions", "predicted_score"),
        (False, "FactMLPredictions", "model_name"),
        (False, "FactMLPredictions", "prediction_timestamp")
    ], "Machine Learning Delay Risk Inference Feed (Pilot Model)", 11)
]

# PAGE 4: FLEET TELEMATICS & PREDICTIVE MAINTENANCE
p4_vcs = [
    # 0. Title Header
    make_textbox(20, 15, 950, 45, "LOGITRACK INTELLIGENCE | Fleet Telematics, Maintenance & Asset Readiness", 0),
    # 1. Vehicle Type Slicer
    make_slicer(990, 15, 270, 45, "DimVehicle", "vehicle_type", "Filter Vehicle Type", 1),
    # 2-7. KPI Cards
    make_card(20,   70, 195, 85, "Total Fleet Vehicles", "TOTAL FLEET ASSETS", "#142B45", 2),
    make_card(225,  70, 195, 85, "Active Vehicles", "ACTIVE ON-ROAD FLEET", "#2E7D5B", 3),
    make_card(430,  70, 195, 85, "Vehicles In Maintenance", "VEHICLES IN DEPOT", "#C58B2A", 4),
    make_card(635,  70, 195, 85, "Maintenance Alert Vehicles", "CRITICAL RISK ALERTS", "#C65353", 5),
    make_card(840,  70, 195, 85, "Total Maintenance Expense ($)", "TOTAL MAINT. EXPENSE", "#2F5D8A", 6),
    make_card(1045, 70, 215, 85, "Total Downtime Hours", "TOTAL DOWNTIME (HRS)", "#C58B2A", 7),
    # 8. Maintenance Expense by Service Type
    make_column_chart(20, 165, 780, 260, "FactMaintenance", "service_type", ["Total Maintenance Expense ($)"], "Maintenance Expense ($) by Service Category", 8),
    # 9. Fleet Operational Availability Status
    make_pie_chart(820, 165, 440, 260, "DimVehicle", "current_status", "Total Fleet Vehicles", "Fleet Operational Availability Breakdown", 9),
    # 10. Maintenance Events by Service Type
    make_bar_chart(20, 435, 550, 265, "FactMaintenance", "service_type", ["Total Maintenance Events"], "Maintenance Event Frequency by Category", 10),
    # 11. High-Risk Vehicle Action Watchlist Table
    make_table(590, 435, 670, 265, [
        (False, "DimVehicle", "vehicle_code"),
        (False, "DimVehicle", "vehicle_model"),
        (False, "DimVehicle", "vehicle_type"),
        (False, "DimVehicle", "current_status"),
        (False, "DimVehicle", "total_mileage_km"),
        (False, "DimVehicle", "is_maintenance_alert")
    ], "High-Risk Vehicle Fleet Maintenance Action Watchlist", 11)
]

# Assemble Full report.json
report_data = {
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
    "sections": [
        {
            "name": "ReportSection_ExecutiveControlTower",
            "displayName": "Executive Control Tower",
            "ordinal": 0,
            "height": 720.0,
            "width": 1280.0,
            "filters": "[]",
            "visualContainers": p1_vcs
        },
        {
            "name": "ReportSection_RegionalHubOperations",
            "displayName": "Regional Hub Operations",
            "ordinal": 1,
            "height": 720.0,
            "width": 1280.0,
            "filters": "[]",
            "visualContainers": p2_vcs
        },
        {
            "name": "ReportSection_DelayRootCauseAnalytics",
            "displayName": "Delay & Root-Cause Analytics",
            "ordinal": 2,
            "height": 720.0,
            "width": 1280.0,
            "filters": "[]",
            "visualContainers": p3_vcs
        },
        {
            "name": "ReportSection_FleetPredictiveMaintenance",
            "displayName": "Fleet Telematics & Predictive Maintenance",
            "ordinal": 3,
            "height": 720.0,
            "width": 1280.0,
            "filters": "[]",
            "visualContainers": p4_vcs
        }
    ]
}

with open(TARGET_REPORT_JSON, "w", encoding="utf-8") as f:
    json.dump(report_data, f, indent=2)

print("Successfully generated full 4-page dashboard report.json with 48 fully data-bound visuals!")
