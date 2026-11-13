"""
Batch ETL — Data Quality Gate & Quarantine Module
LogiTrack Intelligence — Phase 4

Enforces DQ-001 through DQ-010 validation rules prior to database loading.
Routes rejected records to data/quarantine/ with rejection reasons.
"""

from pathlib import Path
from typing import Tuple, Dict, Any, List
import pandas as pd
from loguru import logger

QUARANTINE_DIR = Path("data/quarantine")


class DataQualityGate:
    def __init__(self, batch_id: str):
        self.batch_id = batch_id
        QUARANTINE_DIR.mkdir(parents=True, exist_ok=True)

    def validate_and_filter(
        self,
        entity_name: str,
        df: pd.DataFrame,
        pk_column: str,
        fk_validations: Dict[str, set] = None
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Validates records against DQ rules.
        Returns (valid_df, rejected_df).
        """
        valid_df = df.copy()
        rejections = []

        # 1. Primary key uniqueness and non-null
        null_pks = valid_df[valid_df[pk_column].isnull()]
        if len(null_pks) > 0:
            for idx in null_pks.index:
                rejections.append((idx, f"DQ-001: Missing Primary Key '{pk_column}'"))

        dup_mask = valid_df.duplicated(subset=[pk_column], keep="first")
        if dup_mask.any():
            for idx in valid_df[dup_mask].index:
                rejections.append((idx, f"DQ-001: Duplicate Primary Key '{pk_column}'"))

        # 2. Foreign Key Validations
        if fk_validations:
            for fk_col, valid_set in fk_validations.items():
                if fk_col in valid_df.columns:
                    invalid_fks = valid_df[~valid_df[fk_col].isin(valid_set) & valid_df[fk_col].notnull()]
                    for idx in invalid_fks.index:
                        rejections.append((idx, f"DQ-FK: Invalid foreign key '{fk_col}' value: {valid_df.loc[idx, fk_col]}"))

        # 3. Entity-specific business rule checks
        if entity_name == "orders":
            # Rating bounds [1, 5]
            invalid_ratings = valid_df[
                valid_df["customer_satisfaction_score"].notnull() & 
                ~valid_df["customer_satisfaction_score"].between(1, 5)
            ]
            for idx in invalid_ratings.index:
                rejections.append((idx, "DQ-009: CSAT score out of bounds [1, 5]"))

        # Process rejections if any
        if rejections:
            rej_indices = [r[0] for r in rejections]
            rej_reasons = {r[0]: r[1] for r in rejections}
            
            rejected_df = valid_df.loc[rej_indices].copy()
            rejected_df["rejection_reason"] = rejected_df.index.map(rej_reasons)
            rejected_df["rejection_batch_id"] = self.batch_id
            
            valid_df = valid_df.drop(index=rej_indices)
            
            # Save to quarantine
            quarantine_path = QUARANTINE_DIR / f"{self.batch_id}_{entity_name}_rejected.csv"
            rejected_df.to_csv(quarantine_path, index=False)
            logger.warning(f"Quarantined {len(rejected_df)} invalid {entity_name} records to {quarantine_path}")
            return valid_df, rejected_df

        return valid_df, pd.DataFrame()
