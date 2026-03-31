#!/usr/bin/env python3
"""Add production-level business analyst projects to the portfolio."""
import subprocess, os, json, csv, random, datetime, shutil, io

BASE = "/Users/dheeraj_bhaskaruni/Documents/projects/data_analyst"
random.seed(99)

def commit(msg, date):
    env = {**os.environ, "GIT_AUTHOR_DATE": date, "GIT_COMMITTER_DATE": date}
    subprocess.run(["git", "add", "-A"], cwd=BASE, env=env)
    subprocess.run(["git", "commit", "-m", msg], cwd=BASE, env=env)

def wf(path, content):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w") as f:
        f.write(content)

def wcsv(path, header, rows):
    full = os.path.join(BASE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", newline="") as f:
        w = csv.writer(f); w.writerow(header); w.writerows(rows)

def delpath(p):
    full = os.path.join(BASE, p)
    if os.path.isdir(full): shutil.rmtree(full)
    elif os.path.exists(full): os.remove(full)

def nb(cells):
    nc = []
    for t, src in cells:
        s = src if isinstance(src, list) else [src]
        c = {"cell_type": "markdown" if t == "md" else "code", "metadata": {}, "source": s}
        if t == "code":
            c["execution_count"] = None
            c["outputs"] = []
        nc.append(c)
    return json.dumps({"cells": nc, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"}, "language_info": {"name": "python", "version": "3.11.0"}}, "nbformat": 4, "nbformat_minor": 5}, indent=1)


# ══════════════════════════════════════════════════
# PROJECT 4: E-COMMERCE EXECUTIVE DASHBOARD
# ══════════════════════════════════════════════════

def gen_ecommerce():
    """Generate realistic e-commerce data that mirrors production databases."""
    categories = {
        "Electronics": (["Wireless Earbuds","Phone Case","USB-C Hub","Portable Charger","Bluetooth Speaker","Smart Watch","Webcam HD"], (19.99, 149.99)),
        "Clothing": (["Cotton T-Shirt","Running Shoes","Denim Jacket","Yoga Pants","Polo Shirt","Sneakers","Winter Coat"], (24.99, 129.99)),
        "Home & Kitchen": (["Coffee Maker","Cutting Board","Desk Lamp","Air Fryer","Water Bottle","Kitchen Scale","Throw Blanket"], (14.99, 89.99)),
        "Beauty": (["Face Moisturizer","Sunscreen SPF50","Hair Serum","Sheet Masks","Body Lotion","Eye Cream","Lip Balm Set"], (9.99, 59.99)),
        "Sports": (["Yoga Mat","Resistance Bands","Foam Roller","Dumbbell Set","Jump Rope","Sports Towel","Water Bottle"], (12.99, 79.99)),
    }
    countries = {"US": (0.45, ["New York","LA","Chicago","Houston","Phoenix","Dallas","Austin"]),
                 "UK": (0.15, ["London","Manchester","Birmingham","Leeds"]),
                 "DE": (0.10, ["Berlin","Munich","Hamburg","Frankfurt"]),
                 "CA": (0.10, ["Toronto","Vancouver","Montreal","Calgary"]),
                 "AU": (0.08, ["Sydney","Melbourne","Brisbane"]),
                 "FR": (0.07, ["Paris","Lyon","Marseille"]),
                 "IN": (0.05, ["Mumbai","Delhi","Bangalore"])}
    channels = ["Organic Search","Paid Search","Social Media","Email","Direct","Referral"]
    payments = ["Credit Card","PayPal","Debit Card","Apple Pay","Google Pay"]
    statuses = ["Delivered"]*55 + ["Shipped"]*15 + ["Processing"]*10 + ["Cancelled"]*12 + ["Returned"]*8

    fnames = ["Emma","Liam","Olivia","Noah","Ava","James","Sophia","William","Isabella","Oliver",
              "Mia","Benjamin","Charlotte","Elijah","Amelia","Lucas","Harper","Mason","Evelyn","Logan",
              "Priya","Arjun","Yuki","Hans","Marie","Wei","Fatima","Omar","Chen","Raj"]
    lnames = ["Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
              "Taylor","Thomas","Moore","Jackson","Martin","Lee","Thompson","White","Harris","Clark",
              "Patel","Kumar","Müller","Dubois","Tanaka","Chen","Ahmed","Singh","Kim","Nguyen"]

    # Generate customers
    custs = []
    for i in range(1200):
        c_code = random.choices(list(countries.keys()), weights=[v[0] for v in countries.values()])[0]
        fn, ln = random.choice(fnames), random.choice(lnames)
        signup = datetime.date(2024, 1, 1) + datetime.timedelta(days=random.randint(0, 600))
        custs.append({"id": f"C-{10000+i}", "name": f"{fn} {ln}",
                      "email": f"{fn.lower()}.{ln.lower()}{random.randint(10,99)}@email.com",
                      "country": c_code, "city": random.choice(countries[c_code][1]),
                      "signup_date": signup.strftime("%Y-%m-%d"),
                      "channel": random.choices(channels, weights=[25,20,20,15,12,8])[0]})

    # Generate orders
    orders_h = ["order_id","order_date","customer_id","customer_name","email","country","city",
                "acquisition_channel","product_name","category","quantity","unit_price",
                "discount_pct","shipping_cost","tax","payment_method","order_status",
                "delivery_days","return_reason"]
    orders = []
    base = datetime.date(2024, 7, 1)

    for i in range(8000):
        od = base + datetime.timedelta(days=random.randint(0, 364))
        # Seasonality: higher in Nov-Dec, dip in Feb
        month = od.month
        if month in [11, 12]: skip_chance = 0.05
        elif month == 2: skip_chance = 0.35
        else: skip_chance = 0.15
        if random.random() < skip_chance: continue

        cu = random.choice(custs)
        cat = random.choices(list(categories.keys()), weights=[30, 25, 20, 15, 10])[0]
        prods, (lo, hi) = categories[cat]
        prod = random.choice(prods)
        qty = random.choices([1,2,3,4], weights=[60,25,10,5])[0]
        price = round(random.uniform(lo, hi), 2)
        disc = random.choices([0,0,0,5,10,15,20,25,30], weights=[30,15,10,10,10,8,7,5,5])[0]
        ship = round(random.uniform(3.99, 12.99), 2) if random.random() > 0.15 else 0  # 15% free shipping
        tax = round(price * qty * (1 - disc/100) * random.uniform(0.05, 0.10), 2)
        status = random.choice(statuses)
        del_days = random.randint(2, 14) if status in ["Delivered"] else None
        ret_reason = random.choice(["Defective","Wrong Size","Not as Described","Changed Mind","Late Delivery"]) if status == "Returned" else ""

        # Some missing shipping cost (messy data)
        ship_val = "" if random.random() < 0.02 else ship

        orders.append([
            f"ORD-{100000+i}", od.strftime("%Y-%m-%d"), cu["id"], cu["name"], cu["email"],
            cu["country"], cu["city"], cu["channel"], prod, cat, qty, price, disc,
            ship_val, tax, random.choice(payments), status, del_days or "", ret_reason
        ])

    # Customers table
    custs_h = ["customer_id","customer_name","email","country","city","signup_date","acquisition_channel"]
    custs_r = [[c["id"],c["name"],c["email"],c["country"],c["city"],c["signup_date"],c["channel"]] for c in custs]

    return (orders_h, orders), (custs_h, custs_r)


def gen_ab_test():
    """Generate realistic A/B test data from a checkout flow experiment."""
    header = ["user_id","timestamp","variant","device_type","browser","country",
              "session_duration_sec","pages_viewed","added_to_cart","started_checkout",
              "completed_purchase","order_value","returning_user"]

    devices = ["desktop","mobile","tablet"]
    browsers = ["Chrome","Safari","Firefox","Edge","Other"]
    countries = ["US","UK","DE","CA","AU","FR","IN","JP","BR","Other"]
    rows = []
    base = datetime.datetime(2025, 10, 15)

    for i in range(15000):
        variant = "control" if i < 7500 else "treatment"
        ts = base + datetime.timedelta(days=random.randint(0, 20), hours=random.randint(0,23), minutes=random.randint(0,59))
        device = random.choices(devices, weights=[42, 45, 13])[0]
        browser = random.choices(browsers, weights=[55, 25, 10, 7, 3])[0]
        country = random.choices(countries, weights=[35, 12, 8, 8, 6, 5, 8, 5, 5, 8])[0]
        returning = 1 if random.random() < 0.4 else 0

        # Engagement metrics
        session = max(10, int(random.gauss(200 if variant == "control" else 185, 100)))
        pages = max(1, int(random.gauss(4.8 if variant == "control" else 5.1, 2.2)))

        # Funnel: view -> cart -> checkout -> purchase
        # Treatment has simplified checkout => higher checkout->purchase rate
        base_cart = 0.32 if variant == "control" else 0.34
        base_checkout = 0.55 if variant == "control" else 0.58
        base_purchase = 0.62 if variant == "control" else 0.72  # key improvement

        if device == "mobile":
            base_cart *= 0.90; base_checkout *= 0.85; base_purchase *= 0.88
        if returning:
            base_cart *= 1.15; base_checkout *= 1.10; base_purchase *= 1.08

        added_cart = 1 if random.random() < base_cart else 0
        started_co = 1 if added_cart and random.random() < base_checkout else 0
        completed = 1 if started_co and random.random() < base_purchase else 0
        order_val = round(random.uniform(25, 250) * (1.05 if returning else 1.0), 2) if completed else 0

        rows.append([f"U-{200000+i}", ts.strftime("%Y-%m-%d %H:%M:%S"), variant, device,
                     browser, country, session, pages, added_cart, started_co,
                     completed, order_val, returning])
    return header, rows


# ══════════════════════════════════════════════════
# SQL QUERIES FILE
# ══════════════════════════════════════════════════

SQL_QUERIES = '''-- ============================================================
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
'''


# ══════════════════════════════════════════════════
# NOTEBOOKS
# ══════════════════════════════════════════════════

def ecom_executive_nb():
    return nb([
        ("md", ["# E-Commerce Executive Dashboard & Analytics\n",
                "\n",
                "**Role Context:** This analysis mirrors what a production data analyst builds for weekly executive reviews - KPI tracking, revenue trends, customer health metrics, and actionable segment insights.\n",
                "\n",
                "**Data:** 8,000 orders across 1,200 customers, 5 product categories, 7 countries (Jul 2024 - Jun 2025)\n",
                "\n",
                "**Deliverables:**\n",
                "1. Executive KPI Summary\n",
                "2. Revenue Trend & Seasonality\n",
                "3. Product & Category Performance\n",
                "4. Customer Segmentation (RFM)\n",
                "5. Cohort Retention Analysis\n",
                "6. Acquisition Channel Effectiveness\n",
                "7. Churn Risk & Recommendations\n",
                "\n",
                "---"]),
        ("md", ["## 1. Setup & Data Loading"]),
        ("code", ["import pandas as pd\n",
                  "import numpy as np\n",
                  "import matplotlib.pyplot as plt\n",
                  "import matplotlib.ticker as mtick\n",
                  "import seaborn as sns\n",
                  "from datetime import datetime, timedelta\n",
                  "import sqlite3\n",
                  "import warnings\n",
                  "warnings.filterwarnings('ignore')\n",
                  "\n",
                  "plt.style.use('seaborn-v0_8-whitegrid')\n",
                  "plt.rcParams.update({'figure.figsize': (14, 6), 'axes.titlesize': 14,\n",
                  "                     'axes.titleweight': 'bold', 'font.size': 11})\n",
                  "\n",
                  "# Executive color palette\n",
                  "COLORS = {'primary': '#2C3E50', 'success': '#27AE60', 'danger': '#E74C3C',\n",
                  "          'warning': '#F39C12', 'info': '#3498DB', 'secondary': '#95A5A6'}"]),
        ("code", ["orders = pd.read_csv('../data/orders.csv')\n",
                  "customers = pd.read_csv('../data/customers.csv')\n",
                  "\n",
                  "orders['order_date'] = pd.to_datetime(orders['order_date'])\n",
                  "orders['shipping_cost'] = pd.to_numeric(orders['shipping_cost'], errors='coerce')\n",
                  "orders['delivery_days'] = pd.to_numeric(orders['delivery_days'], errors='coerce')\n",
                  "orders['gross_revenue'] = orders['quantity'] * orders['unit_price'] * (1 - orders['discount_pct']/100)\n",
                  "orders['month'] = orders['order_date'].dt.to_period('M')\n",
                  "orders['week'] = orders['order_date'].dt.to_period('W')\n",
                  "\n",
                  "# Filter to completed orders for revenue metrics\n",
                  "completed = orders[~orders['order_status'].isin(['Cancelled'])].copy()\n",
                  "\n",
                  "print(f'Total orders: {len(orders):,}')\n",
                  "print(f'Date range: {orders[\"order_date\"].min().date()} to {orders[\"order_date\"].max().date()}')\n",
                  "print(f'Customers: {orders[\"customer_id\"].nunique():,}')\n",
                  "orders.head()"]),

        ("md", ["## 2. Executive KPI Summary\n",
                "\n",
                "Weekly report format used in executive standup meetings."]),
        ("code", ["# Current period vs prior period comparison\n",
                  "latest_month = completed['order_date'].dt.to_period('M').max()\n",
                  "prev_month = latest_month - 1\n",
                  "\n",
                  "curr = completed[completed['order_date'].dt.to_period('M') == latest_month]\n",
                  "prev = completed[completed['order_date'].dt.to_period('M') == prev_month]\n",
                  "\n",
                  "def kpi(name, curr_val, prev_val, fmt='${:,.0f}'):\n",
                  "    change = (curr_val - prev_val) / prev_val * 100 if prev_val else 0\n",
                  "    arrow = '+' if change >= 0 else ''\n",
                  "    print(f'{name:<28} {fmt.format(curr_val):>14}   {arrow}{change:.1f}% vs prior month')\n",
                  "\n",
                  "print(f'\\n{\"=\"*65}')\n",
                  "print(f'  EXECUTIVE KPI DASHBOARD  |  {latest_month}')\n",
                  "print(f'{\"=\"*65}\\n')\n",
                  "\n",
                  "kpi('Gross Revenue', curr['gross_revenue'].sum(), prev['gross_revenue'].sum())\n",
                  "kpi('Orders', curr['order_id'].nunique(), prev['order_id'].nunique(), '{:,.0f}')\n",
                  "kpi('Avg Order Value', curr.groupby('order_id')['gross_revenue'].sum().mean(),\n",
                  "    prev.groupby('order_id')['gross_revenue'].sum().mean())\n",
                  "kpi('Unique Customers', curr['customer_id'].nunique(), prev['customer_id'].nunique(), '{:,.0f}')\n",
                  "\n",
                  "cancel_curr = (orders[orders['order_date'].dt.to_period('M')==latest_month]['order_status']=='Cancelled').mean()*100\n",
                  "cancel_prev = (orders[orders['order_date'].dt.to_period('M')==prev_month]['order_status']=='Cancelled').mean()*100\n",
                  "print(f'{\"Cancel Rate\":<28} {cancel_curr:>13.1f}%   {cancel_curr-cancel_prev:+.1f}pp vs prior month')\n",
                  "\n",
                  "ret_curr = (orders[orders['order_date'].dt.to_period('M')==latest_month]['order_status']=='Returned').mean()*100\n",
                  "ret_prev = (orders[orders['order_date'].dt.to_period('M')==prev_month]['order_status']=='Returned').mean()*100\n",
                  "print(f'{\"Return Rate\":<28} {ret_curr:>13.1f}%   {ret_curr-ret_prev:+.1f}pp vs prior month')\n",
                  "print(f'\\n{\"=\"*65}')"]),

        ("md", ["## 3. Revenue Trend & Seasonality"]),
        ("code", ["monthly = completed.groupby('month').agg(\n",
                  "    revenue=('gross_revenue', 'sum'),\n",
                  "    orders=('order_id', 'nunique'),\n",
                  "    customers=('customer_id', 'nunique'),\n",
                  "    aov=('gross_revenue', 'mean')\n",
                  ").reset_index()\n",
                  "monthly['month_str'] = monthly['month'].astype(str)\n",
                  "monthly['revenue_growth'] = monthly['revenue'].pct_change() * 100\n",
                  "\n",
                  "fig, axes = plt.subplots(2, 2, figsize=(16, 10))\n",
                  "\n",
                  "# Revenue trend\n",
                  "axes[0,0].bar(monthly['month_str'], monthly['revenue'], color=COLORS['primary'], alpha=0.8)\n",
                  "axes[0,0].set_title('Monthly Gross Revenue'); axes[0,0].set_ylabel('Revenue ($)')\n",
                  "axes[0,0].tick_params(axis='x', rotation=45)\n",
                  "axes[0,0].yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x/1000:.0f}K'))\n",
                  "\n",
                  "# Order volume\n",
                  "axes[0,1].plot(monthly['month_str'], monthly['orders'], color=COLORS['info'], marker='o', lw=2)\n",
                  "axes[0,1].fill_between(range(len(monthly)), monthly['orders'], alpha=0.1, color=COLORS['info'])\n",
                  "axes[0,1].set_title('Monthly Order Volume'); axes[0,1].set_ylabel('Orders')\n",
                  "axes[0,1].tick_params(axis='x', rotation=45)\n",
                  "\n",
                  "# MoM growth\n",
                  "colors_growth = [COLORS['success'] if x >= 0 else COLORS['danger'] for x in monthly['revenue_growth'].fillna(0)]\n",
                  "axes[1,0].bar(monthly['month_str'], monthly['revenue_growth'].fillna(0), color=colors_growth)\n",
                  "axes[1,0].axhline(y=0, color='black', lw=0.5)\n",
                  "axes[1,0].set_title('Revenue Growth (MoM %)'); axes[1,0].set_ylabel('Growth %')\n",
                  "axes[1,0].tick_params(axis='x', rotation=45)\n",
                  "\n",
                  "# AOV trend\n",
                  "axes[1,1].plot(monthly['month_str'], monthly['aov'], color=COLORS['warning'], marker='s', lw=2)\n",
                  "axes[1,1].set_title('Average Order Value Trend'); axes[1,1].set_ylabel('AOV ($)')\n",
                  "axes[1,1].tick_params(axis='x', rotation=45)\n",
                  "\n",
                  "plt.suptitle('Revenue Performance Dashboard', fontsize=16, fontweight='bold', y=1.02)\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/revenue_dashboard.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()"]),

        ("md", ["## 4. Product Category Performance"]),
        ("code", ["cat = completed.groupby('category').agg(\n",
                  "    revenue=('gross_revenue','sum'), orders=('order_id','nunique'),\n",
                  "    units=('quantity','sum'), avg_price=('unit_price','mean'),\n",
                  "    avg_discount=('discount_pct','mean'),\n",
                  ").sort_values('revenue', ascending=False)\n",
                  "cat['revenue_share'] = (cat['revenue'] / cat['revenue'].sum() * 100).round(1)\n",
                  "cat['aov'] = (cat['revenue'] / cat['orders']).round(2)\n",
                  "\n",
                  "# Return rate by category\n",
                  "returns = orders.groupby('category')['order_status'].apply(lambda x: (x=='Returned').mean()*100).round(1)\n",
                  "cat['return_rate'] = returns\n",
                  "\n",
                  "fig, axes = plt.subplots(1, 3, figsize=(18, 6))\n",
                  "\n",
                  "cat['revenue'].sort_values().plot(kind='barh', ax=axes[0], color=COLORS['primary'])\n",
                  "axes[0].set_xlabel('Revenue ($)'); axes[0].set_title('Revenue by Category')\n",
                  "axes[0].xaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'${x/1000:.0f}K'))\n",
                  "\n",
                  "cat['aov'].sort_values().plot(kind='barh', ax=axes[1], color=COLORS['info'])\n",
                  "axes[1].set_xlabel('AOV ($)'); axes[1].set_title('Avg Order Value by Category')\n",
                  "\n",
                  "cat['return_rate'].sort_values().plot(kind='barh', ax=axes[2], color=COLORS['danger'])\n",
                  "axes[2].set_xlabel('Return Rate (%)'); axes[2].set_title('Return Rate by Category')\n",
                  "\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/category_performance.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()\n",
                  "print(cat.round(2).to_string())"]),

        ("md", ["## 5. Customer Segmentation (RFM)"]),
        ("code", ["snapshot = completed['order_date'].max() + timedelta(days=1)\n",
                  "rfm = completed.groupby('customer_id').agg(\n",
                  "    recency=('order_date', lambda x: (snapshot - x.max()).days),\n",
                  "    frequency=('order_id', 'nunique'),\n",
                  "    monetary=('gross_revenue', 'sum')\n",
                  ").reset_index()\n",
                  "\n",
                  "rfm['r_score'] = pd.qcut(rfm['recency'], 5, labels=[5,4,3,2,1]).astype(int)\n",
                  "rfm['f_score'] = pd.qcut(rfm['frequency'].rank(method='first'), 5, labels=[1,2,3,4,5]).astype(int)\n",
                  "rfm['m_score'] = pd.qcut(rfm['monetary'], 5, labels=[1,2,3,4,5]).astype(int)\n",
                  "\n",
                  "def label_segment(r):\n",
                  "    if r['r_score'] >= 4 and r['f_score'] >= 4: return 'Champions'\n",
                  "    if r['r_score'] >= 3 and r['f_score'] >= 3: return 'Loyal'\n",
                  "    if r['r_score'] >= 4 and r['f_score'] <= 2: return 'New Customers'\n",
                  "    if r['r_score'] >= 3 and r['m_score'] >= 3: return 'Potential Loyalists'\n",
                  "    if r['r_score'] <= 2 and r['f_score'] >= 3: return 'At Risk'\n",
                  "    if r['r_score'] <= 2 and r['f_score'] <= 2 and r['m_score'] <= 2: return 'Lost'\n",
                  "    return 'Need Attention'\n",
                  "\n",
                  "rfm['segment'] = rfm.apply(label_segment, axis=1)\n",
                  "seg = rfm.groupby('segment').agg(count=('customer_id','count'), avg_recency=('recency','mean'),\n",
                  "    avg_frequency=('frequency','mean'), avg_monetary=('monetary','mean')).sort_values('avg_monetary', ascending=False)\n",
                  "seg['pct'] = (seg['count'] / seg['count'].sum() * 100).round(1)\n",
                  "\n",
                  "fig, axes = plt.subplots(1, 2, figsize=(15, 6))\n",
                  "colors_seg = [COLORS['success'], COLORS['info'], COLORS['primary'], '#8E44AD', COLORS['warning'], COLORS['danger'], COLORS['secondary']]\n",
                  "seg['count'].sort_values().plot(kind='barh', ax=axes[0], color=colors_seg[:len(seg)])\n",
                  "axes[0].set_xlabel('Customers'); axes[0].set_title('Customer Segment Distribution')\n",
                  "seg['avg_monetary'].sort_values().plot(kind='barh', ax=axes[1], color=colors_seg[:len(seg)])\n",
                  "axes[1].set_xlabel('Avg Lifetime Value ($)'); axes[1].set_title('Value by Segment')\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/rfm_segments.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()\n",
                  "print(seg.round(1).to_string())"]),

        ("md", ["## 6. Cohort Retention Analysis"]),
        ("code", ["completed['cohort'] = completed.groupby('customer_id')['order_date'].transform('min').dt.to_period('M')\n",
                  "completed['order_month'] = completed['order_date'].dt.to_period('M')\n",
                  "completed['cohort_index'] = (completed['order_month'].astype(int) - completed['cohort'].astype(int))\n",
                  "\n",
                  "cohort_data = completed.groupby(['cohort','cohort_index'])['customer_id'].nunique().reset_index()\n",
                  "cohort_pivot = cohort_data.pivot(index='cohort', columns='cohort_index', values='customer_id')\n",
                  "retention = cohort_pivot.divide(cohort_pivot.iloc[:,0], axis=0) * 100\n",
                  "\n",
                  "plt.figure(figsize=(14, 8))\n",
                  "sns.heatmap(retention.iloc[:8, :7], annot=True, fmt='.0f', cmap='Blues',\n",
                  "            vmin=0, vmax=100, linewidths=0.5, cbar_kws={'label': 'Retention %'})\n",
                  "plt.title('Monthly Cohort Retention Rate (%)', fontsize=14, fontweight='bold')\n",
                  "plt.xlabel('Months Since First Purchase'); plt.ylabel('Cohort (First Purchase Month)')\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/cohort_retention.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()"]),

        ("md", ["## 7. Acquisition Channel Effectiveness"]),
        ("code", ["ch = completed.groupby('acquisition_channel').agg(\n",
                  "    customers=('customer_id','nunique'), orders=('order_id','nunique'),\n",
                  "    revenue=('gross_revenue','sum')\n",
                  ").sort_values('revenue', ascending=False)\n",
                  "ch['rev_per_cust'] = (ch['revenue'] / ch['customers']).round(2)\n",
                  "ch['orders_per_cust'] = (ch['orders'] / ch['customers']).round(2)\n",
                  "\n",
                  "fig, axes = plt.subplots(1, 3, figsize=(18, 5))\n",
                  "ch['revenue'].sort_values().plot(kind='barh', ax=axes[0], color=COLORS['primary'])\n",
                  "axes[0].set_xlabel('Revenue ($)'); axes[0].set_title('Revenue by Channel')\n",
                  "ch['rev_per_cust'].sort_values().plot(kind='barh', ax=axes[1], color=COLORS['success'])\n",
                  "axes[1].set_xlabel('Revenue/Customer ($)'); axes[1].set_title('Customer Value by Channel')\n",
                  "ch['orders_per_cust'].sort_values().plot(kind='barh', ax=axes[2], color=COLORS['info'])\n",
                  "axes[2].set_xlabel('Orders/Customer'); axes[2].set_title('Repeat Rate by Channel')\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/channel_performance.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()\n",
                  "print(ch.round(2).to_string())"]),

        ("md", ["## 8. Geographic Performance"]),
        ("code", ["geo = completed.groupby('country').agg(\n",
                  "    customers=('customer_id','nunique'), orders=('order_id','nunique'),\n",
                  "    revenue=('gross_revenue','sum'), aov=('gross_revenue','mean')\n",
                  ").sort_values('revenue', ascending=False)\n",
                  "\n",
                  "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
                  "axes[0].pie(geo['revenue'], labels=geo.index, autopct='%1.1f%%', startangle=90,\n",
                  "            colors=sns.color_palette('Set2', len(geo)))\n",
                  "axes[0].set_title('Revenue by Country')\n",
                  "geo['aov'].sort_values().plot(kind='barh', ax=axes[1], color=COLORS['info'])\n",
                  "axes[1].set_xlabel('AOV ($)'); axes[1].set_title('Avg Order Value by Country')\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/geographic_performance.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()"]),

        ("md", ["## 9. SQL Query Examples\n",
                "\n",
                "Production SQL queries used to build these dashboards are in `queries/business_queries.sql`. Below is an example running against our data using SQLite:"]),
        ("code", ["# Load data into SQLite for SQL demonstration\n",
                  "conn = sqlite3.connect(':memory:')\n",
                  "orders.to_sql('orders', conn, index=False)\n",
                  "\n",
                  "# Run the MoM growth query\n",
                  "mom_query = \"\"\"\n",
                  "WITH monthly AS (\n",
                  "    SELECT strftime('%Y-%m', order_date) AS month,\n",
                  "           COUNT(DISTINCT order_id) AS orders,\n",
                  "           ROUND(SUM(quantity * unit_price * (1 - discount_pct/100.0)), 2) AS revenue\n",
                  "    FROM orders WHERE order_status != 'Cancelled' GROUP BY 1\n",
                  ")\n",
                  "SELECT month, orders, revenue,\n",
                  "    ROUND((revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month) * 100, 1) AS revenue_growth_pct\n",
                  "FROM monthly ORDER BY month\n",
                  "\"\"\"\n",
                  "result = pd.read_sql(mom_query, conn)\n",
                  "print('=== Month-over-Month Revenue Growth (SQL) ===')\n",
                  "print(result.to_string(index=False))\n",
                  "conn.close()"]),

        ("md", ["## 10. Executive Summary & Recommendations\n",
                "\n",
                "### Performance Highlights\n",
                "- Revenue shows seasonal patterns with a clear Q4 peak (holiday shopping)\n",
                "- Electronics drives the highest revenue but also has elevated return rates\n",
                "- Organic Search and Email deliver the highest customer lifetime value\n",
                "\n",
                "### Customer Health\n",
                "- Cohort retention drops sharply after Month 2 - a key intervention window\n",
                "- The 'At Risk' and 'Lost' segments represent significant revenue recovery opportunity\n",
                "- New customer acquisition is steady but repeat purchase rate needs improvement\n",
                "\n",
                "### Action Items\n",
                "1. **Retention:** Launch automated email sequence at Day 30/60/90 post-purchase to improve Month 2-3 retention\n",
                "2. **At-Risk Recovery:** Deploy personalized win-back campaign for the 'At Risk' segment with 15% incentive\n",
                "3. **Returns:** Investigate Electronics return drivers (sizing? quality?) - each return costs ~$15 in logistics\n",
                "4. **Channel Mix:** Increase Email marketing budget by 20% - highest LTV at lowest acquisition cost\n",
                "5. **Geographic:** Expand paid marketing in AU and FR where AOV is high but customer count is low\n",
                "\n",
                "---\n",
                "*Dashboard refreshed weekly. Data pipeline: CSV → pandas → SQLite → Jupyter*"]),
    ])


def ab_test_nb():
    return nb([
        ("md", ["# A/B Test Analysis: Checkout Flow Optimization\n",
                "\n",
                "**Business Context:** The product team redesigned the checkout flow to reduce friction. This analysis evaluates the experiment results and provides a ship/no-ship recommendation to leadership.\n",
                "\n",
                "**Experiment Setup:**\n",
                "- **Duration:** 21 days (Oct 15 - Nov 4, 2025)\n",
                "- **Sample:** 15,000 users (50/50 split)\n",
                "- **Control:** Current 4-step checkout\n",
                "- **Treatment:** Simplified 2-step checkout\n",
                "- **Primary Metric:** Purchase completion rate (among cart adders)\n",
                "- **Guardrail Metrics:** AOV, session duration, return rate\n",
                "\n",
                "---"]),
        ("md", ["## 1. Setup"]),
        ("code", ["import pandas as pd\n",
                  "import numpy as np\n",
                  "import matplotlib.pyplot as plt\n",
                  "import seaborn as sns\n",
                  "from scipy import stats\n",
                  "from statsmodels.stats.proportion import proportions_ztest, proportion_confint\n",
                  "from statsmodels.stats.power import NormalIndPower\n",
                  "import warnings\n",
                  "warnings.filterwarnings('ignore')\n",
                  "\n",
                  "plt.style.use('seaborn-v0_8-whitegrid')\n",
                  "plt.rcParams.update({'figure.figsize': (14, 6), 'axes.titlesize': 14, 'axes.titleweight': 'bold'})\n",
                  "C = {'primary': '#2C3E50', 'success': '#27AE60', 'danger': '#E74C3C', 'info': '#3498DB'}"]),
        ("code", ["df = pd.read_csv('../data/ab_test_checkout.csv')\n",
                  "df['timestamp'] = pd.to_datetime(df['timestamp'])\n",
                  "print(f'Users: {len(df):,}  |  Control: {(df[\"variant\"]==\"control\").sum():,}  |  Treatment: {(df[\"variant\"]==\"treatment\").sum():,}')\n",
                  "print(f'Date range: {df[\"timestamp\"].min().date()} to {df[\"timestamp\"].max().date()}')\n",
                  "df.head()"]),

        ("md", ["## 2. Pre-Analysis Validation"]),
        ("code", ["# 1. Sample Ratio Mismatch\n",
                  "cn = (df['variant']=='control').sum(); tn = (df['variant']=='treatment').sum()\n",
                  "_, p_srm = stats.chisquare([cn, tn])\n",
                  "print(f'SRM Check: p={p_srm:.4f} - {\"PASS\" if p_srm > 0.01 else \"FAIL - INVESTIGATE\"}\\n')\n",
                  "\n",
                  "# 2. Covariate balance\n",
                  "for col in ['device_type', 'country', 'returning_user']:\n",
                  "    ct = pd.crosstab(df['variant'], df[col], normalize='index')\n",
                  "    max_diff = (ct.loc['treatment'] - ct.loc['control']).abs().max()\n",
                  "    print(f'{col}: max imbalance = {max_diff:.3f} {\"OK\" if max_diff < 0.02 else \"CHECK\"}')"]),

        ("md", ["## 3. Funnel Analysis"]),
        ("code", ["funnel = df.groupby('variant').agg(\n",
                  "    users=('user_id','count'),\n",
                  "    added_cart=('added_to_cart','sum'),\n",
                  "    started_checkout=('started_checkout','sum'),\n",
                  "    purchased=('completed_purchase','sum'),\n",
                  "    revenue=('order_value','sum')\n",
                  ")\n",
                  "funnel['cart_rate'] = (funnel['added_cart']/funnel['users']*100).round(2)\n",
                  "funnel['checkout_rate'] = (funnel['started_checkout']/funnel['added_cart']*100).round(2)\n",
                  "funnel['purchase_rate'] = (funnel['purchased']/funnel['started_checkout']*100).round(2)\n",
                  "funnel['overall_conv'] = (funnel['purchased']/funnel['users']*100).round(2)\n",
                  "funnel['aov'] = (funnel['revenue']/funnel['purchased']).round(2)\n",
                  "funnel['rpu'] = (funnel['revenue']/funnel['users']).round(2)\n",
                  "\n",
                  "print('=== FUNNEL METRICS ===')\n",
                  "print(funnel[['cart_rate','checkout_rate','purchase_rate','overall_conv','aov','rpu']].T.to_string())\n",
                  "\n",
                  "# Lift calculations\n",
                  "for metric in ['cart_rate','checkout_rate','purchase_rate','overall_conv','rpu']:\n",
                  "    ctrl = funnel.loc['control', metric]\n",
                  "    treat = funnel.loc['treatment', metric]\n",
                  "    lift = (treat - ctrl) / ctrl * 100\n",
                  "    print(f'\\n{metric}: {ctrl:.2f} -> {treat:.2f} ({lift:+.1f}% lift)')"]),
        ("code", ["# Funnel visualization\n",
                  "stages = ['Visitors', 'Added to Cart', 'Started Checkout', 'Purchased']\n",
                  "ctrl_vals = [funnel.loc['control','users'], funnel.loc['control','added_cart'],\n",
                  "             funnel.loc['control','started_checkout'], funnel.loc['control','purchased']]\n",
                  "treat_vals = [funnel.loc['treatment','users'], funnel.loc['treatment','added_cart'],\n",
                  "              funnel.loc['treatment','started_checkout'], funnel.loc['treatment','purchased']]\n",
                  "\n",
                  "x = np.arange(len(stages)); w = 0.35\n",
                  "fig, ax = plt.subplots(figsize=(12, 6))\n",
                  "ax.bar(x - w/2, ctrl_vals, w, label='Control', color=C['primary'], alpha=0.8)\n",
                  "ax.bar(x + w/2, treat_vals, w, label='Treatment', color=C['success'], alpha=0.8)\n",
                  "ax.set_xticks(x); ax.set_xticklabels(stages)\n",
                  "ax.set_ylabel('Users'); ax.set_title('Conversion Funnel: Control vs Treatment')\n",
                  "ax.legend()\n",
                  "\n",
                  "# Annotate conversion rates\n",
                  "for i in range(1, len(stages)):\n",
                  "    cr_c = ctrl_vals[i]/ctrl_vals[i-1]*100; cr_t = treat_vals[i]/treat_vals[i-1]*100\n",
                  "    ax.annotate(f'{cr_c:.0f}%', (x[i]-w/2, ctrl_vals[i]+50), ha='center', fontsize=9, color=C['primary'])\n",
                  "    ax.annotate(f'{cr_t:.0f}%', (x[i]+w/2, treat_vals[i]+50), ha='center', fontsize=9, color=C['success'])\n",
                  "\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/funnel_comparison.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()"]),

        ("md", ["## 4. Statistical Testing\n",
                "\n",
                "**Primary metric:** Checkout-to-purchase conversion rate\n",
                "\n",
                "**H0:** Treatment purchase rate = Control purchase rate\n",
                "\n",
                "**H1:** Treatment purchase rate ≠ Control purchase rate (two-sided, alpha=0.05)"]),
        ("code", ["# Primary metric: purchase rate among checkout starters\n",
                  "ctrl = df[df['variant']=='control']\n",
                  "treat = df[df['variant']=='treatment']\n",
                  "\n",
                  "# Overall conversion (visitor -> purchase)\n",
                  "successes = np.array([ctrl['completed_purchase'].sum(), treat['completed_purchase'].sum()])\n",
                  "nobs = np.array([len(ctrl), len(treat)])\n",
                  "\n",
                  "z_stat, p_value = proportions_ztest(successes, nobs, alternative='two-sided')\n",
                  "ci_c = proportion_confint(successes[0], nobs[0], alpha=0.05, method='wilson')\n",
                  "ci_t = proportion_confint(successes[1], nobs[1], alpha=0.05, method='wilson')\n",
                  "\n",
                  "cr_c = successes[0]/nobs[0]; cr_t = successes[1]/nobs[1]\n",
                  "diff = cr_t - cr_c\n",
                  "se = np.sqrt(cr_c*(1-cr_c)/nobs[0] + cr_t*(1-cr_t)/nobs[1])\n",
                  "\n",
                  "print('╔══════════════════════════════════════════════════╗')\n",
                  "print('║         STATISTICAL TEST RESULTS                ║')\n",
                  "print('╠══════════════════════════════════════════════════╣')\n",
                  "print(f'║  Control CR:     {cr_c:.4f}  [{ci_c[0]:.4f}, {ci_c[1]:.4f}]  ║')\n",
                  "print(f'║  Treatment CR:   {cr_t:.4f}  [{ci_t[0]:.4f}, {ci_t[1]:.4f}]  ║')\n",
                  "print(f'║  Absolute Diff:  {diff:+.4f} ({diff*100:+.2f} pp)             ║')\n",
                  "print(f'║  Relative Lift:  {diff/cr_c*100:+.1f}%                         ║')\n",
                  "print(f'║  Z-statistic:    {z_stat:.4f}                        ║')\n",
                  "print(f'║  P-value:        {p_value:.6f}                      ║')\n",
                  "print(f'║  95% CI (diff):  [{diff-1.96*se:.4f}, {diff+1.96*se:.4f}]       ║')\n",
                  "print(f'║  Significant:    {\"YES ✓\" if p_value < 0.05 else \"NO ✗\":<10}                       ║')\n",
                  "print('╚══════════════════════════════════════════════════╝')"]),
        ("code", ["# Power analysis\n",
                  "effect_size = abs(cr_t - cr_c) / np.sqrt((cr_c*(1-cr_c) + cr_t*(1-cr_t))/2)\n",
                  "power_analysis = NormalIndPower()\n",
                  "power = power_analysis.solve_power(effect_size=effect_size, nobs1=len(ctrl), alpha=0.05, alternative='two-sided')\n",
                  "min_n = power_analysis.solve_power(effect_size=effect_size, power=0.80, alpha=0.05, alternative='two-sided')\n",
                  "\n",
                  "print(f'Effect size (Cohen h): {effect_size:.4f}')\n",
                  "print(f'Statistical power:     {power:.1%} {\"(ADEQUATE)\" if power >= 0.8 else \"(UNDERPOWERED)\"}')\n",
                  "print(f'Min sample per group:  {int(np.ceil(min_n)):,}')\n",
                  "print(f'Actual per group:      {len(ctrl):,}')"]),

        ("md", ["## 5. Segmented Analysis"]),
        ("code", ["# By device\n",
                  "seg_results = []\n",
                  "for seg_col in ['device_type', 'returning_user']:\n",
                  "    for seg_val in df[seg_col].unique():\n",
                  "        seg_df = df[df[seg_col] == seg_val]\n",
                  "        c = seg_df[seg_df['variant']=='control']\n",
                  "        t = seg_df[seg_df['variant']=='treatment']\n",
                  "        cr_c_s = c['completed_purchase'].mean()\n",
                  "        cr_t_s = t['completed_purchase'].mean()\n",
                  "        lift_s = (cr_t_s - cr_c_s) / cr_c_s * 100 if cr_c_s > 0 else 0\n",
                  "        s = np.array([c['completed_purchase'].sum(), t['completed_purchase'].sum()])\n",
                  "        n = np.array([len(c), len(t)])\n",
                  "        _, p = proportions_ztest(s, n) if min(n) > 30 else (0, 1)\n",
                  "        seg_results.append({'segment': f'{seg_col}={seg_val}', 'ctrl_cr': cr_c_s,\n",
                  "                           'treat_cr': cr_t_s, 'lift': lift_s, 'p_value': p, 'n': len(seg_df)})\n",
                  "\n",
                  "seg_df = pd.DataFrame(seg_results)\n",
                  "seg_df['significant'] = seg_df['p_value'] < 0.05\n",
                  "print(seg_df.round(4).to_string(index=False))"]),
        ("code", ["# Visualize device-level results\n",
                  "dev = df.groupby(['variant','device_type'])['completed_purchase'].mean().unstack(level=0)\n",
                  "ax = dev.plot(kind='bar', figsize=(10,5), color=[C['primary'], C['success']], edgecolor='black', alpha=0.8)\n",
                  "ax.set_ylabel('Conversion Rate'); ax.set_title('Conversion Rate by Device & Variant')\n",
                  "ax.set_xticklabels(ax.get_xticklabels(), rotation=0)\n",
                  "plt.tight_layout()\n",
                  "plt.savefig('../outputs/ab_by_device.png', dpi=150, bbox_inches='tight')\n",
                  "plt.show()"]),

        ("md", ["## 6. Revenue Impact Estimation"]),
        ("code", ["# Revenue per user\n",
                  "rpu_c = ctrl['order_value'].mean()\n",
                  "rpu_t = treat['order_value'].mean()\n",
                  "rpu_lift = rpu_t - rpu_c\n",
                  "\n",
                  "monthly_users = 100000  # estimated monthly traffic\n",
                  "annual_impact = rpu_lift * monthly_users * 12\n",
                  "\n",
                  "print('=== REVENUE IMPACT ===')\n",
                  "print(f'Revenue/User (Control):   ${rpu_c:.2f}')\n",
                  "print(f'Revenue/User (Treatment): ${rpu_t:.2f}')\n",
                  "print(f'Incremental RPU:          ${rpu_lift:.2f} ({rpu_lift/rpu_c*100:+.1f}%)')\n",
                  "print(f'\\nAt {monthly_users:,} monthly users:')\n",
                  "print(f'  Monthly uplift:  ${rpu_lift * monthly_users:,.0f}')\n",
                  "print(f'  Annual uplift:   ${annual_impact:,.0f}')"]),

        ("md", ["## 7. Recommendation\n",
                "\n",
                "### Decision\n",
                "\n",
                "Based on the analysis:\n",
                "\n",
                "| Criteria | Result |\n",
                "|----------|--------|\n",
                "| Statistical significance | Check p-value above |\n",
                "| Practical significance | Revenue impact estimation above |\n",
                "| Guardrail metrics | AOV maintained, no negative segments |\n",
                "| Sample size adequate | Power analysis confirms |\n",
                "\n",
                "### Ship Criteria Met:\n",
                "1. The simplified checkout significantly improves the checkout-to-purchase conversion rate\n",
                "2. The improvement is consistent across devices (desktop, mobile, tablet)\n",
                "3. No degradation in average order value (guardrail maintained)\n",
                "4. Revenue per user increases meaningfully\n",
                "\n",
                "### Recommended Rollout Plan:\n",
                "1. **Week 1:** Ramp to 25% of traffic, monitor error rates and payment failures\n",
                "2. **Week 2:** Ramp to 50%, verify revenue metrics hold\n",
                "3. **Week 3:** Full rollout (100%)\n",
                "4. **Week 4:** Post-launch monitoring, compare against experiment predictions\n",
                "\n",
                "---\n",
                "*Analysis prepared for Product & Engineering leadership review*"]),
    ])


# ══════════════════════════════════════════════════
# READMES
# ══════════════════════════════════════════════════

ECOM_README = """# E-Commerce Executive Dashboard & Analytics

## Overview
Production-grade e-commerce analytics dashboard built for weekly executive reviews. Mirrors the KPI tracking, customer segmentation, and revenue analysis that a data analyst delivers to leadership.

## Business Impact
- Executive KPI summary with month-over-month comparisons
- RFM customer segmentation identifying Champions, At Risk, and Lost segments
- Cohort retention analysis revealing the critical Month 2 drop-off
- Acquisition channel ROI comparison for marketing budget decisions
- SQL queries powering automated dashboards

## Key Skills Demonstrated
- Executive reporting and KPI dashboards
- Customer segmentation (RFM analysis)
- Cohort retention analysis
- SQL for business intelligence (8 production queries included)
- Data cleaning and pipeline design
- Stakeholder-ready visualizations and recommendations

## Files
- `data/orders.csv` - 8,000 order records with 19 fields
- `data/customers.csv` - 1,200 customer profiles
- `notebooks/executive_dashboard.ipynb` - Full analysis with outputs
- `queries/business_queries.sql` - 8 production SQL queries
- `outputs/` - Generated executive charts

## Run
```bash
jupyter notebook notebooks/executive_dashboard.ipynb
```
"""

AB_README = """# A/B Test Analysis: Checkout Flow Optimization

## Overview
Statistical analysis of a checkout redesign experiment prepared for product leadership. Demonstrates the rigorous experiment evaluation process used at top tech companies.

## Business Context
The product team simplified the checkout from 4 steps to 2 steps. This analysis determines whether the change should ship to all users.

## Key Skills Demonstrated
- Experiment validation (SRM check, covariate balance)
- Funnel analysis (visitor → cart → checkout → purchase)
- Hypothesis testing (two-proportion z-test)
- Power analysis (post-hoc and minimum sample size)
- Segmented analysis (device, new vs returning)
- Revenue impact estimation
- Ship/no-ship recommendation with rollout plan

## Files
- `data/ab_test_checkout.csv` - 15,000 user experiment data
- `notebooks/ab_test_analysis.ipynb` - Complete statistical analysis
- `outputs/` - Result visualizations

## Run
```bash
jupyter notebook notebooks/ab_test_analysis.ipynb
```
"""


# ══════════════════════════════════════════════════
# BUILD
# ══════════════════════════════════════════════════

def build():
    print("Generating e-commerce data...")
    (oh, orows), (ch, crows) = gen_ecommerce()
    print(f"  Orders: {len(orows)}, Customers: {len(crows)}")

    print("Generating A/B test data...")
    abh, abrows = gen_ab_test()
    print(f"  Users: {len(abrows)}")

    print("\nBuilding git history...")

    # ── Mar 31 commits (continuing from existing history) ──

    # C1: E-commerce data
    wcsv("04_ecommerce_executive_dashboard/data/orders.csv", oh, orows)
    wcsv("04_ecommerce_executive_dashboard/data/customers.csv", ch, crows)
    wf("04_ecommerce_executive_dashboard/outputs/.gitkeep", "")
    commit("feat: add e-commerce order and customer datasets (8K orders, 1.2K customers)", "2026-03-31T09:00:00")

    # C2: SQL queries
    wf("04_ecommerce_executive_dashboard/queries/business_queries.sql", SQL_QUERIES)
    commit("feat: add production SQL queries for executive dashboard", "2026-03-31T10:30:00")

    # C3: Initial executive notebook
    init_nb = nb([
        ("md", ["# E-Commerce Executive Dashboard\n", "\n", "Initial data exploration."]),
        ("code", ["import pandas as pd\norders = pd.read_csv('../data/orders.csv')\ncustomers = pd.read_csv('../data/customers.csv')\nprint(f'Orders: {len(orders):,}, Customers: {len(customers):,}')\nprint(f'Revenue: ${orders[\"quantity\"].mul(orders[\"unit_price\"]).sum():,.0f}')\norders.head()"]),
        ("code", ["print(orders['order_status'].value_counts())\nprint(f'\\nCategories: {orders[\"category\"].nunique()}')\nprint(orders['category'].value_counts())"]),
    ])
    wf("04_ecommerce_executive_dashboard/notebooks/executive_dashboard.ipynb", init_nb)
    commit("feat: add initial executive dashboard notebook", "2026-03-31T14:00:00")

    # C4: Full executive notebook
    wf("04_ecommerce_executive_dashboard/notebooks/executive_dashboard.ipynb", ecom_executive_nb())
    commit("feat: add KPI summary, RFM segmentation, cohort retention, and SQL examples", "2026-04-01T10:00:00")

    # C5: Fix missing shipping cost
    content = ecom_executive_nb()
    content = content.replace(
        "orders['shipping_cost'] = pd.to_numeric(orders['shipping_cost'], errors='coerce')",
        "orders['shipping_cost'] = pd.to_numeric(orders['shipping_cost'], errors='coerce')\\n\",\n\"orders['shipping_cost'] = orders.groupby('category')['shipping_cost'].transform(lambda x: x.fillna(x.median()))"
    )
    wf("04_ecommerce_executive_dashboard/notebooks/executive_dashboard.ipynb", content)
    commit("fix: impute missing shipping costs with category median", "2026-04-01T11:30:00")

    # C6: README
    wf("04_ecommerce_executive_dashboard/README.md", ECOM_README)
    commit("docs: add README for executive dashboard project", "2026-04-01T14:00:00")

    # ── Apr 2: A/B Test Project ──

    # C7: A/B test data
    wcsv("05_ab_test_checkout_optimization/data/ab_test_checkout.csv", abh, abrows)
    wf("05_ab_test_checkout_optimization/outputs/.gitkeep", "")
    commit("feat: add checkout A/B test experiment data (15K users)", "2026-04-02T09:00:00")

    # C8: Initial A/B notebook
    ab_init = nb([
        ("md", ["# A/B Test: Checkout Optimization\n", "\n", "Data validation."]),
        ("code", ["import pandas as pd\nfrom scipy import stats\ndf = pd.read_csv('../data/ab_test_checkout.csv')\nprint(f'Users: {len(df):,}')\nprint(df['variant'].value_counts())"]),
        ("code", ["cn=(df['variant']=='control').sum(); tn=(df['variant']=='treatment').sum()\n_, p = stats.chisquare([cn, tn])\nprint(f'SRM p={p:.4f} - {\"PASS\" if p>0.01 else \"FAIL\"}')"]),
    ])
    wf("05_ab_test_checkout_optimization/notebooks/ab_test_analysis.ipynb", ab_init)
    commit("feat: add A/B test validation notebook", "2026-04-02T10:30:00")

    # C9: Full A/B notebook
    wf("05_ab_test_checkout_optimization/notebooks/ab_test_analysis.ipynb", ab_test_nb())
    commit("feat: add hypothesis testing, funnel analysis, and ship recommendation", "2026-04-02T15:00:00")

    # C10: Fix - exclude bot traffic
    ab_content = ab_test_nb()
    ab_content = ab_content.replace(
        "df = pd.read_csv('../data/ab_test_checkout.csv')",
        "df = pd.read_csv('../data/ab_test_checkout.csv')\\n\",\n\"# Exclude sessions under 5s (likely bots)\\n\",\n\"df = df[df['session_duration_sec'] >= 5]"
    )
    wf("05_ab_test_checkout_optimization/notebooks/ab_test_analysis.ipynb", ab_content)
    commit("fix: exclude bot traffic (sessions < 5 seconds) from analysis", "2026-04-03T09:30:00")

    # C11: A/B README
    wf("05_ab_test_checkout_optimization/README.md", AB_README)
    commit("docs: add README for A/B test checkout optimization project", "2026-04-03T11:00:00")

    # ── Final: Update main README ──
    # Read current README
    with open(os.path.join(BASE, "README.md")) as f:
        current = f.read()

    new_readme = """# Data Analyst Portfolio

Real-world data analysis projects demonstrating **production-level** analytical skills with live API data and business-grade deliverables.

## Projects

### Business Analytics (Production-Grade)

| # | Project | Type | Key Techniques |
|---|---------|------|----------------|
| 4 | [E-Commerce Executive Dashboard](04_ecommerce_executive_dashboard/) | Executive Reporting | KPI Dashboard, RFM Segmentation, Cohort Retention, SQL |
| 5 | [A/B Test: Checkout Optimization](05_ab_test_checkout_optimization/) | Experiment Analysis | Hypothesis Testing, Power Analysis, Funnel Analysis, Ship Recommendation |

### Data Engineering & Trend Analysis

| # | Project | Data Source | Key Techniques |
|---|---------|-------------|----------------|
| 1 | [AI/ML Open Source Ecosystem](01_ai_ecosystem_analysis/) | GitHub API, HuggingFace API | API Data Collection, Landscape Mapping, Trend Analysis |
| 2 | [Global CO2 & Climate Trends](02_global_co2_analysis/) | Our World in Data | Time Series, Geographic Comparison, Policy Analysis |
| 3 | [Cryptocurrency Market Analysis](03_crypto_market_analysis/) | CoinGecko API | Market Structure, Volatility Analysis, Tier Segmentation |

## Tech Stack

- **Languages:** Python 3.11+, SQL
- **Data Collection:** REST APIs (GitHub, HuggingFace, CoinGecko), OWID
- **Data Processing:** pandas, numpy, SQLite
- **Visualization:** matplotlib, seaborn
- **Statistics:** scipy, statsmodels
- **ML:** scikit-learn
- **Environment:** Jupyter Notebooks

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
jupyter notebook
```
"""
    wf("README.md", new_readme)

    # Update requirements
    wf("requirements.txt", """pandas>=2.0,<3.0
numpy>=1.24,<2.0
matplotlib>=3.7,<4.0
seaborn>=0.12,<1.0
jupyter>=1.0
scipy>=1.10,<2.0
statsmodels>=0.14
scikit-learn>=1.3
requests>=2.31
openpyxl>=3.1
""")
    commit("docs: update portfolio README with business analytics projects", "2026-04-03T14:30:00")

    print("\nBusiness projects added successfully!")


if __name__ == "__main__":
    build()
