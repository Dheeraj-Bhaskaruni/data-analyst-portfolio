-- ============================================================
-- Business Intelligence SQL Queries
-- E-Commerce Analytics - Production Query Examples
-- ============================================================

-- These queries demonstrate the SQL patterns used to build
-- executive dashboards and ad-hoc business analysis.
-- Adapted for SQLite (can run on the CSV data via pandas read_sql).

-- ============================================================
-- 1. EXECUTIVE KPI SUMMARY (Weekly Report)
-- ============================================================
SELECT
    strftime('%Y-%W', order_date) AS week,
    COUNT(DISTINCT order_id) AS total_orders,
    COUNT(DISTINCT customer_id) AS unique_customers,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS gross_revenue,
    ROUND(AVG(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS avg_order_value,
    ROUND(SUM(CASE WHEN order_status = 'Cancelled' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS cancel_rate_pct,
    ROUND(SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS return_rate_pct
FROM orders
WHERE order_status != 'Cancelled'
GROUP BY 1
ORDER BY 1 DESC
LIMIT 12;


-- ============================================================
-- 2. CUSTOMER COHORT RETENTION (Monthly Cohorts)
-- ============================================================
WITH first_purchase AS (
    SELECT
        customer_id,
        MIN(strftime('%Y-%m', order_date)) AS cohort_month
    FROM orders
    WHERE order_status NOT IN ('Cancelled')
    GROUP BY customer_id
),
monthly_activity AS (
    SELECT
        o.customer_id,
        fp.cohort_month,
        strftime('%Y-%m', o.order_date) AS activity_month,
        (CAST(strftime('%Y', o.order_date) AS INT) - CAST(strftime('%Y', fp.cohort_month || '-01') AS INT)) * 12
        + (CAST(strftime('%m', o.order_date) AS INT) - CAST(strftime('%m', fp.cohort_month || '-01') AS INT)) AS month_number
    FROM orders o
    JOIN first_purchase fp ON o.customer_id = fp.customer_id
    WHERE o.order_status NOT IN ('Cancelled')
)
SELECT
    cohort_month,
    month_number,
    COUNT(DISTINCT customer_id) AS active_customers
FROM monthly_activity
WHERE month_number BETWEEN 0 AND 6
GROUP BY cohort_month, month_number
ORDER BY cohort_month, month_number;


-- ============================================================
-- 3. RFM SEGMENTATION
-- ============================================================
WITH rfm_raw AS (
    SELECT
        customer_id,
        CAST(julianday('2025-07-01') - julianday(MAX(order_date)) AS INT) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS monetary
    FROM orders
    WHERE order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY customer_id
),
rfm_scored AS (
    SELECT *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS f_score,
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score
    FROM rfm_raw
)
SELECT
    CASE
        WHEN r_score >= 4 AND f_score >= 4 AND m_score >= 4 THEN 'Champions'
        WHEN r_score >= 3 AND f_score >= 3 THEN 'Loyal'
        WHEN r_score >= 4 AND f_score <= 2 THEN 'New Customers'
        WHEN r_score <= 2 AND f_score >= 3 THEN 'At Risk'
        WHEN r_score <= 2 AND f_score <= 2 AND m_score <= 2 THEN 'Lost'
        ELSE 'Need Attention'
    END AS segment,
    COUNT(*) AS customer_count,
    ROUND(AVG(recency_days), 0) AS avg_recency,
    ROUND(AVG(frequency), 1) AS avg_frequency,
    ROUND(AVG(monetary), 2) AS avg_monetary
FROM rfm_scored
GROUP BY 1
ORDER BY avg_monetary DESC;


-- ============================================================
-- 4. PRODUCT PERFORMANCE REPORT
-- ============================================================
SELECT
    category,
    product_name,
    COUNT(DISTINCT order_id) AS orders,
    SUM(quantity) AS units_sold,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS revenue,
    ROUND(AVG(unit_price), 2) AS avg_price,
    ROUND(AVG(discount_pct), 1) AS avg_discount,
    ROUND(SUM(CASE WHEN order_status = 'Returned' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 1) AS return_rate
FROM orders
WHERE order_status != 'Cancelled'
GROUP BY category, product_name
ORDER BY revenue DESC
LIMIT 20;


-- ============================================================
-- 5. ACQUISITION CHANNEL ROI
-- ============================================================
SELECT
    acquisition_channel,
    COUNT(DISTINCT customer_id) AS customers_acquired,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS total_revenue,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)) / COUNT(DISTINCT customer_id), 2) AS revenue_per_customer,
    ROUND(COUNT(DISTINCT order_id) * 1.0 / COUNT(DISTINCT customer_id), 2) AS orders_per_customer
FROM orders
WHERE order_status NOT IN ('Cancelled')
GROUP BY acquisition_channel
ORDER BY total_revenue DESC;


-- ============================================================
-- 6. GEOGRAPHIC REVENUE BREAKDOWN
-- ============================================================
SELECT
    country,
    city,
    COUNT(DISTINCT customer_id) AS customers,
    COUNT(DISTINCT order_id) AS orders,
    ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS revenue,
    ROUND(AVG(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS avg_order_value
FROM orders
WHERE order_status NOT IN ('Cancelled')
GROUP BY country, city
ORDER BY revenue DESC
LIMIT 15;


-- ============================================================
-- 7. MONTH-OVER-MONTH GROWTH
-- ============================================================
WITH monthly AS (
    SELECT
        strftime('%Y-%m', order_date) AS month,
        COUNT(DISTINCT order_id) AS orders,
        ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS revenue
    FROM orders
    WHERE order_status NOT IN ('Cancelled')
    GROUP BY 1
)
SELECT
    month,
    orders,
    revenue,
    ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100, 1) AS revenue_growth_pct,
    ROUND((orders - LAG(orders) OVER (ORDER BY month)) * 100.0 / LAG(orders) OVER (ORDER BY month), 1) AS order_growth_pct
FROM monthly
ORDER BY month;


-- ============================================================
-- 8. CUSTOMER LIFETIME VALUE (SIMPLE)
-- ============================================================
SELECT
    CASE
        WHEN order_count = 1 THEN '1 order'
        WHEN order_count BETWEEN 2 AND 3 THEN '2-3 orders'
        WHEN order_count BETWEEN 4 AND 6 THEN '4-6 orders'
        ELSE '7+ orders'
    END AS purchase_frequency,
    COUNT(*) AS customers,
    ROUND(AVG(total_spend), 2) AS avg_ltv,
    ROUND(AVG(avg_order_value), 2) AS avg_aov,
    ROUND(AVG(customer_lifespan_days), 0) AS avg_lifespan_days
FROM (
    SELECT
        customer_id,
        COUNT(DISTINCT order_id) AS order_count,
        SUM(quantity * unit_price * (1 - discount_pct/100.0)) AS total_spend,
        AVG(quantity * unit_price * (1 - discount_pct/100.0)) AS avg_order_value,
        CAST(julianday(MAX(order_date)) - julianday(MIN(order_date)) AS INT) AS customer_lifespan_days
    FROM orders
    WHERE order_status NOT IN ('Cancelled', 'Returned')
    GROUP BY customer_id
) sub
GROUP BY 1
ORDER BY avg_ltv DESC;
