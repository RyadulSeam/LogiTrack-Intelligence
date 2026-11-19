import json
from pathlib import Path
import re

TEST_DIR = Path("F:/LogiTrack-Intelligence/dashboards/powerbi/LogiTrack_Analytics_Compatibility_Test")
MODEL_PATH = TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.SemanticModel" / "model.bim"
REPORT_PATH = TEST_DIR / "LogiTrack_Analytics_Compatibility_Test.Report" / "report.json"

model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
report = json.loads(REPORT_PATH.read_text(encoding="utf-8"))

# Index model tables, columns, and measures
model_tables = set()
model_cols = set()
model_meas = set()

for t in model["model"]["tables"]:
    t_name = t["name"]
    model_tables.add(t_name)
    for c in t.get("columns", []):
        model_cols.add(f"{t_name}.{c['name']}")
    for m in t.get("measures", []):
        model_meas.add(f"{t_name}.{m['name']}")
        model_meas.add(f"_Measures.{m['name']}")

# Supported visual types in PBI Desktop October 2026
SUPPORTED_TYPES = {
    "textbox", "slicer", "card", "barChart", "columnChart", "clusteredColumnChart",
    "lineChart", "pieChart", "donutChart", "tableEx", "pivotTable", "map"
}

diagnostic_rows = []

for s_idx, sec in enumerate(report.get("sections", [])):
    sec_name = sec.get("displayName", f"Section {s_idx+1}")
    for v_idx, vc in enumerate(sec.get("visualContainers", [])):
        cfg_raw = vc.get("config", "{}")
        try:
            cfg = json.loads(cfg_raw) if isinstance(cfg_raw, str) else cfg_raw
            cfg_valid = True
        except Exception as e:
            cfg = {}
            cfg_valid = False
            
        sv = cfg.get("singleVisual", {})
        vtype = sv.get("visualType", "UNKNOWN")
        vname = cfg.get("name", f"unnamed_{s_idx}_{v_idx}")
        
        name_safe = bool(re.match(r"^[A-Za-z0-9_]+$", vname))
        type_supported = vtype in SUPPORTED_TYPES
        
        # Projections & query validation
        proj = sv.get("projections", {})
        proto = sv.get("prototypeQuery", {})
        
        has_query = bool(proto.get("Select") or vtype == "textbox")
        has_proj = bool(proj or vtype == "textbox")
        
        # Check references
        refs_valid = True
        broken_refs = []
        
        if proto.get("Select"):
            for sel in proto["Select"]:
                ref_name = sel.get("Name", "")
                if "Measure" in sel:
                    if ref_name not in model_meas and not any(ref_name.endswith(f".{m}") for m in model_meas):
                        refs_valid = False
                        broken_refs.append(ref_name)
                elif "Column" in sel:
                    if ref_name not in model_cols:
                        refs_valid = False
                        broken_refs.append(ref_name)
                        
        status = "VALID"
        issues = []
        if not cfg_valid:
            issues.append("Malformed config JSON")
        if not name_safe:
            issues.append(f"Unsafe name '{vname}'")
        if not type_supported:
            issues.append(f"Unsupported visualType '{vtype}'")
        if not has_query:
            issues.append("Missing prototypeQuery")
        if not has_proj:
            issues.append("Missing projections")
        if not refs_valid:
            issues.append(f"Broken model refs: {broken_refs}")
            
        # Specific known compatibility notes
        if vtype == "columnChart":
            issues.append("Uses columnChart (stacked) instead of clusteredColumnChart")
            
        if issues:
            status = "NEEDS_ATTENTION: " + "; ".join(issues)
            
        diagnostic_rows.append({
            "page": sec_name,
            "visual_index": v_idx + 1,
            "visual_name": vname,
            "visual_type": vtype,
            "has_query": has_query,
            "has_proj": has_proj,
            "refs_valid": refs_valid,
            "name_safe": name_safe,
            "status": status
        })

print(f"Total Visuals Audited: {len(diagnostic_rows)}")
print(f"Pages: {len(report.get('sections', []))}")
issues_count = sum(1 for r in diagnostic_rows if "NEEDS_ATTENTION" in r["status"])
print(f"Visuals with compatibility notes/issues: {issues_count}")

# Save detailed diagnostic table to markdown
out_md = Path("F:/LogiTrack-Intelligence/docs/pbi/visual_diagnostic_audit_table.md")
out_md.parent.mkdir(parents=True, exist_ok=True)

with open(out_md, "w", encoding="utf-8") as f:
    f.write("# Visual Diagnostic Audit Table (Phase 1)\n\n")
    f.write(f"Total visuals audited: **{len(diagnostic_rows)}** across **{len(report.get('sections', []))}** pages.\n\n")
    f.write("| # | Page | Visual Name | Type | Query | Projections | Model Refs | Safe ID | Status / Notes |\n")
    f.write("|---|---|---|---|---|---|---|---|---|\n")
    for i, r in enumerate(diagnostic_rows):
        f.write(f"| {i+1} | {r['page']} | `{r['visual_name']}` | `{r['visual_type']}` | {'Yes' if r['has_query'] else 'No'} | {'Yes' if r['has_proj'] else 'No'} | {'Valid' if r['refs_valid'] else 'BROKEN'} | {'Yes' if r['name_safe'] else 'NO'} | {r['status']} |\n")

print(f"Diagnostic audit report written to: {out_md}")
