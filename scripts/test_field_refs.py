import json

with open(r"F:\LogiTrack-Intelligence\dashboards\powerbi\LogiTrack_Analytics_Compatibility_Test\LogiTrack_Analytics_Compatibility_Test.SemanticModel\model.bim", "r", encoding="utf-8") as f:
    bim = json.load(f)

model_tables = {t["name"]: [c["name"] for c in t.get("columns", [])] for t in bim["model"]["tables"]}
measures = [m["name"] for t in bim["model"]["tables"] if t["name"] == "_Measures" for m in t.get("measures", [])]

print("Tables in model:", list(model_tables.keys()))
print("Total measures in model:", len(measures))

def validate_ref(query_ref):
    if "." not in query_ref:
        return False, f"Missing dot: {query_ref}"
    tbl, col = query_ref.split(".", 1)
    if tbl == "_Measures":
        if col in measures:
            return True, "Measure OK"
        return False, f"Measure '{col}' NOT in _Measures"
    elif tbl in model_tables:
        if col in model_tables[tbl]:
            return True, "Column OK"
        return False, f"Column '{col}' NOT in table '{tbl}'"
    return False, f"Table '{tbl}' NOT in model"

# Test some refs
test_refs = [
    "_Measures.Total Orders",
    "DimDate.month_name",
    "DimHub.hub_name",
    "FactOrders.order_status",
    "DimVehicle.current_status",
    "FactMaintenance.service_type",
    "DimDriver.driver_name"
]
for r in test_refs:
    print(r, validate_ref(r))
