-- ==========================================
-- 03_transform_core.sql (DuckDB compatible)
-- ==========================================

-- ==========================================
-- 1. Revenue Daily View
-- ==========================================
CREATE OR REPLACE VIEW vw_revenue_daily AS
SELECT
    t.date_key,
    dt.date,
    SUM(t.net_revenue) AS revenue
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;


-- ==========================================
-- 2. COGS Daily View
-- ==========================================
CREATE OR REPLACE VIEW vw_cogs_daily AS
SELECT
    t.date_key,
    dt.date,
    SUM(t.direct_cost) AS cogs
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;


-- ==========================================
-- 3. Margin Daily View
-- ==========================================
CREATE OR REPLACE VIEW vw_margin_daily AS
SELECT
    r.date_key,
    r.date,
    r.revenue,
    c.cogs * -1 AS cogs,
    r.revenue - (c.cogs * -1) AS gross_margin,
    (r.revenue - (c.cogs * -1)) / NULLIF(r.revenue, 0) AS gross_margin_pct
FROM vw_revenue_daily r
LEFT JOIN vw_cogs_daily c USING(date_key);


-- ==========================================
-- 4. OPEX Monthly
-- ==========================================
CREATE OR REPLACE VIEW vw_opex_monthly AS
SELECT
    dt.year,
    dt.month,
    SUM(f.amount) * -1 AS opex
FROM fact_financials f
JOIN dim_time dt USING(date_key)
JOIN dim_account a USING(account_id)
WHERE a.account_type = 'OPEX'
GROUP BY 1,2;


-- ==========================================
-- 5. Revenue Monthly
-- ==========================================
CREATE OR REPLACE VIEW vw_revenue_monthly AS
SELECT
    dt.year,
    dt.month,
    SUM(t.net_revenue) AS revenue
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;


-- ==========================================
-- 6. COGS Monthly
-- ==========================================
CREATE OR REPLACE VIEW vw_cogs_monthly AS
SELECT
    dt.year,
    dt.month,
    SUM(t.direct_cost) AS cogs
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;


-- ==========================================
-- 7. Monthly P&L
-- ==========================================
CREATE OR REPLACE VIEW vw_pnl_monthly AS
SELECT
    r.year,
    r.month,
    r.revenue,
    c.cogs,
    r.revenue - c.cogs AS gross_margin,
    o.opex,
    r.revenue - c.cogs - o.opex AS operating_profit
FROM vw_revenue_monthly r
JOIN vw_cogs_monthly c USING(year, month)
LEFT JOIN vw_opex_monthly o USING(year, month);


-- ==========================================
-- 8. Customer Profitability
-- ==========================================
CREATE OR REPLACE VIEW vw_customer_profitability AS
SELECT
    c.customer_id,
    c.segment,
    c.region,
    SUM(t.net_revenue) AS total_revenue,
    SUM(t.direct_cost) AS total_cogs,
    SUM(t.net_revenue) - SUM(t.direct_cost) AS gross_margin,
    (SUM(t.net_revenue) - SUM(t.direct_cost)) 
        / NULLIF(SUM(t.net_revenue), 0) AS gross_margin_pct
FROM fact_transactions t
JOIN dim_customer c USING(customer_id)
GROUP BY 1,2,3;


-- ==========================================
-- 9. Customer Activity by Month
-- ==========================================
CREATE OR REPLACE VIEW vw_customer_activity_monthly AS
SELECT
    c.customer_id,
    dt.year,
    dt.month,
    SUM(t.net_revenue) AS revenue,
    SUM(t.direct_cost) AS cogs,
    COUNT(*) AS num_transactions
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
JOIN dim_customer c USING(customer_id)
GROUP BY 1,2,3;


-- ==========================================
-- 10. Segment Summary
-- ==========================================
CREATE OR REPLACE VIEW vw_segment_summary AS
SELECT
    segment,
    COUNT(*) AS num_customers,
    SUM(total_revenue) AS total_revenue,
    SUM(gross_margin) AS total_gross_margin,
    AVG(gross_margin_pct) AS avg_gm_pct
FROM vw_customer_profitability
GROUP BY 1;


-- ==========================================
-- 11. Periodic Revenue Views (YTD / QTD / MTD / LTM)
-- ==========================================

CREATE OR REPLACE VIEW vw_revenue_ytd AS
SELECT
    dt.year,
    SUM(t.net_revenue) AS revenue_ytd
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1;

CREATE OR REPLACE VIEW vw_revenue_qtd AS
SELECT
    dt.year,
    dt.quarter,
    SUM(t.net_revenue) AS revenue_qtd
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;

CREATE OR REPLACE VIEW vw_revenue_mtd AS
SELECT
    dt.year,
    dt.month,
    SUM(t.net_revenue) AS revenue_mtd
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;

CREATE OR REPLACE VIEW vw_revenue_ltm AS
WITH monthly AS (
    SELECT
        dt.year,
        dt.month,
        SUM(t.net_revenue) AS revenue
    FROM fact_transactions t
    JOIN dim_time dt USING(date_key)
    GROUP BY 1,2
)
SELECT
    year,
    month,
    SUM(revenue) OVER (
        ORDER BY year, month
        ROWS BETWEEN 11 PRECEDING AND CURRENT ROW
    ) AS revenue_ltm
FROM monthly;
