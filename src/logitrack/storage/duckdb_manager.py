"""
DuckDB Analytical Storage & Lakehouse Manager
LogiTrack Intelligence — Phase 3

Provides zero-overhead, memory-bounded local analytical querying
over Parquet files and local relational schemas.
"""

from pathlib import Path
from typing import Optional
import duckdb
from loguru import logger


class DuckDBManager:
    def __init__(
        self,
        db_path: Optional[str] = "data/lake/logitrack.duckdb",
        memory_limit: str = "2GB",
        threads: int = 2
    ):
        self.db_path = db_path
        self.memory_limit = memory_limit
        self.threads = threads
        
        # Ensure lake directory exists
        if db_path and db_path != ":memory:":
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            
        self.conn = duckdb.connect(db_path or ":memory:")
        self._configure()

    def _configure(self):
        """Sets memory boundaries to keep resource usage strictly within 16 GB laptop limits."""
        self.conn.execute(f"SET memory_limit = '{self.memory_limit}';")
        self.conn.execute(f"SET threads = {self.threads};")
        logger.debug(f"Configured DuckDB connection (memory_limit={self.memory_limit}, threads={self.threads})")

    def execute_script(self, sql_content: str):
        """Executes a multi-statement SQL script."""
        self.conn.execute(sql_content)

    def execute(self, sql: str, params: Optional[list] = None):
        """Executes a parameterized SQL command."""
        if params:
            return self.conn.execute(sql, params)
        return self.conn.execute(sql)

    def query(self, sql: str, params: Optional[list] = None):
        """Executes a query and returns a pandas DataFrame."""
        if params:
            return self.conn.execute(sql, params).df()
        return self.conn.execute(sql).df()

    def close(self):
        """Closes the connection safely."""
        self.conn.close()
