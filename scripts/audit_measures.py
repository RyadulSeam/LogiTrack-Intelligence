import json

model_bim_path = r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test\LogiTrack_Analytics_Compatibility_Test.SemanticModel\model.bim"

with open(model_bim_path, "r", encoding="utf-8") as f:
    d = json.load(f)

for t in d["model"]["tables"]:
    if t["name"] == "_Measures":
        for i, m in enumerate(t["measures"]):
            print(f"[{i+1}] {m['name']} (Folder: {m.get('displayFolder')})")
            print(f"    Format: {m.get('formatString')}")
            print(f"    DAX: {m.get('expression')}")
