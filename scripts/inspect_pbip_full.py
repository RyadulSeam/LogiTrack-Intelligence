import json
import os
import glob
import pandas as pd

base_dir = r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics"
data_export_dir = r"F:\LogiTrack-Intelligence\dashboards\powerbi\data_export"

print("=== 1. PBIP ROOT ===")
pbip_path = os.path.join(base_dir, "LogiTrack_Analytics.pbip")
with open(pbip_path, "r", encoding="utf-8") as f:
    pbip_data = json.load(f)
print(json.dumps(pbip_data, indent=2))

print("\n=== 2. DATASET DEFINITION ===")
pbidataset_path = os.path.join(base_dir, "LogiTrack_Analytics.Dataset", "definition.pbidataset")
with open(pbidataset_path, "r", encoding="utf-8") as f:
    pbidataset_data = json.load(f)
print(json.dumps(pbidataset_data, indent=2))

print("\n=== 3. REPORT DEFINITION ===")
pbir_path = os.path.join(base_dir, "LogiTrack_Analytics.Report", "definition.pbir")
with open(pbir_path, "r", encoding="utf-8") as f:
    pbir_data = json.load(f)
print(json.dumps(pbir_data, indent=2))

print("\n=== 4. MODEL.BIM INSPECTION ===")
model_bim_path = os.path.join(base_dir, "LogiTrack_Analytics.Dataset", "model.bim")
with open(model_bim_path, "r", encoding="utf-8") as f:
    model_bim = json.load(f)

print("Root properties:", list(model_bim.keys()))
print("Compatibility Level:", model_bim.get("compatibilityLevel"))
model = model_bim.get("model", {})
print("Model properties:", list(model.keys()))
print("Culture:", model.get("culture"))
print("Data Access Options:", model.get("dataAccessOptions"))
print("Default PowerBI DataSource Version:", model.get("defaultPowerBIDataSourceVersion"))

tables = model.get("tables", [])
print(f"Total tables: {len(tables)}")
for t in tables:
    t_name = t.get("name")
    cols = t.get("columns", [])
    measures = t.get("measures", [])
    partitions = t.get("partitions", [])
    print(f"\nTable: '{t_name}' | Cols: {len(cols)} | Measures: {len(measures)} | Partitions: {len(partitions)}")
    for p in partitions:
        mode = p.get("mode")
        p_name = p.get("name")
        p_source = p.get("source", {})
        expr = p_source.get("expression", [])
        if isinstance(expr, list):
            expr_str = "\n".join(expr)
        else:
            expr_str = str(expr)
        print(f"  Partition '{p_name}' (mode: {mode}): source type={p_source.get('type')}")
        # print first 2 lines of expr
        first_lines = expr_str.strip().split("\n")[:2]
        print(f"    M expression head: {first_lines}")

relationships = model.get("relationships", [])
print(f"\nTotal relationships: {len(relationships)}")
for r in relationships:
    print(f"  Rel: {r.get('name')} | {r.get('fromTable')}[{r.get('fromColumn')}] -> {r.get('toTable')}[{r.get('toColumn')}] | active={r.get('isActive')}")

print("\n=== 5. CSV DATA SOURCE AUDIT ===")
csv_files = glob.glob(os.path.join(data_export_dir, "*.csv"))
print(f"Found {len(csv_files)} CSV files in {data_export_dir}:")
for cf in csv_files:
    fname = os.path.basename(cf)
    df = pd.read_csv(cf, nrows=2)
    print(f"  {fname}: {len(df.columns)} columns -> {list(df.columns)[:5]}...")

print("\n=== 6. REPORT.JSON INSPECTION ===")
report_json_path = os.path.join(base_dir, "LogiTrack_Analytics.Report", "report.json")
with open(report_json_path, "r", encoding="utf-8") as f:
    report_json = json.load(f)

print("Report.json keys:", list(report_json.keys()))
sections = report_json.get("sections", [])
print(f"Total sections (pages): {len(sections)}")
for s in sections:
    s_name = s.get("name")
    d_name = s.get("displayName")
    vc = s.get("visualContainers", [])
    print(f"  Section: '{d_name}' (name: {s_name}) | Visual containers: {len(vc)}")
