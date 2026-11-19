import json
from pathlib import Path

orig_path = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Analytics/LogiTrack_Analytics.Report/report.json")
test_path = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test/LogiTrack_Analytics_Compatibility_Test.Report/report.json")

print("=== ORIGINAL REPORT.JSON ===")
if orig_path.exists():
    orig = json.loads(orig_path.read_text(encoding="utf-8"))
    for i, s in enumerate(orig.get("sections", [])):
        print(f"\nPage {i+1}: {s.get('displayName')}")
        for j, vc in enumerate(s.get("visualContainers", [])):
            v = vc.get("visual", {})
            vtype = v.get("visualType", "UNKNOWN")
            print(f"  [{j+1}] visualType: {vtype}, keys in vc: {list(vc.keys())}, keys in visual: {list(v.keys())}")
else:
    print("Orig path not found")

print("\n=== COMPATIBILITY TEST REPORT.JSON ===")
if test_path.exists():
    test = json.loads(test_path.read_text(encoding="utf-8"))
    for i, s in enumerate(test.get("sections", [])):
        print(f"\nPage {i+1}: {s.get('displayName')}")
        for j, vc in enumerate(s.get("visualContainers", [])):
            cfg_str = vc.get("config", "{}")
            cfg = json.loads(cfg_str) if isinstance(cfg_str, str) else cfg_str
            vtype = cfg.get("singleVisual", {}).get("visualType", "UNKNOWN")
            name = cfg.get("name", "UNNAMED")
            print(f"  [{j+1}] name: {name}, visualType: {vtype}, keys in vc: {list(vc.keys())}")
