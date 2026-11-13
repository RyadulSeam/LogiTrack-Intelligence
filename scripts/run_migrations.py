"""
Database Migration Runner
LogiTrack Intelligence — Phase 3

Executes SQL migration scripts sequentially against Neon PostgreSQL (if DATABASE_URL is set)
and local DuckDB analytical lakehouse.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
import sqlalchemy
from sqlalchemy import text

from logitrack.storage.duckdb_manager import DuckDBManager

load_dotenv()


def get_migration_files():
    migrations_dir = Path("database/migrations")
    files = sorted(migrations_dir.glob("*.sql"))
    return files


def run_duckdb_migrations(db_path: str = "data/lake/logitrack.duckdb"):
    logger.info(f"Running migrations on DuckDB at {db_path}...")
    manager = DuckDBManager(db_path=db_path)
    
    for f in get_migration_files():
        logger.info(f"Applying {f.name} to DuckDB...")
        with open(f, "r", encoding="utf-8") as sql_file:
            sql_content = sql_file.read()
            # DuckDB natively supports Postgres DDL syntax
            manager.execute_script(sql_content)
            
    logger.success("DuckDB migrations applied successfully!")
    manager.close()


def run_postgres_migrations(database_url: str):
    logger.info("Connecting to Neon PostgreSQL...")
    engine = sqlalchemy.create_engine(database_url, echo=False)
    
    with engine.begin() as conn:
        for f in get_migration_files():
            logger.info(f"Applying {f.name} to PostgreSQL...")
            with open(f, "r", encoding="utf-8") as sql_file:
                sql_content = sql_file.read()
                # Run individual statements split by semicolon if needed
                conn.execute(text(sql_content))
                
    logger.success("Neon PostgreSQL migrations applied successfully!")


if __name__ == "__main__":
    # Always apply to local DuckDB for local analytics and offline testing
    run_duckdb_migrations()
    
    db_url = os.getenv("DATABASE_URL")
    if db_url and "user:password" not in db_url:
        logger.info("Found real DATABASE_URL in .env, running remote Neon migrations...")
        try:
            run_postgres_migrations(db_url)
        except Exception as e:
            logger.error(f"PostgreSQL migration failed: {e}")
    else:
        logger.info("No active Neon DATABASE_URL configured in .env (placeholder detected). Local DuckDB is primary.")
