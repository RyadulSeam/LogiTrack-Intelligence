import json

with open(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test\LogiTrack_Analytics_Compatibility_Test.Report\report.json", "r", encoding="utf-8") as f:
    rep = json.load(f)

print("=== ALL VISUAL TYPES USED ACROSS PAGES ===")
for s_idx, sec in enumerate(rep["sections"]):
    print(f"\n--- Page {s_idx+1}: {sec['displayName']} ---")
    for v_idx, vc in enumerate(sec["visualContainers"]):
        cfg = json.loads(vc["config"])
        vname = cfg.get("name")
        sv = cfg.get("singleVisual", {})
        vtype = sv.get("visualType")
        print(f"  [{v_idx:02d}] {vtype:<15} : '{vname}'")
