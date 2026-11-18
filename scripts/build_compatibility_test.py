import json
import os
import shutil
from pathlib import Path

# Paths
ORIG_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics")
TEST_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test")
DATA_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\data_export")

print(f"Creating compatibility test directory at: {TEST_DIR}")
if TEST_DIR.exists():
    shutil.rmtree(TEST_DIR)

SEMANTIC_DIR = TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.SemanticModel"
REPORT_DIR = TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.Report"

SEMANTIC_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

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

# Update database name to match test project
model_bim_data["name"] = "LogiTrack_Analytics_Compatibility_Test"

with open(SEMANTIC_DIR / "model.bim", "w", encoding="utf-8") as f:
    json.dump(model_bim_data, f, indent=2)

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

# 5. Convert visual containers into standard Power BI report.json schema
orig_report_json_path = ORIG_DIR / "LogiTrack_Analytics.Report" / "report.json"
with open(orig_report_json_path, "r", encoding="utf-8") as f:
    orig_report_data = json.load(f)

new_sections = []
for sec_idx, sec in enumerate(orig_report_data.get("sections", [])):
    sec_name = sec.get("name", f"ReportSection{sec_idx}")
    display_name = sec.get("displayName", f"Page {sec_idx+1}")
    ordinal = sec.get("ordinal", sec_idx)
    
    new_vcs = []
    for v_idx, vc in enumerate(sec.get("visualContainers", [])):
        x = float(vc.get("x", 0))
        y = float(vc.get("y", 0))
        w = float(vc.get("width", 200))
        h = float(vc.get("height", 100))
        z = float(vc.get("z", 10))
        
        vis = vc.get("visual", {})
        vtype = vis.get("visualType", "card")
        vis_title = vis.get("title")
        
        v_name = f"vis_{sec_name}_{v_idx}_{vtype}"
        
        # Build singleVisual object
        single_visual = {
            "visualType": vtype
        }
        
        # If textbox
        if vtype == "textbox":
            single_visual["drillFilterOtherVisuals"] = True
            if "objects" in vis:
                single_visual["objects"] = vis["objects"]
        elif vtype == "card":
            # Check if query is in vis
            if "query" in vis:
                cmd = vis["query"].get("Commands", [{}])[0].get("SemanticQueryDataShapeCommand", {})
                sq = cmd.get("Query", {}).get("Commands", [{}])[0].get("SemanticQuery", {})
                selects = sq.get("Select", [])
                if selects:
                    meas_name = selects[0].get("Name")
                    single_visual["projections"] = {
                        "Values": [{"queryRef": f"_Measures.{meas_name}"}]
                    }
                    single_visual["prototypeQuery"] = {
                        "Version": 2,
                        "From": [{"Name": "m", "Entity": "_Measures", "Type": 0}],
                        "Select": [
                            {
                                "Measure": {
                                    "Expression": {"SourceRef": {"Source": "m"}},
                                    "Property": meas_name
                                },
                                "Name": f"_Measures.{meas_name}"
                            }
                        ]
                    }
            if "objects" in vis:
                single_visual["objects"] = vis["objects"]
        else:
            # Chart or Table visual
            if "objects" in vis:
                single_visual["objects"] = vis["objects"]
            elif vis_title:
                single_visual["objects"] = {
                    "general": [
                        {
                            "properties": {
                                "title": {
                                    "expr": {
                                        "Literal": {
                                            "Value": f"'{vis_title}'"
                                        }
                                    }
                                }
                            }
                        }
                    ]
                }
        
        config_obj = {
            "name": v_name,
            "layouts": [
                {
                    "id": 0,
                    "position": {
                        "x": x,
                        "y": y,
                        "z": z,
                        "width": w,
                        "height": h
                    }
                }
            ],
            "singleVisual": single_visual
        }
        
        new_vcs.append({
            "x": x,
            "y": y,
            "z": z,
            "width": w,
            "height": h,
            "config": json.dumps(config_obj),
            "filters": "[]"
        })
    
    new_sections.append({
        "name": sec_name,
        "displayName": display_name,
        "ordinal": ordinal,
        "height": 720.0,
        "width": 1280.0,
        "filters": "[]",
        "visualContainers": new_vcs
    })

# Write report.json using Microsoft standard baseTheme CY24SU10
new_report_json = {
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
    "sections": new_sections
}

with open(REPORT_DIR / "report.json", "w", encoding="utf-8") as f:
    json.dump(new_report_json, f, indent=2)

print("Generated LogiTrack_Analytics_Compatibility_Test successfully!")
