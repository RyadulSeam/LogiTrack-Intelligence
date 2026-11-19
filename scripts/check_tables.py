import duckdb
c = duckdb.connect("data/lake/logitrack.duckdb", read_only=True)
tbls = c.execute("""
SELECT table_schema, table_name FROM information_schema.tables
WHERE table_schema IN ('staging', 'warehouse', 'forecasting', 'ml')
ORDER BY table_schema, table_name
""").fetchdf()
print(tbls.to_string())
c.close()
