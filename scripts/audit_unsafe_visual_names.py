import json
import re

with open(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test\LogiTrack_Analytics_Compatibility_Test.Report\report.json", "r", encoding="utf-8") as f:
    rep = json.load(f)

print("=== AUDIT OF ALL VISUAL NAMES IN REPORT.JSON ===")
unsafe_found = []
for s_idx, sec in enumerate(rep["sections"]):
    print(f"\n--- Section {s_idx+1}: {sec['displayName']} ---")
    for v_idx, vc in enumerate(sec["visualContainers"]):
        cfg = json.loads(vc["config"])
        vname = cfg.get("name", "")
        vtype = cfg.get("singleVisual", {}).get("visualType", "")
        is_safe = bool(re.match(r"^[A-Za-z0-9_]+$", vname))
        if not is_safe:
            unsafe_found.append((sec["displayName"], v_idx, vname, vtype))
            print(f"  [UNSAFE] Visual [{v_idx}]: name='{vname}' (type={vtype})")
        else:
            print(f"  [SAFE] Visual [{v_idx}]: name='{vname}' (type={vtype})")

print(f"\nTotal unsafe visual names found: {len(unsafe_found)}")
for u in unsafe_found:
    print(" ", u)
