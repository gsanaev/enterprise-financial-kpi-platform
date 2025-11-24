-- ==========================================
-- 02_load_staging_data.sql (DuckDB version)
-- ==========================================

COPY dim_time
FROM 'data/raw/dim_time.csv'
WITH (HEADER TRUE);

COPY dim_customer
FROM 'data/raw/dim_customer.csv'
WITH (HEADER TRUE);

COPY dim_product
FROM 'data/raw/dim_product.csv'
WITH (HEADER TRUE);

COPY dim_account
FROM 'data/raw/dim_account.csv'
WITH (HEADER TRUE);

COPY dim_cost_center
FROM 'data/raw/dim_cost_center.csv'
WITH (HEADER TRUE);

COPY fact_transactions
FROM 'data/raw/fact_transactions.csv'
WITH (HEADER TRUE);

COPY fact_financials
FROM 'data/raw/fact_financials.csv'
WITH (HEADER TRUE);

-- Row count validation
SELECT 'dim_time', COUNT(*) FROM dim_time;
SELECT 'dim_customer', COUNT(*) FROM dim_customer;
SELECT 'dim_product', COUNT(*) FROM dim_product;
SELECT 'dim_account', COUNT(*) FROM dim_account;
SELECT 'dim_cost_center', COUNT(*) FROM dim_cost_center;
SELECT 'fact_transactions', COUNT(*) FROM fact_transactions;
SELECT 'fact_financials', COUNT(*) FROM fact_financials;
