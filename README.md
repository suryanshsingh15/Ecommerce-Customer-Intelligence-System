# E-Commerce Customer Intelligence System

Python | SQL | Pandas | NumPy | Statistics

A complete, runnable project that matches the resume bullet points exactly:

- Analyzed customer purchasing behavior using SQL to identify revenue trends, top customers, repeat purchases, and product performance.
- Designed and queried a relational database containing customer, order, and product data using JOINs, aggregations, subqueries, and CTEs.
- Performed data cleaning and exploratory data analysis using Python, Pandas, and NumPy, handling missing values, duplicates, and inconsistent records.

## Project structure

```
ecommerce-customer-intelligence/
├── data/
│   ├── generate_data.py        # creates a realistic, intentionally "messy" raw dataset
│   └── raw/                    # generated CSVs: customers, products, orders, order_items
├── database/
│   ├── build_database.py       # loads raw CSVs into a SQLite relational database
│   └── ecommerce.db            # SQLite database (raw_* tables + cleaned tables)
├── python/
│   └── data_cleaning_eda.py    # Pandas/NumPy: cleaning + exploratory data analysis
├── sql/
│   ├── analysis_queries.sql    # JOINs, aggregations, subqueries, CTEs, window functions
│   └── run_queries.py          # executes every query and saves the results
├── outputs/
│   ├── eda_summary.txt              # full text report of the cleaning + EDA run
│   ├── sql_query_results.txt        # output of every SQL query
│   ├── clean_merged_dataset.csv     # final cleaned, analysis-ready dataset
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_top_customers.png
│   ├── 03_category_performance.png
│   └── 04_order_value_distribution.png
└── run_all.py                  # runs the entire pipeline end-to-end
```

## How to run

```bash
pip install pandas numpy matplotlib
python run_all.py
```

This will, in order:
1. Generate a synthetic raw dataset (150 customers, 45 products, ~520 orders, ~970 order line items) with deliberately injected duplicates, missing values, and inconsistent formatting — so the cleaning step has real problems to fix.
2. Load the raw CSVs into a SQLite database (`database/ecommerce.db`).
3. Clean the data with Pandas/NumPy: removes exact duplicates, standardizes inconsistent city names and order-status casing, imputes missing prices from the category median, drops orders with unusable missing dates, removes invalid (negative) quantities, and rebuilds a merged analysis-ready dataset. Cleaned tables are written back to the database.
4. Run exploratory data analysis (revenue stats, order value distribution, monthly trend, top customers, repeat-purchase rate, category performance) and save 4 charts plus a text summary to `outputs/`.
5. Run the full SQL analysis file (`sql/analysis_queries.sql`) against the cleaned database and save results.

## What the SQL analysis covers

| # | Query | SQL techniques used |
|---|-------|---------------------|
| 1 | Monthly revenue trend | JOIN, GROUP BY, aggregation |
| 2 | Top 10 customers by revenue | multi-table JOIN, aggregation |
| 3 | Repeat purchase rate & repeat customers | CTE (`WITH`), scalar subqueries |
| 4 | Product performance (units sold, revenue) | JOIN, GROUP BY |
| 5 | Category performance ranking | subquery + `RANK()` window function |
| 6 | Above-average-spend customers | correlated subquery, `HAVING` |
| 7 | City-wise revenue | JOIN, GROUP BY |
| 8 | Order status / cancellation breakdown | aggregation, subquery |

## What the Python cleaning/EDA covers

- **Duplicates**: exact duplicate customer rows, duplicate `product_id`s, duplicate `order_id`s.
- **Missing values**: blank emails (flagged), blank cities (set to "Unknown"), missing product prices (imputed via category median), missing order dates (dropped — cannot be safely imputed), missing line-item prices (filled from the product master).
- **Inconsistent records**: city name variants (`"bengaluru"`, `"Bangalore"`, `"Bengaluru"` → standardized to `"Bengaluru"`), inconsistent order-status casing, invalid (zero/negative) order quantities, orphan foreign keys.
- **EDA**: revenue totals, average order value, order-value distribution stats (mean/median/std via NumPy), monthly revenue trend, top customers, repeat-purchase rate, category/product performance, city-wise revenue — visualized in 4 charts.

## Sample results from this run

- Total revenue (fulfilled orders): **Rs. 2,259,427.95**
- Average Order Value: **Rs. 8,012.16**
- Repeat customer rate: **77.0%**
- Top category by revenue: **Fashion**

## Notes for adapting this to your resume / interview

- All data here is **synthetically generated** (see `data/generate_data.py`) so the project is fully self-contained and reproducible — no external dataset download needed. If you'd rather use a real public dataset (e.g., the "Olist" Brazilian e-commerce dataset or a Kaggle e-commerce dataset), swap the CSVs in `data/raw/` and keep the same schema; the cleaning, SQL, and EDA code will work unchanged.
- Push this folder to GitHub as-is and link it from your resume/portfolio.
- Be ready to explain the cleaning choices (why dates were dropped instead of imputed, why prices were imputed with category median, etc.) — interviewers often probe exactly these decisions.
