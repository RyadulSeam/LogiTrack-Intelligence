"""
Batch ETL — Database Loading Module
LogiTrack Intelligence — Phase 4

Loads Bronze (raw.*) and Silver (staging.*) DataFrames idempotently into DuckDB
(and Neon PostgreSQL if active DATABASE_URL is configured).
"""

from typing import Dict
import pandas as pd
from loguru import logger
import sqlalchemy
from sqlalchemy import text
from logitrack.storage.duckdb_manager import DuckDBManager


def load_to_duckdb(
    raw_data: Dict[str, pd.DataFrame],
    staging_data: Dict[str, pd.DataFrame],
    db_path: str = "data/lake/logitrack.duckdb"
):
    """Loads raw and staging datasets idempotently into DuckDB."""
    manager = DuckDBManager(db_path=db_path)
    
    # 1. Load Raw (Bronze) Tables
    for entity, df in raw_data.items():
        table_name = f"raw.raw_{entity}"
        manager.conn.register("temp_raw", df)
        manager.execute_script(f"DELETE FROM {table_name};")
        manager.execute_script(f"INSERT INTO {table_name} SELECT * FROM temp_raw;")
        manager.conn.unregister("temp_raw")
        logger.info(f"Loaded {len(df):,} records into DuckDB table '{table_name}'")

    # 2. Load Staging (Silver) Tables
    for entity, df in staging_data.items():
        table_name = f"staging.stg_{entity}"
        manager.conn.register("temp_stg", df)
        manager.execute_script(f"DELETE FROM {table_name};")
        manager.execute_script(f"INSERT INTO {table_name} SELECT * FROM temp_stg;")
        manager.conn.unregister("temp_stg")
        logger.info(f"Loaded {len(df):,} records into DuckDB table '{table_name}'")

    manager.close()
    logger.success("Idempotent DuckDB loading completed!")


def load_to_postgres(
    raw_data: Dict[str, pd.DataFrame],
    staging_data: Dict[str, pd.DataFrame],
    database_url: str
):
    """Loads raw and staging datasets idempotently into Neon PostgreSQL."""
    engine = sqlalchemy.create_engine(database_url)
    
    with engine.begin() as conn:
        for entity, df in raw_data.items():
            table_name = f"raw_{entity}"
            conn.execute(text(f"TRUNCATE TABLE raw.{table_name};"))
            df.to_sql(table_name, con=conn, schema="raw", if_exists="append", index=False)
            logger.info(f"Loaded {len(df):,} records into PostgreSQL 'raw.{table_name}'")

        for entity, df in staging_data.items():
            table_name = f"stg_{entity}"
            conn.execute(text(f"TRUNCATE TABLE staging.{table_name};"))
            df.to_sql(table_name, con=conn, schema="staging", if_exists="append", index=False)
            logger.info(f"Loaded {len(df):,} records into PostgreSQL 'staging.{table_name}'")

    logger.success("PostgreSQL loading completed!")
