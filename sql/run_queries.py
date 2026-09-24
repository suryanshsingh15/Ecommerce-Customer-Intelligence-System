"""
run_queries.py
---------------
Executes every query in analysis_queries.sql against the cleaned database
and saves the results to outputs/sql_query_results.txt — useful to verify
the SQL actually runs correctly and to showcase sample output.
"""

import sqlite3
import pandas as pd
import os
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "ecommerce.db")
SQL_PATH = os.path.join(BASE_DIR, "sql", "analysis_queries.sql")
OUT_PATH = os.path.join(BASE_DIR, "outputs", "sql_query_results.txt")

with open(SQL_PATH) as f:
    sql_text = f.read()

# Split into individual statements based on the numbered comment headers
blocks = re.split(r"\n(?=-- \d+[a-z]?\. )", sql_text)

conn = sqlite3.connect(DB_PATH)
lines = []

for block in blocks:
    block = block.strip()
    if not block or not re.search(r"SELECT", block, re.IGNORECASE):
        continue
    header_match = re.search(r"-- (\d+[a-z]?\..*)", block)
    title = header_match.group(1).strip() if header_match else "Query"
    # the actual SQL statement(s) in this block
    stmt = block
    try:
        df = pd.read_sql(stmt, conn)
        lines.append("=" * 78)
        lines.append(title)
        lines.append("=" * 78)
        lines.append(df.to_string(index=False))
        lines.append("")
        print(f"OK  : {title}")
    except Exception as e:
        lines.append(f"ERROR running query: {title}\n{e}\n")
        print(f"FAIL: {title} -> {e}")

conn.close()

os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
with open(OUT_PATH, "w") as f:
    f.write("\n".join(lines))

print(f"\nResults saved to: {OUT_PATH}")
