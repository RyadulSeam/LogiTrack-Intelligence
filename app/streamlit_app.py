"""
LogiTrack Intelligence — Streamlit Operational Control Tower Entrypoint
"""

import sys
from pathlib import Path

# Add project root and src directory
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "src"))

# Execute the primary application script
app_path = ROOT_DIR / "src" / "logitrack" / "app" / "app.py"
with open(app_path, "r", encoding="utf-8") as f:
    code = compile(f.read(), str(app_path), "exec")
    exec(code, globals())
