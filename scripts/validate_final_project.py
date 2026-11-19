import json
import re
from pathlib import Path

FINAL_DIR = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Analytics_Final")
MODEL_PATH = FINAL_DIR / "LogiTrack_Analytics_Final.SemanticModel/model.bim"
REPORT_PATH = FINAL_DIR / "LogiTrack_Analytics_Final.Report/report.json"
PBIR_PATH = FINAL_DIR / "LogiTrack_Analytics_Final.Report/definition.pbir"
PBIP_PATH = FINAL_DIR / "LogiTrack_Analytics_Final.pbip"

print(f"=== FULL AUDIT & VALIDATION OF FINAL PROJECT: {FINAL_DIR} ===\n")

# Check PBIP
assert PBIP_PATH.exists(), "PBIP missing"
pbip = json.loads(PBIP_PATH.read_text(encoding="utf-8"))
assert pbip.get("artifacts", [{}])[0].get("report", {}).get("path") == "LogiTrack_Analytics_Final.Report"
print("[PASS] .pbip artifact reference valid.")

# Check PBIR
assert PBIR_PATH.exists(), "definition.pbir missing"
pbir = json.loads(PBIR_PATH.read_text(encoding="utf-8"))
assert pbir.get("datasetReference", {}).get("byPath", {}).get("path") == "../LogiTrack_Analytics_Final.SemanticModel"
assert "byConnection" in pbir.get("datasetReference", {})
assert pbir["datasetReference"]["byConnection"] is None
print("[PASS] definition.pbir references semantic model with byConnection: null.")

# Check Model.bim
assert MODEL_PATH.exists(), "model.bim missing"
model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
tables = {t["name"]: t for t in model["model"]["tables"]}
assert len(tables) == 9, f"Expected 9 tables, found {len(tables)}"
print(f"[PASS] model.bim loaded with {len(tables)} tables.")

measures = set()
for t in tables.values():
    for m in t.get("measures", []):
        measures.add(f"{t['name']}.{m['name']}")
        measures.add(f"_Measures.{m['name']}")
print(f"[PASS] {len(model['model']['tables'][0].get('measures', []))} DAX measures indexed in _Measures table.")

columns = set()
for t in tables.values():
    for c in t.get("columns", []):
        columns.add(f"{t['name']}.{c['name']}")
print(f"[PASS] {len(columns)} physical columns indexed across all 9 tables.")

# Check report.json
assert REPORT_PATH.exists(), "report.json missing"
rep = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

# Check resourcePackages envelope
rp = rep.get("resourcePackages", [])
assert len(rp) == 1, "Expected 1 resourcePackage"
assert "resourcePackage" in rp[0], "Missing resourcePackage envelope"
assert rp[0]["resourcePackage"]["type"] == 1, "resourcePackage.type must be 1 (Int32)"
assert rp[0]["resourcePackage"]["items"][0]["type"] == 201, "item.type must be 201 (Int32)"
print("[PASS] report.json resourcePackages envelope schema verified (type 1, item 201).")

# Check config themeCollection
cfg = json.loads(rep.get("config", "{}"))
assert cfg.get("themeCollection", {}).get("customTheme", {}).get("type") == 1
print("[PASS] report.json customTheme type verified as integer 1.")

# Visual-by-visual audit
total_visuals = 0
unsafe_names = []
broken_refs = []
name_pattern = re.compile(r"^[a-z0-9_]+$")

for s_idx, sec in enumerate(rep.get("sections", [])):
    s_name = sec.get("displayName")
    vcs = sec.get("visualContainers", [])
    print(f"\n--- Section {s_idx+1}: {s_name} ({len(vcs)} visuals) ---")
    for v_idx, vc in enumerate(vcs):
        total_visuals += 1
        c = json.loads(vc.get("config", "{}"))
        vname = c.get("name", "")
        sv = c.get("singleVisual", {})
        vtype = sv.get("visualType", "")
        
        # Check name
        if not name_pattern.match(vname):
            unsafe_names.append((vname, "Doesn't match ^[a-z0-9_]+$"))
            print(f"  [UNSAFE NAME] {vname}")
        else:
            print(f"  [SAFE] [{v_idx+1:02d}] {vname} (type: {vtype})")
            
        # Check references
        proto = sv.get("prototypeQuery", {})
        for sel in proto.get("Select", []):
            ref = sel.get("Name", "")
            if "Measure" in sel:
                if ref not in measures and not any(ref.endswith(f".{m}") for m in measures):
                    broken_refs.append((vname, ref))
            elif "Column" in sel:
                if ref not in columns:
                    broken_refs.append((vname, ref))

print("\n" + "="*80)
print(f"TOTAL VISUALS VALIDATED: {total_visuals}")
print(f"UNSAFE NAMES FOUND: {len(unsafe_names)}")
print(f"BROKEN MODEL REFERENCES FOUND: {len(broken_refs)}")
assert len(unsafe_names) == 0, f"Unsafe names: {unsafe_names}"
assert len(broken_refs) == 0, f"Broken refs: {broken_refs}"
assert total_visuals == 53, f"Expected 53 visuals, got {total_visuals}"
print("=== FINAL ACCEPTANCE AUDIT: 100% PASS ===")
