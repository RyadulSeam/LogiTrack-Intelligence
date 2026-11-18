"""
Stage 1: Project Inspection Script
LogiTrack Intelligence — Power BI PBIP Project
Comprehensive audit of all DuckDB schemas, tables, columns, data types, and row counts.
"""
import duckdb
import pandas as pd

con = duckdb.connect('data/lake/logitrack.duckdb', read_only=True)

# 1. List all schemas
print("=" * 70)
print("SECTION 1: DATABASE SCHEMAS")
print("=" * 70)
schemas = con.execute(
    "SELECT schema_name FROM information_schema.schemata "
    "WHERE schema_name NOT IN ('information_schema', 'pg_catalog') "
    "ORDER BY schema_name;"
).df()
print(schemas.to_string(index=False))

# 2. List all tables with row counts
print("\n" + "=" * 70)
print("SECTION 2: ALL TABLES WITH ROW COUNTS")
print("=" * 70)
tables = con.execute(
    "SELECT table_schema, table_name, table_type "
    "FROM information_schema.tables "
    "WHERE table_schema NOT IN ('information_schema', 'pg_catalog') "
    "ORDER BY table_schema, table_name;"
).df()

for _, row in tables.iterrows():
    schema = row['table_schema']
    table = row['table_name']
    ttype = row['table_type']
    try:
        cnt = con.execute(f"SELECT COUNT(*) AS cnt FROM {schema}.{table};").fetchone()[0]
    except Exception:
        cnt = "ERROR"
    print(f"  {schema}.{table:40s} [{ttype:15s}] -> {cnt:>10} rows")

# 3. Detailed column inspection for each warehouse table
print("\n" + "=" * 70)
print("SECTION 3: WAREHOUSE SCHEMA — DETAILED COLUMN INVENTORY")
print("=" * 70)

warehouse_tables = con.execute(
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = 'warehouse' ORDER BY table_name;"
).df()

for _, row in warehouse_tables.iterrows():
    tname = row['table_name']
    print(f"\n--- warehouse.{tname} ---")
    cols = con.execute(f"DESCRIBE warehouse.{tname};").df()
    print(cols.to_string(index=False))

    # Sample values
    sample = con.execute(f"SELECT * FROM warehouse.{tname} LIMIT 2;").df()
    print(f"  Sample ({len(sample)} rows):")
    for c in sample.columns:
        vals = sample[c].tolist()
        print(f"    {c}: {vals}")

# 4. ML schema inspection
print("\n" + "=" * 70)
print("SECTION 4: ML SCHEMA — DETAILED COLUMN INVENTORY")
print("=" * 70)

ml_tables = con.execute(
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = 'ml' ORDER BY table_name;"
).df()

for _, row in ml_tables.iterrows():
    tname = row['table_name']
    print(f"\n--- ml.{tname} ---")
    cols = con.execute(f"DESCRIBE ml.{tname};").df()
    print(cols.to_string(index=False))
    cnt = con.execute(f"SELECT COUNT(*) FROM ml.{tname};").fetchone()[0]
    print(f"  Row Count: {cnt}")

# 5. Raw and Staging schemas
print("\n" + "=" * 70)
print("SECTION 5: RAW & STAGING SCHEMAS — TABLES & COLUMNS")
print("=" * 70)

for schema_name in ['raw', 'staging']:
    stables = con.execute(
        f"SELECT table_name FROM information_schema.tables "
        f"WHERE table_schema = '{schema_name}' ORDER BY table_name;"
    ).df()
    for _, row in stables.iterrows():
        tname = row['table_name']
        print(f"\n--- {schema_name}.{tname} ---")
        cols = con.execute(f"DESCRIBE {schema_name}.{tname};").df()
        print(cols.to_string(index=False))
        cnt = con.execute(f"SELECT COUNT(*) FROM {schema_name}.{tname};").fetchone()[0]
        print(f"  Row Count: {cnt}")

# 6. Realtime schema
print("\n" + "=" * 70)
print("SECTION 6: REALTIME SCHEMA")
print("=" * 70)

rt_tables = con.execute(
    "SELECT table_name FROM information_schema.tables "
    "WHERE table_schema = 'realtime' ORDER BY table_name;"
).df()

for _, row in rt_tables.iterrows():
    tname = row['table_name']
    print(f"\n--- realtime.{tname} ---")
    cols = con.execute(f"DESCRIBE realtime.{tname};").df()
    print(cols.to_string(index=False))
    cnt = con.execute(f"SELECT COUNT(*) FROM realtime.{tname};").fetchone()[0]
    print(f"  Row Count: {cnt}")

con.close()
print("\n[INSPECTION COMPLETE]")
