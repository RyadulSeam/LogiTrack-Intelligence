"""
Batch ETL — Extraction Module
LogiTrack Intelligence — Phase 4

Extracts raw CSV files from data/source/, generates cryptographic SHA256 checksums,
and collects source metadata for lineage tracking.
"""

import hashlib
from pathlib import Path
from typing import Dict, Tuple
import pandas as pd
from loguru import logger

SOURCE_FILES = {
    "hubs": Path("data/source/Hubs.csv"),
    "drivers": Path("data/source/Drivers.csv"),
    "vehicles": Path("data/source/Vehicles.csv"),
    "orders": Path("data/source/Orders.csv"),
}


def calculate_file_hash(filepath: Path) -> str:
    """Calculates SHA256 checksum of a file for data lineage and change detection."""
    sha256 = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha256.update(chunk)
    return sha256.hexdigest()


def extract_source_data() -> Dict[str, Tuple[pd.DataFrame, Dict[str, str]]]:
    """
    Extracts all 4 source files and returns DataFrames along with metadata
    (file size, record count, SHA256 hash).
    """
    extracted = {}
    for name, path in SOURCE_FILES.items():
        if not path.exists():
            raise FileNotFoundError(f"Source file not found: {path}")

        file_hash = calculate_file_hash(path)
        df = pd.read_csv(path)
        
        metadata = {
            "source_file": str(path),
            "file_name": path.name,
            "row_count": len(df),
            "file_hash_sha256": file_hash,
        }
        
        logger.info(f"Extracted {name.upper()}: {len(df):,} rows from {path.name} (SHA: {file_hash[:8]}...)")
        extracted[name] = (df, metadata)

    return extracted
