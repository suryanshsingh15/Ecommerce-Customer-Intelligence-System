"""
generate_data.py
-----------------
Generates a synthetic (but realistic) raw e-commerce dataset and saves it as CSV files.
The data is deliberately imperfect (duplicates, missing values, inconsistent formatting)
so that the cleaning / preprocessing step in this project has real work to do —
mirroring the "handling missing values, duplicates, and inconsistent records" bullet
from the resume.

Output (raw, uncleaned):
    data/raw/customers.csv
    data/raw/products.csv
    data/raw/orders.csv
    data/raw/order_items.csv
"""

import random
import csv
import os
from datetime import datetime, timedelta

random.seed(42)

RAW_DIR = os.path.join(os.path.dirname(__file__), "raw")
os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Reference data
# ---------------------------------------------------------------------------
FIRST_NAMES = ["Aarav", "Vivaan", "Aditya", "Sai", "Reyansh", "Ishaan", "Arjun",
               "Kabir", "Ayaan", "Krishna", "Diya", "Ananya", "Isha", "Saanvi",
               "Aadhya", "Myra", "Aarohi", "Riya", "Kiara", "Anika", "Rohan",
               "Karthik", "Meera", "Neha", "Pooja", "Rahul", "Sneha", "Varun"]

LAST_NAMES = ["Sharma", "Verma", "Iyer", "Reddy", "Nair", "Gupta", "Singh",
              "Kapoor", "Rao", "Patel", "Menon", "Joshi", "Malhotra", "Chawla",
              "Bansal", "Mehta", "Pillai", "Bhat"]

# Inconsistent city spellings on purpose (to be standardized during cleaning)
CITIES = ["Bengaluru", "bengaluru", "Bangalore", "Mumbai", "mumbai", "Delhi",
          "New Delhi", "Chennai", "chennai", "Hyderabad", "Pune", "pune",
          "Kolkata", "Ahmedabad"]

CATEGORIES = {
    "Electronics": ["Wireless Earbuds", "Bluetooth Speaker", "Smartwatch",
                    "Laptop Stand", "USB-C Hub", "Power Bank 10000mAh",
                    "Mechanical Keyboard", "Wireless Mouse", "Webcam HD",
                    "Portable SSD 1TB"],
    "Fashion": ["Men's Cotton T-Shirt", "Women's Kurti", "Denim Jacket",
                "Running Shoes", "Leather Wallet", "Sunglasses",
                "Formal Shirt", "Women's Handbag", "Sports Cap", "Sneakers"],
    "Home & Kitchen": ["Non-Stick Pan Set", "Electric Kettle", "LED Desk Lamp",
                       "Air Fryer", "Cotton Bedsheet Set", "Vacuum Flask",
                       "Ceramic Dinner Set", "Storage Organizer Box"],
    "Beauty": ["Face Wash 100ml", "Sunscreen SPF50", "Lip Balm Pack",
              "Hair Serum", "Body Lotion 200ml", "Shampoo 340ml"],
    "Books": ["Fiction Bestseller", "Self-Help Book", "Children's Story Set",
             "Cookbook", "Business Strategy Book"],
    "Sports": ["Yoga Mat", "Adjustable Dumbbell Set", "Cricket Bat",
              "Football", "Resistance Bands Set", "Skipping Rope"],
}

STATUSES = ["Delivered", "Delivered", "Delivered", "Delivered", "Shipped",
            "Cancelled", "Returned", "Processing"]

N_CUSTOMERS = 150
N_PRODUCTS = 45
N_ORDERS = 520
START_DATE = datetime(2024, 1, 1)
END_DATE = datetime(2025, 12, 31)


def random_date(start, end):
    delta = end - start
    return start + timedelta(days=random.randint(0, delta.days))


# ---------------------------------------------------------------------------
# 1. Customers  (with duplicates + missing values + inconsistent casing)
# ---------------------------------------------------------------------------
customers = []
for cid in range(1, N_CUSTOMERS + 1):
    fname = random.choice(FIRST_NAMES)
    lname = random.choice(LAST_NAMES)
    name = f"{fname} {lname}"
    email = f"{fname.lower()}.{lname.lower()}{cid}@example.com"
    city = random.choice(CITIES)
    signup_date = random_date(START_DATE, END_DATE).strftime("%Y-%m-%d")

    # inject missing values randomly
    if random.random() < 0.05:
        email = ""
    if random.random() < 0.06:
        city = ""

    customers.append([cid, name, email, city, signup_date])

# inject a handful of exact-duplicate customer rows
for _ in range(6):
    customers.append(random.choice(customers[:N_CUSTOMERS]))

with open(os.path.join(RAW_DIR, "customers.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["customer_id", "customer_name", "email", "city", "signup_date"])
    w.writerows(customers)

# ---------------------------------------------------------------------------
# 2. Products (with a few missing prices + duplicate product rows)
# ---------------------------------------------------------------------------
products = []
pid = 1
for category, items in CATEGORIES.items():
    for item in items:
        if pid > N_PRODUCTS:
            break
        base_price = round(random.uniform(150, 6000), 2)
        products.append([pid, item, category, base_price])
        pid += 1

# a couple of missing prices (to be imputed with category median during cleaning)
for row in random.sample(products, 3):
    row[3] = ""

# duplicate product listing (data-entry error)
products.append(list(products[0]))
products.append(list(products[5]))

with open(os.path.join(RAW_DIR, "products.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["product_id", "product_name", "category", "price"])
    w.writerows(products)

# ---------------------------------------------------------------------------
# 3. Orders (some missing order_date, some inconsistent status casing)
# ---------------------------------------------------------------------------
customer_ids = [c[0] for c in customers[:N_CUSTOMERS]]
# skew towards repeat customers: 40% of customers get extra weight
repeat_pool = random.sample(customer_ids, int(N_CUSTOMERS * 0.4))
weighted_customers = customer_ids + repeat_pool * 3

orders = []
for oid in range(1001, 1001 + N_ORDERS):
    cust_id = random.choice(weighted_customers)
    order_date = random_date(START_DATE, END_DATE).strftime("%Y-%m-%d")
    status = random.choice(STATUSES)
    if random.random() < 0.3:
        status = status.upper() if random.random() < 0.5 else status.lower()
    if random.random() < 0.04:
        order_date = ""  # missing date
    orders.append([oid, cust_id, order_date, status])

# a duplicate order row (system glitch / double submission)
orders.append(list(orders[10]))
orders.append(list(orders[200]))

with open(os.path.join(RAW_DIR, "orders.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["order_id", "customer_id", "order_date", "status"])
    w.writerows(orders)

# ---------------------------------------------------------------------------
# 4. Order items (some negative/zero quantity, some missing unit_price)
# ---------------------------------------------------------------------------
order_ids = [o[0] for o in orders[:N_ORDERS]]
product_ids = [p[0] for p in products[:N_PRODUCTS]]
product_price = {p[0]: p[3] for p in products[:N_PRODUCTS]}

order_items = []
item_id = 1
for oid in order_ids:
    n_items = random.choices([1, 2, 3, 4], weights=[45, 30, 15, 10])[0]
    chosen_products = random.sample(product_ids, n_items)
    for pid_ in chosen_products:
        qty = random.choices([1, 2, 3, -1], weights=[70, 20, 8, 2])[0]  # -1 = bad data
        unit_price = product_price.get(pid_, "")
        if unit_price == "":
            unit_price = round(random.uniform(150, 6000), 2)
        if random.random() < 0.03:
            unit_price = ""  # missing price at line-item level
        order_items.append([item_id, oid, pid_, qty, unit_price])
        item_id += 1

with open(os.path.join(RAW_DIR, "order_items.csv"), "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["order_item_id", "order_id", "product_id", "quantity", "unit_price"])
    w.writerows(order_items)

print(f"Raw data generated in: {RAW_DIR}")
print(f"  customers.csv    : {len(customers)} rows")
print(f"  products.csv     : {len(products)} rows")
print(f"  orders.csv       : {len(orders)} rows")
print(f"  order_items.csv  : {len(order_items)} rows")
