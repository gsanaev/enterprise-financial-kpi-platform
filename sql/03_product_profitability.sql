-- ================================================================
-- 03_product_profitability.sql
-- Product Revenue, Revenue Share, OPEX Allocation, Profitability
-- ================================================================

---------------------------------------------------------
-- PRODUCT REVENUE BY MONTH
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_product_revenue_monthly AS
SELECT
    p.product_id,
    dt.year,
    dt.month,
    dt.year_month_key,
    dt.year_month_label,
    SUM(t.net_revenue) AS product_revenue
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
JOIN dim_product p USING(product_id)
GROUP BY 1,2,3,4,5;

CREATE OR REPLACE VIEW vw_total_revenue_monthly AS
SELECT
    year_month_key,
    year,
    month,
    year_month_label,
    SUM(product_revenue) AS total_revenue
FROM vw_product_revenue_monthly
GROUP BY 1,2,3,4;

CREATE OR REPLACE VIEW vw_product_revenue_share AS
SELECT
    pr.product_id,
    pr.year,
    pr.month,
    pr.year_month_key,
    pr.year_month_label,
    pr.product_revenue,
    tr.total_revenue,
    pr.product_revenue / NULLIF(tr.total_revenue,0) AS revenue_share
FROM vw_product_revenue_monthly pr
JOIN vw_total_revenue_monthly tr USING(year_month_key);

---------------------------------------------------------
-- OPEX ALLOCATION
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_opex_total_monthly AS
SELECT
    year_month_key,
    year,
    month,
    year_month_label,
    SUM(opex) AS opex_total
FROM vw_opex_monthly
GROUP BY 1,2,3,4;

CREATE OR REPLACE VIEW vw_product_opex_allocated AS
SELECT
    rs.product_id,
    rs.year,
    rs.month,
    rs.year_month_key,
    rs.year_month_label,
    rs.revenue_share,
    om.opex_total,
    rs.revenue_share * om.opex_total AS opex_allocated
FROM vw_product_revenue_share rs
LEFT JOIN vw_opex_total_monthly om USING(year_month_key);

---------------------------------------------------------
-- PRODUCT PROFITABILITY
---------------------------------------------------------

CREATE OR REPLACE VIEW vw_product_profitability AS
SELECT
    p.product_id,
    p.product_name,
    pr.year,
    pr.month,
    pr.year_month_key,
    pr.year_month_label,
    pr.product_revenue,
    SUM(t.direct_cost) AS cogs,
    pa.opex_allocated,
    pr.product_revenue - SUM(t.direct_cost) AS gross_margin,
    pr.product_revenue - SUM(t.direct_cost) - pa.opex_allocated AS operating_profit
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
JOIN dim_product p USING(product_id)
JOIN vw_product_revenue_monthly pr
  ON pr.product_id = p.product_id
 AND pr.year_month_key = dt.year_month_key
JOIN vw_product_opex_allocated pa
  ON pa.product_id = p.product_id
 AND pa.year_month_key = dt.year_month_key
GROUP BY
    p.product_id,
    p.product_name,
    pr.year,
    pr.month,
    pr.year_month_key,
    pr.year_month_label,
    pr.product_revenue,
    pa.opex_allocated;
