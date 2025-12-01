# src/export_to_sqlite.py

"""
Export selected DuckDB tables and views to a SQLite database.

This script:
1. Connects to DuckDB (finance.duckdb)
2. Reads star-schema tables:
      - dim_time
      - dim_customer
      - dim_product
      - dim_account
      - dim_cost_center
      - fact_transactions
      - fact_financials
3. Reads KPI views:
      - vw_pnl_monthly
      - vw_customer_profitability
      - vw_product_profitability
4. Reads ML output:
      - predicted_churn
5. Writes all into:
      finance.sqlite

Power BI connects only to finance.sqlite.
"""

import duckdb
import sqlite3
import pandas as pd

from src.config import PROJECT_ROOT

DUCKDB_PATH = PROJECT_ROOT / "finance.duckdb"
SQLITE_PATH = PROJECT_ROOT / "finance.sqlite"


# ---------------------------------------------------------
# Helper: write a DataFrame to SQLite
# ---------------------------------------------------------
def write_table(conn: sqlite3.Connection, name: str, df: pd.DataFrame):
    df.to_sql(name, conn, if_exists="replace", index=False)
    print(f"  ✔ Wrote table: {name} ({len(df):,} rows)")


# ---------------------------------------------------------
# Main export function
# ---------------------------------------------------------
def export_to_sqlite():
    print("🔗 Connecting to DuckDB...")
    con = duckdb.connect(str(DUCKDB_PATH))

    print("📦 Exporting tables and views to SQLite...")
    sqlite_conn = sqlite3.connect(SQLITE_PATH)

    # ------------------------------------
    # 1. Base dimension & fact tables
    # ------------------------------------
    base_tables = [
        "dim_time",
        "dim_customer",
        "dim_product",
        "dim_account",
        "dim_cost_center",
        "fact_transactions",
        "fact_financials",
    ]

    for table in base_tables:
        df = con.execute(f"SELECT * FROM {table}").fetchdf()
        write_table(sqlite_conn, table, df)

    # ------------------------------------
    # 2. KPI views (optional but recommended)
    # ------------------------------------
    kpi_views = [
        "vw_pnl_monthly",
        "vw_customer_profitability",
        "vw_product_profitability",
    ]

    for view in kpi_views:
        try:
            df = con.execute(f"SELECT * FROM {view}").fetchdf()
            write_table(sqlite_conn, view, df)
        except Exception as e:
            print(f"  ⚠ Warning: Could not export view {view} → {e}")

    # ------------------------------------
    # 3. ML Output: predicted_churn
    # ------------------------------------
    try:
        df = con.execute("SELECT * FROM predicted_churn").fetchdf()
        write_table(sqlite_conn, "predicted_churn", df)
    except Exception:
        print("  ⚠ No 'predicted_churn' table found. Please run churn_model.py first.")

    sqlite_conn.close()
    con.close()

    print(f"🏁 Export complete. SQLite database created at: {SQLITE_PATH}")


if __name__ == "__main__":
    export_to_sqlite()
