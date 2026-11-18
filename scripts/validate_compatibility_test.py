import json
import os
from pathlib import Path

ORIG_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics")
TEST_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test")
DATA_DIR = Path(r"F:\LogiTrack-Intelligence\dashboards\powerbi\data_export")

print("=== CHECK 1: File Existence & Size ===")
for root, dirs, files in os.walk(TEST_DIR):
    for f in files:
        fp = Path(root) / f
        rel = fp.relative_to(TEST_DIR)
        print(f"  {rel} ({fp.stat().st_size} bytes)")

print("\n=== CHECK 2: Model Comparison ===")
with open(ORIG_DIR / "LogiTrack_Analytics.Dataset" / "model.bim", "r", encoding="utf-8") as f:
    orig_bim = json.load(f)
with open(TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.SemanticModel" / "model.bim", "r", encoding="utf-8") as f:
    test_bim = json.load(f)

orig_tables = orig_bim["model"]["tables"]
test_tables = test_bim["model"]["tables"]
print(f"Original tables: {len(orig_tables)} | Test tables: {len(test_tables)}")
assert len(orig_tables) == len(test_tables)

orig_measures = sum(len(t.get("measures", [])) for t in orig_tables)
test_measures = sum(len(t.get("measures", [])) for t in test_tables)
print(f"Original measures: {orig_measures} | Test measures: {test_measures}")
assert orig_measures == test_measures

orig_rels = orig_bim["model"]["relationships"]
test_rels = test_bim["model"]["relationships"]
print(f"Original relationships: {len(orig_rels)} | Test relationships: {len(test_rels)}")
assert len(orig_rels) == len(test_rels)

print("\n=== CHECK 3: CSV Data Sources Verification ===")
for t in test_tables:
    t_name = t["name"]
    for p in t.get("partitions", []):
        expr = p["source"]["expression"]
        if isinstance(expr, list):
            expr_str = " ".join(expr)
        else:
            expr_str = str(expr)
        if "File.Contents" in expr_str:
            import re
            m = re.search(r'File\.Contents\("([^"]+)"\)', expr_str)
            if m:
                path = m.group(1)
                exists = os.path.exists(path)
                print(f"  Table '{t_name}' -> CSV: {path} | Exists: {exists}")
                assert exists

print("\n=== CHECK 4: Report Visuals & Schema Verification ===")
with open(ORIG_DIR / "LogiTrack_Analytics.Report" / "report.json", "r", encoding="utf-8") as f:
    orig_rep = json.load(f)
with open(TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.Report" / "report.json", "r", encoding="utf-8") as f:
    test_rep = json.load(f)

print(f"Original sections: {len(orig_rep['sections'])} | Test sections: {len(test_rep['sections'])}")
assert len(orig_rep["sections"]) == len(test_rep["sections"])

for s_idx, (os_sec, ts_sec) in enumerate(zip(orig_rep["sections"], test_rep["sections"])):
    o_vcs = os_sec["visualContainers"]
    t_vcs = ts_sec["visualContainers"]
    print(f"  Page {s_idx+1}: '{ts_sec['displayName']}' | Original visuals: {len(o_vcs)} | Test visuals: {len(t_vcs)}")
    assert len(o_vcs) == len(t_vcs)
    for v in t_vcs:
        assert "config" in v and isinstance(v["config"], str)
        cfg = json.loads(v["config"])
        assert "singleVisual" in cfg
        assert "visualType" in cfg["singleVisual"]

print("\n=== CHECK 5: Original Project Unaltered ===")
git_status = os.popen("git status -s dashboards/powerbi/LogiTrack_Analytics").read().strip()
print(f"Original directory git modifications: '{git_status}'")
assert git_status == "", "Original project must have no unstaged modifications!"

print("\nALL 5 VALIDATION CHECKS PASSED PERFECTLY!")
