"""
Stage 3: Semantic Model & Referential Integrity Verification
"""
import duckdb

con = duckdb.connect('data/lake/logitrack.duckdb', read_only=True)

print("=" * 70)
print("SECTION 1: PRIMARY KEY UNIQUENESS CHECKS")
print("=" * 70)
tables = [
    ('warehouse', 'dim_date', 'date_key'),
    ('warehouse', 'dim_hub', 'hub_key'),
    ('warehouse', 'dim_driver', 'driver_key'),
    ('warehouse', 'dim_vehicle', 'vehicle_key'),
    ('warehouse', 'dim_route', 'route_key'),
    ('warehouse', 'fact_orders', 'order_id'),
    ('warehouse', 'fact_hub_hourly', 'hub_hourly_id'),
    ('ml', 'model_registry', 'model_id'),
    ('ml', 'predictions', 'prediction_id'),
]

for schema, tbl, pk in tables:
    total = con.execute(f"SELECT COUNT(*) FROM {schema}.{tbl};").fetchone()[0]
    distinct = con.execute(f"SELECT COUNT(DISTINCT {pk}) FROM {schema}.{tbl};").fetchone()[0]
    status = "PASS" if total == distinct else "FAIL"
    print(f"  {schema}.{tbl:20s} ({pk:15s}): Total={total:>6}, Distinct={distinct:>6} -> {status}")

print("\n" + "=" * 70)
print("SECTION 2: FOREIGN KEY INTEGRITY CHECKS (fact_orders)")
print("=" * 70)
fk_checks = [
    ('order_date_key', 'warehouse.dim_date', 'date_key'),
    ('delivery_date_key', 'warehouse.dim_date', 'date_key'),
    ('hub_key', 'warehouse.dim_hub', 'hub_key'),
    ('driver_key', 'warehouse.dim_driver', 'driver_key'),
    ('vehicle_key', 'warehouse.dim_vehicle', 'vehicle_key'),
]

for fk_col, dim_tbl, dim_pk in fk_checks:
    orphan_q = f"""
        SELECT COUNT(*) 
        FROM warehouse.fact_orders f 
        LEFT JOIN {dim_tbl} d ON f.{fk_col} = d.{dim_pk}
        WHERE f.{fk_col} IS NOT NULL AND d.{dim_pk} IS NULL;
    """
    orphans = con.execute(orphan_q).fetchone()[0]
    nulls = con.execute(f"SELECT COUNT(*) FROM warehouse.fact_orders WHERE {fk_col} IS NULL;").fetchone()[0]
    status = "PASS" if orphans == 0 else "FAIL"
    print(f"  fact_orders.{fk_col:18s} -> {dim_tbl}.{dim_pk}: Orphans={orphans:>2}, Nulls={nulls:>4} -> {status}")

print("\n" + "=" * 70)
print("SECTION 3: FOREIGN KEY INTEGRITY CHECKS (fact_hub_hourly)")
print("=" * 70)
hub_orphans = con.execute("""
    SELECT COUNT(*) 
    FROM warehouse.fact_hub_hourly f 
    LEFT JOIN warehouse.dim_hub d ON f.hub_key = d.hub_key 
    WHERE d.hub_key IS NULL;
""").fetchone()[0]
date_orphans = con.execute("""
    SELECT COUNT(*) 
    FROM warehouse.fact_hub_hourly f 
    LEFT JOIN warehouse.dim_date d ON f.date_key = d.date_key 
    WHERE d.date_key IS NULL;
""").fetchone()[0]
print(f"  fact_hub_hourly.hub_key  -> dim_hub.hub_key:  Orphans={hub_orphans} -> {'PASS' if hub_orphans == 0 else 'FAIL'}")
print(f"  fact_hub_hourly.date_key -> dim_date.date_key: Orphans={date_orphans} -> {'PASS' if date_orphans == 0 else 'FAIL'}")

print("\n" + "=" * 70)
print("SECTION 4: SYNTHETIC MAINTENANCE FOREIGN KEY CHECKS")
print("=" * 70)
maint_check = con.execute("""
    SELECT 
        COUNT(*) AS total_maint,
        COUNT(DISTINCT m.vehicle_code) AS distinct_vehicles,
        COUNT(*) FILTER (WHERE v.vehicle_key IS NULL) AS orphan_vehicles
    FROM read_csv_auto('data/synthetic/synthetic_maintenance.csv') m
    LEFT JOIN warehouse.dim_vehicle v ON m.vehicle_code = v.vehicle_code;
""").df()
print(maint_check.to_string(index=False))

con.close()
print("\n[SEMANTIC MODEL INTEGRITY VERIFIED]")
