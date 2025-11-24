-- ==========================================
-- 05_kpi_views.sql
-- ==========================================

-- ------------------------------------------
-- Customer Profitability Summary
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_customer_profitability_summary AS
SELECT
    segment,
    COUNT(DISTINCT customer_id) AS num_customers,
    SUM(total_revenue) AS total_revenue,
    SUM(total_cogs) AS total_cogs,
    SUM(gross_margin) AS total_gross_margin,
    AVG(gross_margin_pct) AS avg_gross_margin_pct
FROM vw_customer_profitability
GROUP BY 1;


-- ------------------------------------------
-- Customer Activity Summary
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_customer_activity_summary AS
SELECT
    customer_id,
    COUNT(*) AS active_months,
    SUM(num_transactions) AS total_transactions,
    SUM(revenue) AS total_revenue,
    SUM(cogs) AS total_cogs
FROM vw_customer_activity_monthly
GROUP BY 1;


-- ------------------------------------------
-- CLV (simple gross-margin LTV)
-- ------------------------------------------
CREATE OR REPLACE VIEW vw_customer_clv AS
SELECT
    c.customer_id,
    c.segment,
    c.region,
    p.total_revenue,
    p.total_cogs,
    p.gross_margin AS lifetime_margin,
    a.total_transactions,
    a.active_months,
    (p.gross_margin / NULLIF(a.active_months, 0)) * 12 AS annualized_gm
FROM vw_customer_profitability p
LEFT JOIN vw_customer_activity_summary a USING(customer_id)
JOIN dim_customer c USING(customer_id);


-- ------------------------------------------
-- Monthly P&L + YTD + QTD + LTM
-- ------------------------------------------

CREATE OR REPLACE VIEW vw_pnl_enhanced AS
WITH base AS (
    SELECT
        year,
        month,
        revenue,
        cogs,
        gross_margin,
        opex,
        operating_profit,
        -- derive quarter
        CASE 
            WHEN month IN (1,2,3) THEN 1
            WHEN month IN (4,5,6) THEN 2
            WHEN month IN (7,8,9) THEN 3
            ELSE 4
        END AS quarter
    FROM vw_pnl_monthly
)

SELECT
    b.year,
    b.month,
    b.quarter,

    b.revenue,
    b.cogs,
    b.gross_margin,
    b.opex,
    b.operating_profit,

    -- YTD
    y.revenue_ytd,

    -- QTD (join via derived quarter)
    q.revenue_qtd,

    -- LTM
    l.revenue_ltm

FROM base b

LEFT JOIN vw_revenue_ytd y 
    ON b.year = y.year

LEFT JOIN vw_revenue_qtd q
    ON b.year = q.year
   AND b.quarter = q.quarter

LEFT JOIN vw_revenue_ltm l
    ON b.year = l.year
   AND b.month = l.month
ORDER BY b.year, b.month;
