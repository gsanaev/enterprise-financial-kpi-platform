-- ================================================================
-- 01_schema_and_staging.sql
-- Full Schema Creation + Staging Data Load
-- ================================================================

---------------------------------------------------------
-- 1. DIMENSION TABLES
---------------------------------------------------------

CREATE TABLE IF NOT EXISTS dim_time (
    date_key        INTEGER PRIMARY KEY,
    date            DATE NOT NULL,
    day             INTEGER,
    month           INTEGER,
    quarter         INTEGER,
    year            INTEGER,
    weekday         INTEGER,
    is_month_end    INTEGER,

    -- Numeric month key: 202401, 202402, ...
    year_month_key  INTEGER GENERATED ALWAYS AS (year * 100 + month),

    -- Text label for visuals, derived from date (e.g. '2024-01')
    year_month_label VARCHAR GENERATED ALWAYS AS (strftime('%Y-%m', date)),

    -- Short month name from date (e.g. 'Jan')
    month_name      VARCHAR GENERATED ALWAYS AS (strftime('%b', date))
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id         INTEGER PRIMARY KEY,
    segment             VARCHAR,
    region              VARCHAR,
    risk_score          DECIMAL(6,2),
    acquisition_date    DATE,
    churn_date          DATE,
    is_active           INTEGER
);

CREATE TABLE IF NOT EXISTS dim_product (
    product_id          INTEGER PRIMARY KEY,
    product_name        VARCHAR,
    category            VARCHAR,
    base_price          DECIMAL(18,2),
    direct_cost_ratio   DECIMAL(6,4)
);

CREATE TABLE IF NOT EXISTS dim_account (
    account_id      INTEGER PRIMARY KEY,
    account_name    VARCHAR,
    account_type    VARCHAR,
    account_group   VARCHAR,
    reporting_line  VARCHAR
);

CREATE TABLE IF NOT EXISTS dim_cost_center (
    cost_center_id  INTEGER PRIMARY KEY,
    department      VARCHAR,
    country         VARCHAR,
    manager         VARCHAR
);

---------------------------------------------------------
-- 2. FACT TABLES
---------------------------------------------------------

CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id      INTEGER PRIMARY KEY,
    date_key            INTEGER,
    customer_id         INTEGER,
    product_id          INTEGER,
    quantity            INTEGER,
    net_revenue         DECIMAL(18,2),
    direct_cost         DECIMAL(18,2),
    channel             VARCHAR
);

CREATE TABLE IF NOT EXISTS fact_financials (
    posting_id      INTEGER PRIMARY KEY,
    date_key        INTEGER,
    account_id      INTEGER,
    cost_center_id  INTEGER,
    amount          DECIMAL(18,2),
    currency        VARCHAR
);

---------------------------------------------------------
-- 3. LOAD DATA FROM CSV FILES
---------------------------------------------------------

COPY dim_time (
    date_key,
    date,
    day,
    month,
    quarter,
    year,
    weekday,
    is_month_end
)
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

---------------------------------------------------------
-- 4. BASIC VALIDATION
---------------------------------------------------------

SELECT 'dim_time', COUNT(*) FROM dim_time;
SELECT 'dim_customer', COUNT(*) FROM dim_customer;
SELECT 'dim_product', COUNT(*) FROM dim_product;
SELECT 'dim_account', COUNT(*) FROM dim_account;
SELECT 'dim_cost_center', COUNT(*) FROM dim_cost_center;
SELECT 'fact_transactions', COUNT(*) FROM fact_transactions;
SELECT 'fact_financials', COUNT(*) FROM fact_financials;
