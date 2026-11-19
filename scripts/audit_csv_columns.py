import os
import glob
import pandas as pd

data_dir = r"F:\LogiTrack-Intelligence\dashboards\powerbi\data_export"
csv_files = sorted(glob.glob(os.path.join(data_dir, "*.csv")))

print("=== AUDIT OF CSV EXPORT DATASETS ===")
for cf in csv_files:
    fname = os.path.basename(cf)
    df = pd.read_csv(cf)
    print(f"\n--- {fname} (Rows: {len(df):,}, Cols: {len(df.columns)}) ---")
    for col in df.columns:
        non_null = df[col].notnull().sum()
        nunique = df[col].nunique()
        sample = df[col].dropna().unique()[:3].tolist()
        dtype = df[col].dtype
        print(f"  {col} ({dtype}): {non_null}/{len(df)} non-null, {nunique} unique -> sample: {sample}")
