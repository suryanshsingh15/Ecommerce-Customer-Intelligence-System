"""
build_database.py
------------------
Loads the raw CSV files into a SQLite relational database (raw_* tables).
This mirrors the resume bullet: "Designed and queried a relational database
containing customer, order, and product data."

Run this AFTER data/generate_data.py and BEFORE python/data_cleaning_eda.py.
"""

import sqlite3
import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "data", "raw")
DB_PATH = os.path.join(BASE_DIR, "database", "ecommerce.db")

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

conn = sqlite3.connect(DB_PATH)

tables = {
    "raw_customers": "customers.csv",
    "raw_products": "products.csv",
    "raw_orders": "orders.csv",
    "raw_order_items": "order_items.csv",
}

for table_name, filename in tables.items():
    df = pd.read_csv(os.path.join(RAW_DIR, filename))
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    print(f"Loaded {filename} -> {table_name} ({len(df)} rows)")

conn.commit()
conn.close()
print(f"\nSQLite database created at: {DB_PATH}")
