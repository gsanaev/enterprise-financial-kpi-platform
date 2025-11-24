-- ==========================================
-- 04_cost_allocation.sql (Simple MVP, DuckDB)
-- ==========================================

-- ------------------------------------------
-- 1. Monthly revenue per product
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_product_revenue_monthly AS
SELECT
    p.product_id,
    dt.year,
    dt.month,
    SUM(t.net_revenue) AS product_revenue
FROM fact_transactions t
JOIN dim_time dt USING(date_key)
JOIN dim_product p USING(product_id)
GROUP BY 1,2,3;


-- ------------------------------------------
-- 2. Total monthly revenue
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_total_revenue_monthly AS
SELECT
    year,
    month,
    SUM(product_revenue) AS total_revenue
FROM vw_product_revenue_monthly
GROUP BY 1,2;


-- ------------------------------------------
-- 3. Revenue share per product
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_product_revenue_share AS
SELECT
    pr.product_id,
    pr.year,
    pr.month,
    pr.product_revenue,
    tr.total_revenue,
    pr.product_revenue / NULLIF(tr.total_revenue, 0) AS revenue_share
FROM vw_product_revenue_monthly pr
JOIN vw_total_revenue_monthly tr USING(year, month);


-- ------------------------------------------
-- 4. Monthly OPEX total
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_opex_total_monthly AS
SELECT
    year,
    month,
    SUM(opex) AS opex_total
FROM vw_opex_monthly
GROUP BY 1,2;


-- ------------------------------------------
-- 5. Allocate OPEX to products
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_product_opex_allocated AS
SELECT
    rs.product_id,
    rs.year,
    rs.month,
    rs.revenue_share,
    om.opex_total,
    rs.revenue_share * om.opex_total AS opex_allocated
FROM vw_product_revenue_share rs
LEFT JOIN vw_opex_total_monthly om USING(year, month);


-- ------------------------------------------
-- 6. Product-level profitability
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_product_profitability AS
SELECT
    p.product_id,
    p.product_name,
    dt.year,
    dt.month,
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
   AND pr.year = dt.year
   AND pr.month = dt.month
JOIN vw_product_opex_allocated pa
    ON pa.product_id = p.product_id
   AND pa.year = dt.year
   AND pa.month = dt.month
GROUP BY 1,2,3,4,5,7;
