"""
Batch ETL — Pipeline Audit Module
LogiTrack Intelligence — Phase 4

Captures run metadata, execution timings, row counts, rejection metrics,
and operational status for full end-to-end auditability.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import pandas as pd
from loguru import logger

AUDIT_LOG_FILE = Path("data/processed/pipeline_audit.csv")


def record_pipeline_audit(audit_entry: Dict[str, Any]):
    """Appends an execution audit record to the persistent audit log."""
    AUDIT_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    df_entry = pd.DataFrame([audit_entry])
    if not AUDIT_LOG_FILE.exists():
        df_entry.to_csv(AUDIT_LOG_FILE, index=False)
    else:
        df_entry.to_csv(AUDIT_LOG_FILE, mode="a", header=False, index=False)
        
    logger.info(f"Recorded pipeline audit for run_id: {audit_entry.get('run_id')} (Status: {audit_entry.get('status')})")
