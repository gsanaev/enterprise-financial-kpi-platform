-- ================================================================
-- 03_product_profitability.sql
-- Product Revenue, COGS, Revenue Share, OPEX Allocation, Profitability
-- ================================================================


---------------------------------------------------------
-- 1. PRODUCT REVENUE + COGS BY MONTH  (CLEAN, NO DUPLICATION)
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_product_pnl_monthly AS
SELECT
    t.product_id,
    dt.year,
    dt.month,
    dt.year_month_key,
    dt.year_month_label,
    SUM(t.net_revenue) AS product_revenue,
    SUM(t.direct_cost) AS product_cogs,
    SUM(t.net_revenue) - SUM(t.direct_cost) AS product_gross_margin
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
GROUP BY 1,2,3,4,5;


---------------------------------------------------------
-- 2. TOTAL REVENUE PER MONTH
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_total_revenue_monthly AS
SELECT
    year_month_key,
    SUM(product_revenue) AS total_revenue
FROM vw_product_pnl_monthly
GROUP BY 1;


---------------------------------------------------------
-- 3. PRODUCT REVENUE SHARE (PER MONTH)
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_product_revenue_share AS
SELECT
    pnl.product_id,
    pnl.year,
    pnl.month,
    pnl.year_month_key,
    pnl.year_month_label,
    pnl.product_revenue,
    pnl.product_cogs,
    pnl.product_gross_margin,
    tr.total_revenue,
    pnl.product_revenue / NULLIF(tr.total_revenue, 0) AS revenue_share
FROM vw_product_pnl_monthly pnl
JOIN vw_total_revenue_monthly tr USING (year_month_key);


---------------------------------------------------------
-- 4. TOTAL OPEX PER MONTH  (POSITIVE VALUE)
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_opex_total_monthly AS
SELECT
    dt.year,
    dt.month,
    dt.year_month_key,
    dt.year_month_label,
    SUM(f.amount) * -1 AS opex_total
FROM fact_financials f
JOIN dim_time dt USING(date_key)
JOIN dim_account a USING(account_id)
WHERE a.account_type = 'OPEX'
GROUP BY 1,2,3,4;


---------------------------------------------------------
-- 5. ALLOCATE OPEX TO PRODUCTS BY REVENUE SHARE
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_product_opex_allocated AS
SELECT
    rs.product_id,
    rs.year,
    rs.month,
    rs.year_month_key,
    rs.year_month_label,
    rs.product_revenue,
    rs.product_cogs,
    rs.product_gross_margin,
    rs.revenue_share,
    om.opex_total,
    rs.revenue_share * om.opex_total AS opex_allocated
FROM vw_product_revenue_share rs
LEFT JOIN vw_opex_total_monthly om USING (year_month_key);


---------------------------------------------------------
-- 6. FINAL PRODUCT PROFITABILITY (NO CARTESIAN JOINS)
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_product_profitability AS
SELECT
    p.product_id,
    prod.product_name,
    p.year,
    p.month,
    p.year_month_key,
    p.year_month_label,

    -- Financials
    p.product_revenue,
    p.product_cogs,
    p.product_gross_margin,
    p.opex_allocated,

    -- Operating Profit
    p.product_gross_margin - p.opex_allocated AS operating_profit

FROM vw_product_opex_allocated p
JOIN dim_product prod USING (product_id);
