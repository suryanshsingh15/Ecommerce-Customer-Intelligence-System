"""
data_cleaning_eda.py
---------------------
Resume bullet covered here:
"Performed data cleaning and exploratory data analysis using Python, Pandas,
and NumPy, handling missing values, duplicates, and inconsistent records."

Steps:
  1. Load raw_* tables from the SQLite database.
  2. Clean each table:
       - drop exact duplicate rows
       - standardize inconsistent text (city names, order status casing)
       - handle missing values (impute / flag / drop, chosen per-column)
       - fix inconsistent records (negative quantities, orphan foreign keys)
  3. Write cleaned tables back to the database (customers, products, orders,
     order_items) so the SQL analysis step can query clean data.
  4. Run exploratory data analysis with Pandas/NumPy and save:
       - a text summary report (outputs/eda_summary.txt)
       - 4 charts (outputs/*.png)
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "database", "ecommerce.db")
OUT_DIR = os.path.join(BASE_DIR, "outputs")
os.makedirs(OUT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

report_lines = []


def log(line=""):
    print(line)
    report_lines.append(line)


log("=" * 70)
log("E-COMMERCE CUSTOMER INTELLIGENCE SYSTEM — DATA CLEANING & EDA REPORT")
log("=" * 70)

# ---------------------------------------------------------------------------
# 1. LOAD RAW TABLES
# ---------------------------------------------------------------------------
customers = pd.read_sql("SELECT * FROM raw_customers", conn)
products = pd.read_sql("SELECT * FROM raw_products", conn)
orders = pd.read_sql("SELECT * FROM raw_orders", conn)
order_items = pd.read_sql("SELECT * FROM raw_order_items", conn)

log(f"\nRaw row counts -> customers: {len(customers)}, products: {len(products)}, "
    f"orders: {len(orders)}, order_items: {len(order_items)}")

# ---------------------------------------------------------------------------
# 2. CLEAN CUSTOMERS
# ---------------------------------------------------------------------------
log("\n--- Cleaning: customers ---")

dupes = customers.duplicated().sum()
customers = customers.drop_duplicates().reset_index(drop=True)
log(f"Removed {dupes} exact duplicate customer rows.")

customers["email"] = customers["email"].replace("", np.nan)
customers["city"] = customers["city"].replace("", np.nan)

missing_email = customers["email"].isna().sum()
missing_city_before = customers["city"].isna().sum()
log(f"Missing emails: {missing_email} (flagged as 'unknown@example.com')")
customers["email"] = customers["email"].fillna("unknown@example.com")

# standardize inconsistent city names (case + spelling variants)
city_map = {
    "bengaluru": "Bengaluru", "bangalore": "Bengaluru", "bengaluru": "Bengaluru",
    "mumbai": "Mumbai", "new delhi": "Delhi", "delhi": "Delhi",
    "chennai": "Chennai", "pune": "Pune", "hyderabad": "Hyderabad",
    "kolkata": "Kolkata", "ahmedabad": "Ahmedabad",
}
customers["city_clean"] = customers["city"].str.strip().str.lower().map(city_map)
customers["city_clean"] = customers["city_clean"].fillna("Unknown")
customers["city"] = customers["city_clean"]
customers = customers.drop(columns=["city_clean"])
log(f"Standardized city names (e.g. 'bengaluru'/'Bangalore' -> 'Bengaluru'). "
    f"Missing city values ({missing_city_before}) set to 'Unknown'.")

customers["signup_date"] = pd.to_datetime(customers["signup_date"], errors="coerce")

# ---------------------------------------------------------------------------
# 3. CLEAN PRODUCTS
# ---------------------------------------------------------------------------
log("\n--- Cleaning: products ---")

dupes = products.duplicated(subset=["product_id"]).sum()
products = products.drop_duplicates(subset=["product_id"], keep="first").reset_index(drop=True)
log(f"Removed {dupes} duplicate product_id rows.")

products["price"] = pd.to_numeric(products["price"], errors="coerce")
missing_price = products["price"].isna().sum()
# impute missing price with the median price of the same category
products["price"] = products.groupby("category")["price"].transform(
    lambda s: s.fillna(s.median())
)
log(f"Imputed {missing_price} missing product prices using category median.")

# ---------------------------------------------------------------------------
# 4. CLEAN ORDERS
# ---------------------------------------------------------------------------
log("\n--- Cleaning: orders ---")

dupes = orders.duplicated(subset=["order_id"]).sum()
orders = orders.drop_duplicates(subset=["order_id"], keep="first").reset_index(drop=True)
log(f"Removed {dupes} duplicate order_id rows.")

orders["status"] = orders["status"].str.strip().str.title()

orders["order_date"] = orders["order_date"].replace("", np.nan)
missing_dates = orders["order_date"].isna().sum()
orders = orders.dropna(subset=["order_date"]).reset_index(drop=True)
log(f"Dropped {missing_dates} orders with missing order_date (cannot be reliably imputed).")
orders["order_date"] = pd.to_datetime(orders["order_date"])

# drop orders referencing a customer_id that no longer exists (orphan FK safety check)
valid_customer_ids = set(customers["customer_id"])
before = len(orders)
orders = orders[orders["customer_id"].isin(valid_customer_ids)].reset_index(drop=True)
log(f"Removed {before - len(orders)} orders with an orphan customer_id.")

# ---------------------------------------------------------------------------
# 5. CLEAN ORDER ITEMS
# ---------------------------------------------------------------------------
log("\n--- Cleaning: order_items ---")

dupes = order_items.duplicated(subset=["order_item_id"]).sum()
order_items = order_items.drop_duplicates(subset=["order_item_id"]).reset_index(drop=True)
log(f"Removed {dupes} duplicate order_item_id rows.")

order_items["unit_price"] = pd.to_numeric(order_items["unit_price"], errors="coerce")
missing_line_price = order_items["unit_price"].isna().sum()
price_lookup = products.set_index("product_id")["price"]
order_items["unit_price"] = order_items["unit_price"].fillna(
    order_items["product_id"].map(price_lookup)
)
log(f"Filled {missing_line_price} missing line-item prices from the product master.")

bad_qty = (order_items["quantity"] <= 0).sum()
order_items = order_items[order_items["quantity"] > 0].reset_index(drop=True)
log(f"Removed {bad_qty} order_item rows with invalid (zero/negative) quantity.")

# keep only order_items referencing a surviving, cleaned order
valid_order_ids = set(orders["order_id"])
before = len(order_items)
order_items = order_items[order_items["order_id"].isin(valid_order_ids)].reset_index(drop=True)
log(f"Removed {before - len(order_items)} order_item rows tied to dropped/invalid orders.")

order_items["line_revenue"] = order_items["quantity"] * order_items["unit_price"]

log(f"\nClean row counts -> customers: {len(customers)}, products: {len(products)}, "
    f"orders: {len(orders)}, order_items: {len(order_items)}")

# ---------------------------------------------------------------------------
# 6. WRITE CLEAN TABLES BACK TO SQLITE (for the SQL analysis step)
# ---------------------------------------------------------------------------
customers.to_sql("customers", conn, if_exists="replace", index=False)
products.to_sql("products", conn, if_exists="replace", index=False)
orders_out = orders.copy()
orders_out["order_date"] = orders_out["order_date"].dt.strftime("%Y-%m-%d")
orders_out.to_sql("orders", conn, if_exists="replace", index=False)
order_items.to_sql("order_items", conn, if_exists="replace", index=False)
conn.commit()
log("\nClean tables written to database: customers, products, orders, order_items")

# ---------------------------------------------------------------------------
# 7. EXPLORATORY DATA ANALYSIS (Pandas / NumPy)
# ---------------------------------------------------------------------------
log("\n" + "=" * 70)
log("EXPLORATORY DATA ANALYSIS")
log("=" * 70)

# Merge into a single analysis-ready frame
full = (order_items
        .merge(orders, on="order_id", how="left")
        .merge(customers, on="customer_id", how="left")
        .merge(products, on="product_id", how="left", suffixes=("", "_product")))

delivered = full[full["status"].isin(["Delivered", "Shipped"])].copy()

# --- Revenue overview ---
total_revenue = delivered["line_revenue"].sum()
total_orders = delivered["order_id"].nunique()
aov = total_revenue / total_orders
log(f"\nTotal revenue (Delivered/Shipped orders): Rs. {total_revenue:,.2f}")
log(f"Total fulfilled orders: {total_orders}")
log(f"Average Order Value (AOV): Rs. {aov:,.2f}")

# --- Order value distribution stats (NumPy) ---
order_values = delivered.groupby("order_id")["line_revenue"].sum().values
log(f"\nOrder value stats -> mean: {np.mean(order_values):.2f}, "
    f"median: {np.median(order_values):.2f}, std: {np.std(order_values):.2f}, "
    f"min: {np.min(order_values):.2f}, max: {np.max(order_values):.2f}")

# --- Monthly revenue trend ---
delivered["order_month"] = delivered["order_date"].dt.to_period("M").astype(str)
monthly_revenue = delivered.groupby("order_month")["line_revenue"].sum().sort_index()

# --- Top customers by revenue ---
customer_revenue = (delivered.groupby(["customer_id", "customer_name"])["line_revenue"]
                     .sum().sort_values(ascending=False).reset_index())
top_customers = customer_revenue.head(10)
log("\nTop 5 customers by revenue:")
for _, row in top_customers.head(5).iterrows():
    log(f"  {row['customer_name']:<20} Rs. {row['line_revenue']:,.2f}")

# --- Repeat purchase analysis ---
orders_per_customer = orders.groupby("customer_id")["order_id"].nunique()
repeat_customers = (orders_per_customer >= 2).sum()
total_customers_with_orders = orders_per_customer.shape[0]
repeat_rate = repeat_customers / total_customers_with_orders * 100
log(f"\nCustomers with >=2 orders (repeat customers): {repeat_customers} "
    f"of {total_customers_with_orders} ({repeat_rate:.1f}%)")

# --- Product / category performance ---
category_perf = (delivered.groupby("category")["line_revenue"]
                  .sum().sort_values(ascending=False))
log("\nRevenue by category:")
for cat, rev in category_perf.items():
    log(f"  {cat:<18} Rs. {rev:,.2f}")

top_products = (delivered.groupby("product_name")["line_revenue"]
                 .sum().sort_values(ascending=False).head(10))

# ---------------------------------------------------------------------------
# 8. CHARTS
# ---------------------------------------------------------------------------
plt.style.use("seaborn-v0_8-whitegrid") if "seaborn-v0_8-whitegrid" in plt.style.available else None

# Chart 1: Monthly revenue trend
plt.figure(figsize=(9, 4.5))
plt.plot(monthly_revenue.index, monthly_revenue.values, marker="o", color="#2563eb")
plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue (Rs.)")
plt.xticks(rotation=45, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "01_monthly_revenue_trend.png"), dpi=130)
plt.close()

# Chart 2: Top 10 customers by revenue
plt.figure(figsize=(8, 5))
plt.barh(top_customers["customer_name"][::-1], top_customers["line_revenue"][::-1],
         color="#16a34a")
plt.title("Top 10 Customers by Revenue")
plt.xlabel("Revenue (Rs.)")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "02_top_customers.png"), dpi=130)
plt.close()

# Chart 3: Revenue by category
plt.figure(figsize=(8, 5))
plt.bar(category_perf.index, category_perf.values, color="#f59e0b")
plt.title("Revenue by Product Category")
plt.ylabel("Revenue (Rs.)")
plt.xticks(rotation=30, ha="right")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "03_category_performance.png"), dpi=130)
plt.close()

# Chart 4: Order value distribution
plt.figure(figsize=(8, 5))
plt.hist(order_values, bins=25, color="#7c3aed", edgecolor="white")
plt.title("Distribution of Order Values")
plt.xlabel("Order Value (Rs.)")
plt.ylabel("Number of Orders")
plt.tight_layout()
plt.savefig(os.path.join(OUT_DIR, "04_order_value_distribution.png"), dpi=130)
plt.close()

log(f"\nSaved 4 charts to: {OUT_DIR}")

# ---------------------------------------------------------------------------
# 9. SAVE REPORT
# ---------------------------------------------------------------------------
report_path = os.path.join(OUT_DIR, "eda_summary.txt")
with open(report_path, "w") as f:
    f.write("\n".join(report_lines))

# also export the cleaned, analysis-ready dataset
full.to_csv(os.path.join(OUT_DIR, "clean_merged_dataset.csv"), index=False)

conn.close()
print(f"\nFull text report saved to: {report_path}")
