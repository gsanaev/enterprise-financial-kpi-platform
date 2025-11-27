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
│
├── data/
│   ├── raw/                   # Synthetic CSV files
│   └── processed/             # PBIX, exports, etc.
│
├── dashboards/
│   └── enterprise_financial_kpis.pbix
│
├── sql/
│   ├── 01_create_schema.sql
│   ├── 02_load_staging_data.sql
│   ├── 03_transform_core.sql
│   ├── 04_cost_allocation.sql
│   └── 05_kpi_views.sql
│
├── semantic_model/            # DAX automation layer
│   ├── create_measures.cs     # Script for Tabular Editor
│   └── measures/              # Optional JSON definitions
│       └── measures.json
│
├── src/
│   └── enterprise_financial_kpi_platform/
│       ├── generate_synthetic_data.py
│       ├── export_to_sqlite.py
│       ├── utils.py
│       └── validate_kpis.py
│
├── notebooks/
│   └── 01_synthetic_data_design.ipynb
│
├── finance.sqlite             # Final PowerBI-ready data mart
├── main.py
└── README.md
```

## 🧪 Part I — Data Engineering Workflow  
**1. Generate Synthetic Data**   
```bash
uv run python -m src.enterprise_financial_kpi_platform.generate_synthetic_data
```

Creates thousands of customers, products, accounts, daily transactions, financial postings.
Outputs → `data/raw/*.csv`.

**2. Build DuckDB Warehouse**  
**Create schema**
```bash
duckdb finance.duckdb -c ".read 'sql/01_create_schema.sql'"
```

**Load staging data**  
```bash
duckdb finance.duckdb -c ".read 'sql/02_load_staging_data.sql'"
```

**Transform core layer**  
```bash
duckdb finance.duckdb -c ".read 'sql/03_transform_core.sql'"
```

**Cost allocation**  
```bash
duckdb finance.duckdb -c ".read 'sql/04_cost_allocation.sql'"
````

**KPI views**  
```bash
duckdb finance.duckdb -c ".read 'sql/05_kpi_views.sql'"
```

**3. Export final star schema to SQLite (for Power BI)**  
```bash
uv run python src/enterprise_financial_kpi_platform/export_to_sqlite.py
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

Select:  
```
finance.sqlite
```
Load tables:
- dim_customer  
- dim_product  
- dim_time  
- dim_account  
- fact_transactions  
- fact_financials  

**Step 2 — Create _Measures table (manually)**  
In Power BI:
```sql
Model View → New Table
```

Paste:
```DAX
_Measures = {1}
```
Then:  
- hide column **Value**  
- keep table _Measures  

**Step 3 — Generate DAX measures automatically (Tabular Editor)**
1. Install **Tabular Editor 2**
2. In Power BI **→ External Tools → Tabular Editor**
3. Open file:  
`semantic_model/create_measures.cs`  
4. Run the script  
This will create all KPIs:
- Revenue (YTD/QTD/MTD/LTM)  
- COGS (YTD/QTD/MTD/LTM)  
- Gross Margin %  
- OPEX  
- Operating Profit  
- Operating Margin %  
- Customers, Active Customers, Churn  
- Transaction Count  
- ARPC (Avg Revenue per Customer)  
All measures are correctly grouped in folders:  
```css
Revenue/
Revenue/Time
COGS/
COGS/Time
Gross Margin/
Gross Margin/Time
OPEX & Operating Profit/
OPEX & Operating Profit/Time
Volume & Customers/
```
**Step 4 — Build Dashboard**  
Suggested visuals:  

**Executive Summary**  
- Revenue YTD  
- Gross Margin %  
- Operating Profit  
- Operating Margin %  
- Active Customers  
- Churn Rate  

**Trend Visuals**  
- Revenue MTD/QTD/YTD  
- Gross Margin trend  
- Operating Profit trend  

**Dimensional Analysis**  
- Revenue by Product  
- Revenue by Customer Segment  
- Profitability by Product  
- Customer Lifetime Revenue  

**Transaction Analysis**  
- Volume  
- ARPC  
- Churn logic  

## 🧠 Financial KPIs Included
**Core**  
- Revenue  
- COGS  
- Gross Margin  
- OPEX  
- Operating Profit  

**Margins**  
- Gross Margin %  
- Operating Margin %  

**Time Intelligence**  
- YTD / QTD / MTD / LTM versions for  
Revenue, COGS, Gross Margin, OPEX, Operating Profit

**Customer / Volume Metrics**
- Transaction Count  
- Customers  
- Active Customers  
- Churned Customers  
- Churn Rate  
- Avg Revenue per Customer  
- Avg Gross Margin per Customer  

## 🚀 Reproduce Entire Pipeline

To rebuild everything from scratch:
```bash
rm finance.duckdb
duckdb finance.duckdb -c ".read 'sql/01_create_schema.sql'"
duckdb finance.duckdb -c ".read 'sql/02_load_staging_data.sql'"
duckdb finance.duckdb -c ".read 'sql/03_transform_core.sql'"
duckdb finance.duckdb -c ".read 'sql/04_cost_allocation.sql'"
duckdb finance.duckdb -c ".read 'sql/05_kpi_views.sql'"

uv run python src/enterprise_financial_kpi_platform/export_to_sqlite.py
```

Then:  
1. Load **finance.sqlite** in Power BI  
2. Create `_Measures = {1}`  
3. Run create_measures.cs via Tabular Editor  

## 🗂 Storing Dashboards

Save Power BI dashboards into:  
```markdown
dashboards/
    enterprise_financial_kpis.pbix  
```