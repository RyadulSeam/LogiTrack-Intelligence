import json
from pathlib import Path

test_dir = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test")
report_json_path = test_dir / "LogiTrack_Analytics_Compatibility_Test.Report" / "report.json"

with open(report_json_path, "r", encoding="utf-8") as f:
    rep = json.load(f)

for s_idx, sec in enumerate(rep["sections"]):
    print(f"\n=======================================================")
    print(f"PAGE {s_idx+1}: {sec['displayName']}")
    print(f"Canvas: width={sec.get('width')}, height={sec.get('height')}")
    print(f"=======================================================")
    for v_idx, vc in enumerate(sec["visualContainers"]):
        cfg = json.loads(vc["config"])
        vname = cfg.get("name")
        sv = cfg.get("singleVisual", {})
        vtype = sv.get("visualType")
        x = vc.get("x")
        y = vc.get("y")
        w = vc.get("width")
        h = vc.get("height")
        z = vc.get("z")
        
        proj = sv.get("projections", {})
        proto = sv.get("prototypeQuery", {})
        from_list = proto.get("From", [])
        select_list = proto.get("Select", [])
        
        print(f"\n  Visual [{v_idx:02d}] '{vname}' ({vtype}): pos=({x},{y}), size=({w}x{h}), z={z}")
        print(f"    Projections: {list(proj.keys())}")
        for p_k, p_v in proj.items():
            print(f"      {p_k}: {[item.get('queryRef') for item in p_v]}")
        print(f"    PrototypeQuery From: {[f.get('Entity') for f in from_list]}")
        select_names = [s.get("Name") for s in select_list]
        print(f"    PrototypeQuery Select ({len(select_names)}): {select_names[:4]}")
