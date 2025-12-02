-- ================================================================
-- 02_core_kpis.sql
-- Core Financial KPIs, Time-based P&L, Customer Analytics
-- ================================================================

---------------------------------------------------------
-- DAILY METRICS
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_revenue_daily AS
SELECT
    t.date_key,
    dt.date,
    SUM(t.net_revenue) AS revenue
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;

CREATE OR REPLACE VIEW vw_cogs_daily AS
SELECT
    t.date_key,
    dt.date,
    SUM(t.direct_cost) AS cogs
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2;

CREATE OR REPLACE VIEW vw_margin_daily AS
SELECT
    r.date_key,
    r.date,
    r.revenue,
    c.cogs,
    r.revenue - c.cogs AS gross_margin,
    (r.revenue - c.cogs) / NULLIF(r.revenue,0) AS gross_margin_pct
FROM vw_revenue_daily r
LEFT JOIN vw_cogs_daily c USING(date_key);

---------------------------------------------------------
-- MONTHLY P&L (Revenue / COGS / OPEX)
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_revenue_monthly AS
SELECT
    dt.year,
    dt.month,
    dt.year_month_key,
    dt.year_month_label,
    SUM(t.net_revenue) AS revenue
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2,3,4;

CREATE OR REPLACE VIEW vw_cogs_monthly AS
SELECT
    dt.year,
    dt.month,
    dt.year_month_key,
    dt.year_month_label,
    SUM(t.direct_cost) AS cogs
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2,3,4;

CREATE OR REPLACE VIEW vw_opex_monthly AS
SELECT
    dt.year,
    dt.month,
    dt.year_month_key,
    dt.year_month_label,
    SUM(f.amount) * -1 AS opex
FROM fact_financials f
JOIN dim_time dt USING(date_key)
JOIN dim_account a USING(account_id)
WHERE a.account_type = 'OPEX'
GROUP BY 1,2,3,4;

CREATE OR REPLACE VIEW vw_pnl_monthly AS
SELECT
    r.year,
    r.month,
    r.year_month_key,
    r.year_month_label,
    r.revenue,
    c.cogs,
    r.revenue - c.cogs AS gross_margin,
    o.opex,
    r.revenue - c.cogs - o.opex AS operating_profit
FROM vw_revenue_monthly r
JOIN vw_cogs_monthly c USING(year_month_key)
LEFT JOIN vw_opex_monthly o USING(year_month_key);

---------------------------------------------------------
-- CUSTOMER PROFITABILITY (UPDATED WITH REVENUE BANDS)
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_customer_profitability AS
SELECT
    c.customer_id,
    c.segment,
    c.region,

    SUM(t.net_revenue) AS total_revenue,
    SUM(t.direct_cost) AS total_cogs,
    SUM(t.net_revenue) - SUM(t.direct_cost) AS gross_margin,
    (SUM(t.net_revenue) - SUM(t.direct_cost)) / NULLIF(SUM(t.net_revenue), 0) AS gross_margin_pct,

    -- Revenue Band
    CASE
        WHEN SUM(t.net_revenue) < 1000 THEN '<1K'
        WHEN SUM(t.net_revenue) < 5000 THEN '1K–5K'
        WHEN SUM(t.net_revenue) < 10000 THEN '5K–10K'
        WHEN SUM(t.net_revenue) < 50000 THEN '10K–50K'
        WHEN SUM(t.net_revenue) < 200000 THEN '50K–200K'
        ELSE '200K+'
    END AS revenue_band,

    -- Sort key for band ordering
    CASE
        WHEN SUM(t.net_revenue) < 1000 THEN 1
        WHEN SUM(t.net_revenue) < 5000 THEN 2
        WHEN SUM(t.net_revenue) < 10000 THEN 3
        WHEN SUM(t.net_revenue) < 50000 THEN 4
        WHEN SUM(t.net_revenue) < 200000 THEN 5
        ELSE 6
    END AS revenue_band_sort

FROM fact_transactions t
JOIN dim_customer c USING (customer_id)
GROUP BY 1,2,3;


---------------------------------------------------------
-- CUSTOMER ACTIVITY BY MONTH
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_customer_activity_monthly AS
SELECT
    c.customer_id,
    dt.year,
    dt.month,
    dt.year_month_key,
    dt.year_month_label,
    SUM(t.net_revenue) AS revenue,
    SUM(t.direct_cost) AS cogs,
    COUNT(*) AS num_transactions
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
JOIN dim_customer c USING(customer_id)
GROUP BY 1,2,3,4,5;

---------------------------------------------------------
-- SEGMENT SUMMARY
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_segment_summary AS
SELECT
    segment,
    COUNT(*) AS num_customers,
    SUM(total_revenue) AS total_revenue,
    SUM(gross_margin) AS total_gross_margin,
    AVG(gross_margin_pct) AS avg_gm_pct
FROM vw_customer_profitability
GROUP BY 1;
