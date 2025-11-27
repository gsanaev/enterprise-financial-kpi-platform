// Tabular Editor 2 Advanced Script
// Creates table "_Measures" and all measures with Display Folders

using System.Linq;

// 1. Get or create _Measures table
var measuresTable = Model.Tables.FirstOrDefault(t => t.Name == "_Measures");
if (measuresTable == null)
{
    measuresTable = Model.AddTable("_Measures");
}

// Helper as a delegate (local methods are not allowed in this scripting context)
System.Action<string, string, string, string> EnsureMeasure =
    (name, expression, formatString, folder) =>
{
    var m = measuresTable.Measures.FirstOrDefault(x => x.Name == name);
    if (m == null)
    {
        m = measuresTable.AddMeasure(name, expression);
    }
    else
    {
        m.Expression = expression;
    }

    if (!string.IsNullOrEmpty(formatString))
        m.FormatString = formatString;

    m.DisplayFolder = folder;
};


// =====================
// Base measures
// =====================

EnsureMeasure(
    "Revenue",
    "SUM ( fact_transactions[net_revenue] )",
    "#,0",
    "Revenue"
);

EnsureMeasure(
    "COGS",
    "SUM ( fact_transactions[direct_cost] )",
    "#,0",
    "COGS"
);

EnsureMeasure(
    "Gross Margin",
    "[Revenue] - [COGS]",
    "#,0",
    "Gross Margin"
);

EnsureMeasure(
    "Gross Margin %",
    "DIVIDE ( [Gross Margin], [Revenue] )",
    "0.0%",
    "Gross Margin"
);


// =====================
// OPEX & Operating Profit
// =====================

EnsureMeasure(
    "OPEX",
    "- SUMX ( FILTER ( fact_financials, RELATED ( dim_account[account_type] ) = \"OPEX\" ), fact_financials[amount] )",
    "#,0",
    "OPEX & Operating Profit"
);

EnsureMeasure(
    "Operating Profit",
    "[Gross Margin] - [OPEX]",
    "#,0",
    "OPEX & Operating Profit"
);

EnsureMeasure(
    "Operating Margin %",
    "DIVIDE ( [Operating Profit], [Revenue] )",
    "0.0%",
    "OPEX & Operating Profit"
);


// =====================
// Volume & Customers
// =====================

EnsureMeasure(
    "Transaction Count",
    "COUNTROWS ( fact_transactions )",
    "#,0",
    "Volume & Customers"
);

EnsureMeasure(
    "Customers",
    "DISTINCTCOUNT ( dim_customer[customer_id] )",
    "#,0",
    "Volume & Customers"
);

EnsureMeasure(
    "Active Customers",
    "CALCULATE ( DISTINCTCOUNT ( dim_customer[customer_id] ), dim_customer[is_active] = 1 )",
    "#,0",
    "Volume & Customers"
);

EnsureMeasure(
    "Churned Customers",
    "[Customers] - [Active Customers]",
    "#,0",
    "Volume & Customers"
);

EnsureMeasure(
    "Churn Rate",
    "DIVIDE ( [Churned Customers], [Customers] )",
    "0.0%",
    "Volume & Customers"
);

EnsureMeasure(
    "Avg Revenue per Customer",
    "DIVIDE ( [Revenue], [Customers] )",
    "#,0",
    "Volume & Customers"
);

EnsureMeasure(
    "Avg Gross Margin per Customer",
    "DIVIDE ( [Gross Margin], [Customers] )",
    "#,0",
    "Volume & Customers"
);


// =====================
// Time Intelligence - Revenue
// =====================

EnsureMeasure(
    "Revenue YTD",
    "CALCULATE ( [Revenue], DATESYTD ( dim_time[date] ) )",
    "#,0",
    "Revenue\\Time"
);

EnsureMeasure(
    "Revenue QTD",
    "CALCULATE ( [Revenue], DATESQTD ( dim_time[date] ) )",
    "#,0",
    "Revenue\\Time"
);

EnsureMeasure(
    "Revenue MTD",
    "CALCULATE ( [Revenue], DATESMTD ( dim_time[date] ) )",
    "#,0",
    "Revenue\\Time"
);

EnsureMeasure(
    "Revenue LTM",
    "CALCULATE ( [Revenue], DATESINPERIOD ( dim_time[date], MAX ( dim_time[date] ), -12, MONTH ) )",
    "#,0",
    "Revenue\\Time"
);


// =====================
// Time Intelligence - COGS
// =====================

EnsureMeasure(
    "COGS YTD",
    "CALCULATE ( [COGS], DATESYTD ( dim_time[date] ) )",
    "#,0",
    "COGS\\Time"
);

EnsureMeasure(
    "COGS QTD",
    "CALCULATE ( [COGS], DATESQTD ( dim_time[date] ) )",
    "#,0",
    "COGS\\Time"
);

EnsureMeasure(
    "COGS MTD",
    "CALCULATE ( [COGS], DATESMTD ( dim_time[date] ) )",
    "#,0",
    "COGS\\Time"
);

EnsureMeasure(
    "COGS LTM",
    "CALCULATE ( [COGS], DATESINPERIOD ( dim_time[date], MAX ( dim_time[date] ), -12, MONTH ) )",
    "#,0",
    "COGS\\Time"
);


// =====================
// Time Intelligence - Gross Margin
// =====================

EnsureMeasure(
    "Gross Margin YTD",
    "[Revenue YTD] - [COGS YTD]",
    "#,0",
    "Gross Margin\\Time"
);

EnsureMeasure(
    "Gross Margin QTD",
    "[Revenue QTD] - [COGS QTD]",
    "#,0",
    "Gross Margin\\Time"
);

EnsureMeasure(
    "Gross Margin MTD",
    "[Revenue MTD] - [COGS MTD]",
    "#,0",
    "Gross Margin\\Time"
);

EnsureMeasure(
    "Gross Margin LTM",
    "[Revenue LTM] - [COGS LTM]",
    "#,0",
    "Gross Margin\\Time"
);


// =====================
// Time Intelligence - OPEX & Operating Profit
// =====================

EnsureMeasure(
    "OPEX YTD",
    "CALCULATE ( [OPEX], DATESYTD ( dim_time[date] ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);

EnsureMeasure(
    "OPEX QTD",
    "CALCULATE ( [OPEX], DATESQTD ( dim_time[date] ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);

EnsureMeasure(
    "OPEX MTD",
    "CALCULATE ( [OPEX], DATESMTD ( dim_time[date] ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);

EnsureMeasure(
    "OPEX LTM",
    "CALCULATE ( [OPEX], DATESINPERIOD ( dim_time[date], MAX ( dim_time[date] ), -12, MONTH ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);

EnsureMeasure(
    "Operating Profit YTD",
    "CALCULATE ( [Operating Profit], DATESYTD ( dim_time[date] ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);

EnsureMeasure(
    "Operating Profit QTD",
    "CALCULATE ( [Operating Profit], DATESQTD ( dim_time[date] ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);

EnsureMeasure(
    "Operating Profit MTD",
    "CALCULATE ( [Operating Profit], DATESMTD ( dim_time[date] ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);

EnsureMeasure(
    "Operating Profit LTM",
    "CALCULATE ( [Operating Profit], DATESINPERIOD ( dim_time[date], MAX ( dim_time[date] ), -12, MONTH ) )",
    "#,0",
    "OPEX & Operating Profit\\Time"
);
