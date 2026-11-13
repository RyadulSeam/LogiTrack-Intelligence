"""
Streaming Dead-Letter & Failure Handler
LogiTrack Intelligence — Phase 5

Captures corrupt, unparseable, or schema-violating streaming events
and routes them to dead-letter persistent storage for investigation.
"""

import json
import uuid
from pathlib import Path
from datetime import datetime
from typing import Optional
from loguru import logger
from logitrack.storage.duckdb_manager import DuckDBManager

DEAD_LETTER_FILE = Path("data/quarantine/dead_letter_events.jsonl")


class DeadLetterHandler:
    def __init__(self, db_path: str = "data/lake/logitrack.duckdb"):
        self.db_path = db_path
        DEAD_LETTER_FILE.parent.mkdir(parents=True, exist_ok=True)

    def route_to_dead_letter(
        self,
        topic: str,
        raw_payload: str,
        reason: str
    ):
        error_id = f"err-{uuid.uuid4().hex[:12]}"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        logger.warning(f"Routing event to DLQ [{error_id}]: {reason}")

        # 1. Append to local JSON Lines quarantine file
        dlq_entry = {
            "error_id": error_id,
            "topic": topic,
            "raw_payload": raw_payload,
            "reason": reason,
            "timestamp": now
        }
        with open(DEAD_LETTER_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(dlq_entry) + "\n")

        # 2. Insert into realtime.ingestion_errors in DuckDB
        try:
            manager = DuckDBManager(db_path=self.db_path)
            manager.conn.execute(
                """
                INSERT INTO realtime.ingestion_errors (error_id, source_topic, failed_payload, error_reason, error_timestamp)
                VALUES (?, ?, ?, ?, ?);
                """,
                [error_id, topic, raw_payload[:1000], reason, now]
            )
            manager.close()
        except Exception as e:
            logger.error(f"Failed to record error in database DLQ table: {e}")
