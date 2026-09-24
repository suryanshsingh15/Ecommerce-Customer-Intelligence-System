"""
run_all.py
----------
Runs the entire E-Commerce Customer Intelligence System pipeline end-to-end:
  1. Generate raw (messy) data
  2. Load raw data into SQLite
  3. Clean data + run EDA (Pandas/NumPy) -> writes clean tables + charts
  4. Run SQL analysis queries -> outputs/sql_query_results.txt

Usage:
    python run_all.py
"""

import subprocess
import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

steps = [
    ("Generating raw data", ["data", "generate_data.py"]),
    ("Building SQLite database", ["database", "build_database.py"]),
    ("Cleaning data & running EDA", ["python", "data_cleaning_eda.py"]),
    ("Running SQL analysis queries", ["sql", "run_queries.py"]),
]

for label, path_parts in steps:
    print(f"\n{'='*70}\nSTEP: {label}\n{'='*70}")
    script_path = os.path.join(BASE_DIR, *path_parts)
    result = subprocess.run([sys.executable, script_path], cwd=os.path.dirname(script_path))
    if result.returncode != 0:
        print(f"\nStep failed: {label}")
        sys.exit(1)

print("\nAll steps completed successfully.")
print(f"See results in: {os.path.join(BASE_DIR, 'outputs')}")
