import json

with open(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test\LogiTrack_Analytics_Compatibility_Test.SemanticModel\model.bim", "r", encoding="utf-8") as f:
    bim = json.load(f)

print("=== RELATIONSHIPS IN MODEL.BIM ===")
for r in bim["model"]["relationships"]:
    print(f"  {r['name']}: {r['fromTable']}[{r['fromColumn']}] -> {r['toTable']}[{r['toColumn']}] (active={r.get('isActive')})")
