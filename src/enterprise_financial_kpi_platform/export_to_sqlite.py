import duckdb
import sqlite3
import os

DUCKDB_PATH = "finance.duckdb"            # your DuckDB warehouse
SQLITE_PATH = "finance.sqlite"            # output SQLite DB

# ---------------------------------------------------
# 1. Remove previous SQLite file (if exists)
# ---------------------------------------------------
if os.path.exists(SQLITE_PATH):
    print(f"Removing existing SQLite file: {SQLITE_PATH}")
    os.remove(SQLITE_PATH)

# ---------------------------------------------------
# 2. Open DuckDB (read-only)
# ---------------------------------------------------
print("Connecting to DuckDB...")
duck_con = duckdb.connect(DUCKDB_PATH, read_only=True)

# ---------------------------------------------------
# 3. Open SQLite
# ---------------------------------------------------
print("Creating SQLite database...")
sqlite_con = sqlite3.connect(SQLITE_PATH)

tables = duck_con.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'main'
""").fetchall()

print(f"Found {len(tables)} tables in DuckDB.")

# ---------------------------------------------------
# 4. Export all tables
# ---------------------------------------------------
for (table_name,) in tables:
    print(f"Exporting table: {table_name}")

    df = duck_con.execute(f"SELECT * FROM {table_name}").df()   # load table to pandas DataFrame
    df.to_sql(table_name, sqlite_con, if_exists="replace", index=False)

print("All tables exported successfully.")

# ---------------------------------------------------
# 5. Close connections
# ---------------------------------------------------
duck_con.close()
sqlite_con.close()

print(f"SQLite export complete → {SQLITE_PATH}")
