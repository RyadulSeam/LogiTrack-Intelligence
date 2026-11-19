import json
import os
from pathlib import Path

test_dir = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test")
report_json_path = test_dir / "LogiTrack_Analytics_Compatibility_Test.Report" / "report.json"
model_bim_path = test_dir / "LogiTrack_Analytics_Compatibility_Test.SemanticModel" / "model.bim"

with open(report_json_path, "r", encoding="utf-8") as f:
    report_data = json.load(f)

print(f"Report config: {report_data.get('config')}")
print(f"Total sections: {len(report_data.get('sections', []))}")

for sec in report_data.get('sections', []):
    print(f"\n--- Section: {sec.get('displayName')} ({sec.get('name')}) ---")
    print(f"Dimensions: {sec.get('width')} x {sec.get('height')}")
    vcs = sec.get('visualContainers', [])
    print(f"Total visual containers: {len(vcs)}")
    for idx, vc in enumerate(vcs):
        cfg = json.loads(vc.get('config', '{}'))
        sv = cfg.get('singleVisual', {})
        vtype = sv.get('visualType')
        proj = sv.get('projections')
        proto = sv.get('prototypeQuery')
        objs = sv.get('objects')
        print(f"  Visual [{idx}]: type={vtype}, name={cfg.get('name')}")
        print(f"    has projections: {bool(proj)}, has prototypeQuery: {bool(proto)}, has objects: {bool(objs)}")
        if proj:
            print(f"    projections: {proj}")
        if vtype == 'textbox':
            print(f"    textbox objects: {objs}")

with open(model_bim_path, "r", encoding="utf-8") as f:
    model_data = json.load(f)

print(f"\n--- Semantic Model: {model_data.get('name')} ---")
tables = model_data.get('model', {}).get('tables', [])
print(f"Total tables: {len(tables)}")
for t in tables:
    meas = t.get('measures', [])
    cols = t.get('columns', [])
    print(f"Table '{t.get('name')}': {len(cols)} cols, {len(meas)} measures")
    if meas:
        print(f"  Measures ({len(meas)}): {[m.get('name') for m in meas]}")
