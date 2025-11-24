-- ==========================================
-- 01_create_schema.sql (DuckDB)
-- ==========================================

CREATE TABLE IF NOT EXISTS dim_time (
    date_key        INTEGER PRIMARY KEY,
    date            DATE NOT NULL,
    day             INTEGER,
    month           INTEGER,
    quarter         INTEGER,
    year            INTEGER,
    weekday         INTEGER,
    is_month_end    INTEGER
);

CREATE TABLE IF NOT EXISTS dim_customer (
    customer_id         INTEGER PRIMARY KEY,
    segment             VARCHAR,
    region              VARCHAR,
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
