import json
from pathlib import Path

backup_dir = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test_Backup")
curr_dir = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test")

print("=== COMPARING BACKUP (WHICH OPENED) VS CURRENT (WHICH CRASHED WITH 'SOMETHING WENT WRONG') ===\n")

# 1. Compare pbip
b_pbip = (backup_dir / "LogiTrack_Analytics_Compatibility_Test.pbip").read_text(encoding="utf-8")
c_pbip = (curr_dir / "LogiTrack_Analytics_Compatibility_Test.pbip").read_text(encoding="utf-8")
print(f"1. .pbip identical: {b_pbip == c_pbip}")

# 2. Compare definition.pbism
b_pbism = (backup_dir / "LogiTrack_Analytics_Compatibility_Test.SemanticModel/definition.pbism").read_text(encoding="utf-8")
c_pbism = (curr_dir / "LogiTrack_Analytics_Compatibility_Test.SemanticModel/definition.pbism").read_text(encoding="utf-8")
print(f"2. definition.pbism identical: {b_pbism == c_pbism}")

# 3. Compare model.bim
b_bim = (backup_dir / "LogiTrack_Analytics_Compatibility_Test.SemanticModel/model.bim").read_text(encoding="utf-8")
c_bim = (curr_dir / "LogiTrack_Analytics_Compatibility_Test.SemanticModel/model.bim").read_text(encoding="utf-8")
print(f"3. model.bim identical: {b_bim == c_bim}")

# 4. Compare definition.pbir
b_pbir = (backup_dir / "LogiTrack_Analytics_Compatibility_Test.Report/definition.pbir").read_text(encoding="utf-8")
c_pbir = (curr_dir / "LogiTrack_Analytics_Compatibility_Test.Report/definition.pbir").read_text(encoding="utf-8")
print(f"4. definition.pbir identical: {b_pbir == c_pbir}")
if b_pbir != c_pbir:
    print("   Backup definition.pbir:")
    print("   " + b_pbir.replace("\n", "\n   "))
    print("   Current definition.pbir:")
    print("   " + c_pbir.replace("\n", "\n   "))

# 5. Compare report.json top-level properties
b_rep = json.loads((backup_dir / "LogiTrack_Analytics_Compatibility_Test.Report/report.json").read_text(encoding="utf-8"))
c_rep = json.loads((curr_dir / "LogiTrack_Analytics_Compatibility_Test.Report/report.json").read_text(encoding="utf-8"))

print("\n5. report.json top-level comparison:")
print("   Backup config:", b_rep.get("config"))
print("   Current config:", c_rep.get("config"))
print("   Backup resourcePackages:", json.dumps(b_rep.get("resourcePackages")))
print("   Current resourcePackages:", json.dumps(c_rep.get("resourcePackages")))

print("\n6. Sections and visuals comparison:")
print(f"   Backup sections: {len(b_rep.get('sections', []))}")
for i, s in enumerate(b_rep.get("sections", [])):
    print(f"     Section {i}: {s.get('displayName')} ({len(s.get('visualContainers', []))} visuals)")

print(f"   Current sections: {len(c_rep.get('sections', []))}")
for i, s in enumerate(c_rep.get("sections", [])):
    print(f"     Section {i}: {s.get('displayName')} ({len(s.get('visualContainers', []))} visuals)")
