import duckdb
import sqlite3
import os

DUCKDB_PATH = "finance.duckdb"      # Input DuckDB warehouse
SQLITE_PATH = "finance.sqlite"      # Output SQLite database


# ============================================================
# 1. Remove old SQLite file
# ============================================================
if os.path.exists(SQLITE_PATH):
    print(f"Removing existing SQLite file: {SQLITE_PATH}")
    os.remove(SQLITE_PATH)


# ============================================================
# 2. Connect to DuckDB and SQLite
# ============================================================
print("Connecting to DuckDB...")
duck_con = duckdb.connect(DUCKDB_PATH, read_only=True)

print("Creating new SQLite database...")
sqlite_con = sqlite3.connect(SQLITE_PATH)


# ============================================================
# 3. Final list of tables to export (solid, fixed, production)
# ============================================================

BASE_TABLES = [
    "dim_time",
    "dim_customer",
    "dim_product",
    "dim_account",
    "dim_cost_center",
    "fact_transactions",
    "fact_financials"
]

SEMANTIC_TABLES = [
    "vw_revenue_daily",
    "vw_cogs_daily",
    "vw_margin_daily",
    "vw_pnl_monthly",
    "vw_customer_profitability",
    "vw_customer_activity_monthly",
    "vw_segment_summary",
    "vw_product_profitability"
]

FINAL_EXPORT_LIST = BASE_TABLES + SEMANTIC_TABLES

print("\nTables to export:")
for t in FINAL_EXPORT_LIST:
    print("  -", t)


# ============================================================
# 4. Export each table/view
# ============================================================
for table_name in FINAL_EXPORT_LIST:
    print(f"\nExporting: {table_name}")
    
    try:
        df = duck_con.execute(f"SELECT * FROM {table_name}").df()
    except Exception as e:
        print(f"ERROR reading '{table_name}': {e}")
        continue

    df.to_sql(table_name, sqlite_con, if_exists="replace", index=False)
    print(f"→ Exported {len(df):,} rows")


# ============================================================
# 5. Close connections
# ============================================================
duck_con.close()
sqlite_con.close()

print("\nAll tables exported successfully!")
print(f"SQLite file ready → {SQLITE_PATH}")
