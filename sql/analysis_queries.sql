-- =============================================================================
-- E-COMMERCE CUSTOMER INTELLIGENCE SYSTEM — SQL ANALYSIS
-- Resume bullets covered:
--   "Analyzed customer purchasing behavior using SQL to identify revenue
--    trends, top customers, repeat purchases, and product performance."
--   "Designed and queried a relational database containing customer, order,
--    and product data using JOINs, aggregations, subqueries, and CTEs."
--
-- Run against: database/ecommerce.db  (clean tables: customers, products,
-- orders, order_items — produced by python/data_cleaning_eda.py)
-- =============================================================================


-- -----------------------------------------------------------------------------
-- 0. SCHEMA (for reference)
-- -----------------------------------------------------------------------------
-- customers    (customer_id, customer_name, email, city, signup_date)
-- products     (product_id, product_name, category, price)
-- orders       (order_id, customer_id, order_date, status)
-- order_items  (order_item_id, order_id, product_id, quantity, unit_price, line_revenue)


-- -----------------------------------------------------------------------------
-- 1. REVENUE TRENDS — monthly revenue, using a JOIN + aggregation
-- -----------------------------------------------------------------------------
SELECT
    strftime('%Y-%m', o.order_date)      AS order_month,
    COUNT(DISTINCT o.order_id)           AS total_orders,
    ROUND(SUM(oi.line_revenue), 2)       AS monthly_revenue,
    ROUND(SUM(oi.line_revenue) * 1.0 / COUNT(DISTINCT o.order_id), 2) AS avg_order_value
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY order_month
ORDER BY order_month;


-- -----------------------------------------------------------------------------
-- 2. TOP 10 CUSTOMERS BY REVENUE — JOIN across 3 tables + aggregation
-- -----------------------------------------------------------------------------
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    COUNT(DISTINCT o.order_id)      AS total_orders,
    ROUND(SUM(oi.line_revenue), 2)  AS total_spent
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY c.customer_id, c.customer_name, c.city
ORDER BY total_spent DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 3. REPEAT PURCHASE CUSTOMERS — CTE + HAVING
--    Identify customers with 2+ orders and their repeat-purchase revenue share
-- -----------------------------------------------------------------------------
WITH customer_orders AS (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count
    FROM orders
    GROUP BY customer_id
),
repeat_customers AS (
    SELECT customer_id, order_count
    FROM customer_orders
    WHERE order_count >= 2
)
SELECT
    (SELECT COUNT(*) FROM repeat_customers)                              AS repeat_customer_count,
    (SELECT COUNT(*) FROM customer_orders)                               AS total_customers_with_orders,
    ROUND(
        (SELECT COUNT(*) FROM repeat_customers) * 100.0 /
        (SELECT COUNT(*) FROM customer_orders), 1
    )                                                                    AS repeat_rate_pct;


-- 3b. Detail view: each repeat customer with their order count and total spend
WITH customer_orders AS (
    SELECT customer_id, COUNT(DISTINCT order_id) AS order_count
    FROM orders
    GROUP BY customer_id
)
SELECT
    c.customer_name,
    co.order_count,
    ROUND(SUM(oi.line_revenue), 2) AS total_spent
FROM customer_orders co
JOIN customers c ON c.customer_id = co.customer_id
JOIN orders o     ON o.customer_id = co.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE co.order_count >= 2
  AND o.status IN ('Delivered', 'Shipped')
GROUP BY c.customer_id, c.customer_name, co.order_count
ORDER BY total_spent DESC
LIMIT 10;


-- -----------------------------------------------------------------------------
-- 4. PRODUCT PERFORMANCE — revenue and units sold per product, by category
-- -----------------------------------------------------------------------------
SELECT
    p.category,
    p.product_name,
    SUM(oi.quantity)                AS units_sold,
    ROUND(SUM(oi.line_revenue), 2)  AS total_revenue
FROM order_items oi
JOIN orders o    ON o.order_id = oi.order_id
JOIN products p  ON p.product_id = oi.product_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY p.product_id, p.category, p.product_name
ORDER BY total_revenue DESC
LIMIT 15;


-- -----------------------------------------------------------------------------
-- 5. CATEGORY-LEVEL PERFORMANCE — aggregation with ranking (window function)
-- -----------------------------------------------------------------------------
SELECT
    category,
    total_revenue,
    RANK() OVER (ORDER BY total_revenue DESC) AS revenue_rank
FROM (
    SELECT
        p.category,
        ROUND(SUM(oi.line_revenue), 2) AS total_revenue
    FROM order_items oi
    JOIN orders o   ON o.order_id = oi.order_id
    JOIN products p ON p.product_id = oi.product_id
    WHERE o.status IN ('Delivered', 'Shipped')
    GROUP BY p.category
) category_totals
ORDER BY revenue_rank;


-- -----------------------------------------------------------------------------
-- 6. HIGH-VALUE CUSTOMERS — subquery comparing each customer to the overall
--    average customer spend (correlated aggregation via subquery)
-- -----------------------------------------------------------------------------
SELECT
    c.customer_name,
    ROUND(SUM(oi.line_revenue), 2) AS total_spent
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY c.customer_id, c.customer_name
HAVING SUM(oi.line_revenue) > (
    -- average total spend per customer, computed as a subquery
    SELECT AVG(customer_total)
    FROM (
        SELECT SUM(oi2.line_revenue) AS customer_total
        FROM orders o2
        JOIN order_items oi2 ON oi2.order_id = o2.order_id
        WHERE o2.status IN ('Delivered', 'Shipped')
        GROUP BY o2.customer_id
    )
)
ORDER BY total_spent DESC;


-- -----------------------------------------------------------------------------
-- 7. CITY-WISE REVENUE — where customers are generating the most revenue
-- -----------------------------------------------------------------------------
SELECT
    c.city,
    COUNT(DISTINCT c.customer_id)   AS customers,
    COUNT(DISTINCT o.order_id)      AS orders,
    ROUND(SUM(oi.line_revenue), 2)  AS revenue
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id = o.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY c.city
ORDER BY revenue DESC;


-- -----------------------------------------------------------------------------
-- 8. ORDER STATUS BREAKDOWN — cancellation / return rate
-- -----------------------------------------------------------------------------
SELECT
    status,
    COUNT(*) AS order_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM orders), 1) AS pct_of_total
FROM orders
GROUP BY status
ORDER BY order_count DESC;
