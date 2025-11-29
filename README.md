## Enterprise Financial KPI Platform

An end-to-end analytics platform that generates synthetic enterprise finance data, builds a DuckDB/SQLite data warehouse, transforms it into a star schema, computes financial KPIs, and enables a complete Power BI executive dashboard — with automated DAX measure generation.

## 🌐 Project Architecture

This project has **two parts:**

**PART I — Data Engineering (VSCode)**
**Python + DuckDB + SQL + SQLite**

1. Generate synthetic data  
2. Build the DuckDB warehouse  
3. Apply SQL transformation layers  
4. Export the final data mart to SQLite (for Power BI)  

This pipeline is fully reproducible and automated.

**PART II — Business Intelligence (Power BI)**  
**Power BI Desktop + Tabular Editor 2** 

1. Load `finance.sqlite`  
2. Create a `_Measures` table  
3. Run `create_measures.cs` (DAX automation)  
4. Build visuals and dashboards  

This part happens entirely inside Power BI.

## 📁 Repository Structure
```bash
enterprise-financial-kpi-platform/
├── dashboards
│   └── enterprise_financial_kpis.pbix
├── data
│   ├── processed
│   └── raw
├── finance.duckdb
├── finance.sqlite
├── main.py
├── notebooks
│   └── 01_synthetic_data_design.ipynb
├── pyproject.toml
├── README.md
├── semantic_model
│   └── create_measures.cs
├── sql
│   ├── 01_schema_and_staging.sql
│   ├── 02_core_kpis.sql
│   └── 03_product_profitability.sql
├── src
│   ├── __init__.py
│   ├── __pycache__
│   ├── export_to_sqlite.py
│   ├── generate_synthetic_data.py
│   ├── utils.py
│   └── validate_kpis.py
└── uv.lock
```

## 🧪 Part I — Data Engineering Workflow  
**1. Generate Synthetic Data**   
```bash
uv run python -m src.generate_synthetic_data
```

Creates thousands of customers, products, accounts, daily transactions, financial postings.
Outputs → `data/raw/*.csv`.

**2. Build DuckDB Warehouse**  
**Create Schema and Staging**
```bash
duckdb finance.duckdb -c ".read 'sql/01_schema_and_staging.sql'"
```

**Create Core KPIs**  
```bash
duckdb finance.duckdb -c ".read 'sql/02_core_kpis.sql'"
```

**Create Product Profitability**  
```bash
duckdb finance.duckdb -c ".read 'sql/03_product_profitability.sql'"
```

**3. Export final star schema to SQLite (for Power BI)**  
```bash
uv run python src/export_to_sqlite.py
```

This produces:
```bash
finance.sqlite
```

**This is the only file Power BI needs.**  

## 📊 Part II — Power BI Workflow
**Step 1 — Load the SQLite database**  
In Power BI Desktop:
```pgsql
Get Data → Database → SQLite
```
