E-Commerce Customer Intelligence System

Python | SQL | Pandas | NumPy | SQLite | Statistics

An end-to-end data analysis project for studying e-commerce customer, order, and product data using Python and SQL. The project covers data generation, cleaning, database creation, exploratory analysis, and SQL-based business analysis.

Project Overview

The system analyzes customer purchasing behavior and sales data to identify:

* Revenue trends
* Top customers
* Repeat purchases
* Product and category performance
* City-wise revenue
* Order status and cancellation patterns

The project uses Python for data cleaning and exploratory analysis and SQLite for relational data storage and SQL analysis.

Project Structure
'''text
ecommerce-customer-intelligence/
│
├── data/
│   ├── generate_data.py
│   └── raw/
│       ├── customers.csv
│       ├── products.csv
│       ├── orders.csv
│       └── order_items.csv
│
├── database/
│   ├── build_database.py
│   └── ecommerce.db
│
├── python/
│   └── data_cleaning_eda.py
│
├── sql/
│   ├── analysis_queries.sql
│   └── run_queries.py
│
├── outputs/
│   ├── eda_summary.txt
│   ├── sql_query_results.txt
│   ├── clean_merged_dataset.csv
│   ├── 01_monthly_revenue_trend.png
│   ├── 02_top_customers.png
│   ├── 03_category_performance.png
│   └── 04_order_value_distribution.png
│
├── run_all.py
└── README.md
'''
Dataset

The project uses synthetically generated e-commerce data so that the complete pipeline can run without downloading an external dataset.

The generated dataset contains approximately:

* 150 customers
* 45 products
* 520 orders
* 970 order items

The raw data contains intentionally introduced duplicates, missing values, and inconsistent formatting to provide realistic data-cleaning tasks.

How to Run

Install the required Python libraries:

pip install pandas numpy matplotlib

Then run the complete pipeline:

python run_all.py

The pipeline performs the following steps automatically.

Data Processing Pipeline

1. Generate Raw Data

Python generates customer, product, order, and order-item CSV files.

The raw data includes some duplicate records, missing values, and inconsistent values that are handled during the cleaning stage.

2. Create SQLite Database

The raw CSV files are loaded into a SQLite relational database:

database/ecommerce.db

The database contains the tables required for customer, product, order, and order-item analysis.

3. Data Cleaning

Python, Pandas, and NumPy are used to clean the raw data.

The cleaning process includes:

* Removing exact duplicate records
* Handling duplicate customer, product, and order IDs
* Handling missing email and city values
* Standardizing city names
* Standardizing order-status values
* Filling missing product prices using the category median
* Filling missing line-item prices using the product information
* Removing orders with unusable dates
* Removing invalid zero or negative quantities
* Checking for orphan foreign-key records
* Creating a cleaned dataset for analysis

The cleaned tables are also written back to the SQLite database.

Exploratory Data Analysis

The Python analysis calculates and summarizes:

* Total revenue
* Average order value
* Order-value distribution
* Monthly revenue trends
* Top customers
* Repeat-customer rate
* Product performance
* Category performance
* City-wise revenue

Four charts are generated and saved in the outputs/ directory.

SQL Analysis

The SQL analysis uses the cleaned SQLite database to answer common e-commerce business questions.

#	Analysis	SQL Techniques
1	Monthly revenue trend	JOIN, GROUP BY, aggregation
2	Top 10 customers by revenue	Multi-table JOIN, aggregation
3	Repeat purchase rate	CTE, scalar subquery
4	Product performance	JOIN, GROUP BY
5	Category performance ranking	Subquery, RANK() window function
6	Above-average spending customers	Correlated subquery, HAVING
7	City-wise revenue	JOIN, GROUP BY
8	Order status and cancellation breakdown	Aggregation, subquery

The SQL queries are stored in:

sql/analysis_queries.sql

The results are saved to:

outputs/sql_query_results.txt

Example Results

Example results from the current generated dataset:

* Total revenue from fulfilled orders: Rs. 2,259,427.95
* Average order value: Rs. 8,012.16
* Repeat customer rate: 77.0%
* Top category by revenue: Fashion

These values may change if the synthetic dataset is regenerated.

Technologies Used

* Python — data processing and analysis
* Pandas — data cleaning and manipulation
* NumPy — numerical calculations and statistics
* Matplotlib — data visualization
* SQL — business analysis and querying
* SQLite — relational database
* Git/GitHub — version control and project management

Dataset Note

All data in this project is synthetically generated. No real customer or personally identifiable information is used.
