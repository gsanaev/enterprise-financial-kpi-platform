//----------------------------------------------
// CREATE _MEASURES TABLE IF NOT EXISTS
//----------------------------------------------
var measuresTableName = "_Measures";
Table measuresTable = null;

// Find existing _Measures table (if any)
foreach (var t in Model.Tables)
{
    if (t.Name == measuresTableName)
    {
        measuresTable = t;
        break;
    }
}

// Create table if missing
if (measuresTable == null)
{
    measuresTable = Model.AddTable(measuresTableName);
    var dummy = measuresTable.AddCalculatedColumn("Value", "1");
    dummy.IsHidden = true;
}


//----------------------------------------------
// HELPER: ADD MEASURE (NO LINQ, NO Find)
//----------------------------------------------

// name, expression, displayFolder, formatString
Action<string, string, string, string> AddMeasure = (name, expression, folder, formatString) =>
{
    Measure m = null;

    // Try to find existing measure with same name
    foreach (var mm in measuresTable.Measures)
    {
        if (mm.Name == name)
        {
            m = mm;
            break;
        }
    }

    // Create if it does not exist
    if (m == null)
    {
        m = measuresTable.AddMeasure(name);
    }

    m.Expression = expression;
    m.DisplayFolder = folder;

    if (!string.IsNullOrEmpty(formatString))
    {
        m.FormatString = formatString;
    }
};


//----------------------------------------------
// FINANCIAL PERFORMANCE KPIs
//----------------------------------------------

// Total Revenue
AddMeasure(
    "Total Revenue",
    "SUM(fact_transactions[net_revenue])",
    "Financial",
    "#,0.00"
);

// Total COGS
AddMeasure(
    "Total COGS",
    "SUM(fact_transactions[direct_cost])",
    "Financial",
    "#,0.00"
);

// Gross Margin
AddMeasure(
    "Gross Margin",
    "[Total Revenue] - [Total COGS]",
    "Financial",
    "#,0.00"
);

// Gross Margin %
AddMeasure(
    "Gross Margin %",
    "DIVIDE([Gross Margin], [Total Revenue])",
    "Financial",
    "0.0%"
);

// Total OPEX
AddMeasure(
    "Total OPEX",
    "CALCULATE(-1 * SUM(fact_financials[amount]), dim_account[account_type] = \"OPEX\")",
    "Financial",
    "#,0.00"
);

// Operating Profit
AddMeasure(
    "Operating Profit",
    "[Total Revenue] - [Total COGS] - [Total OPEX]",
    "Financial",
    "#,0.00"
);

// Operating Margin %
AddMeasure(
    "Operating Margin %",
    "DIVIDE([Operating Profit], [Total Revenue])",
    "Financial",
    "0.0%"
);


//----------------------------------------------
// CUSTOMER KPIs
//----------------------------------------------

// Active Customers
AddMeasure(
    "Active Customers",
    "CALCULATE(DISTINCTCOUNT(dim_customer[customer_id]), dim_customer[is_active] = 1)",
    "Customer",
    "#,0"
);

// Churned Customers
AddMeasure(
    "Churned Customers",
    "CALCULATE(DISTINCTCOUNT(dim_customer[customer_id]), dim_customer[is_active] = 0)",
    "Customer",
    "#,0"
);

// Churn Rate (Actual)
AddMeasure(
    "Churn Rate (Actual)",
    "DIVIDE([Churned Customers], [Active Customers] + [Churned Customers])",
    "Customer",
    "0.0%"
);

// ARPU (Average Revenue Per Customer)
AddMeasure(
    "ARPU (Average Revenue Per Customer)",
    "DIVIDE([Total Revenue], DISTINCTCOUNT(dim_customer[customer_id]))",
    "Customer",
    "#,0.00"
);


//----------------------------------------------
// PRODUCT KPIs
//----------------------------------------------

// Product Revenue
AddMeasure(
    "Product Revenue",
    "SUM(fact_transactions[net_revenue])",
    "Product",
    "#,0.00"
);

// Product Gross Margin
AddMeasure(
    "Product Gross Margin",
    "SUM(fact_transactions[net_revenue]) - SUM(fact_transactions[direct_cost])",
    "Product",
    "#,0.00"
);

// Product GM %
AddMeasure(
    "Product GM %",
    "DIVIDE([Product Gross Margin], [Product Revenue])",
    "Product",
    "0.0%"
);


//----------------------------------------------
// CHURN RISK KPIs (ML)
//----------------------------------------------

// Avg Churn Probability
AddMeasure(
    "Avg Churn Probability",
    "AVERAGE(predicted_churn[churn_probability])",
    "Churn",
    "0.0%"
);

// High-Risk Customers (probability >= 0.7)
AddMeasure(
    "High-Risk Customers",
    "CALCULATE(DISTINCTCOUNT(dim_customer[customer_id]), FILTER(predicted_churn, predicted_churn[churn_probability] >= 0.7))",
    "Churn",
    "#,0"
);


//----------------------------------------------
// SCRIPT FINISHED
//----------------------------------------------
