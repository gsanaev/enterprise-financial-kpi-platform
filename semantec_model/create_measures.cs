//----------------------------------------------
// CREATE _MEASURES TABLE IF NOT EXISTS
//----------------------------------------------
var measuresTableName = "_Measures";
Table measuresTable = null;

foreach (var t in Model.Tables)
{
    if (t.Name == measuresTableName)
    {
        measuresTable = t;
        break;
    }
}

if (measuresTable == null)
{
    measuresTable = Model.AddTable(measuresTableName);
    var dummy = measuresTable.AddCalculatedColumn("Value", "1");
    dummy.IsHidden = true;
}


//----------------------------------------------
// HELPER FUNCTION
//----------------------------------------------
Action<string, string, string, string> AddMeasure =
(name, expression, folder, formatString) =>
{
    var m = measuresTable.Measures.FirstOrDefault(x => x.Name == name);
    if (m == null)
        m = measuresTable.AddMeasure(name);

    m.Expression = expression;
    m.DisplayFolder = folder;
    if (!string.IsNullOrEmpty(formatString))
        m.FormatString = formatString;
};


//----------------------------------------------
// FINANCIAL MEASURES
//----------------------------------------------
AddMeasure("Total Revenue",
"SUM(fact_transactions[net_revenue])",
"Financial", "#,0");

AddMeasure("Total COGS",
"SUM(fact_transactions[direct_cost])",
"Financial", "#,0");

AddMeasure("Gross Margin",
"[Total Revenue] - [Total COGS]",
"Financial", "#,0");

AddMeasure("Gross Margin %",
"DIVIDE([Gross Margin], [Total Revenue])",
"Financial", "0.0%");

AddMeasure("Total OPEX",
"CALCULATE(-1 * SUM(fact_financials[amount]), dim_account[account_type] = \"OPEX\")",
"Financial", "#,0");

AddMeasure("Operating Profit",
"[Gross Margin] - [Total OPEX]",
"Financial", "#,0");

AddMeasure("Operating Margin %",
"DIVIDE([Operating Profit], [Total Revenue])",
"Financial", "0.0%");


//----------------------------------------------
// CUSTOMER KPIs
//----------------------------------------------
AddMeasure("Active Customers",
"CALCULATE(DISTINCTCOUNT(dim_customer[customer_id]), dim_customer[is_active] = 1)",
"Customer", "#,0");

AddMeasure("Churned Customers",
"CALCULATE(DISTINCTCOUNT(dim_customer[customer_id]), dim_customer[is_active] = 0)",
"Customer", "#,0");

AddMeasure("Churn Rate (Actual)",
"DIVIDE([Churned Customers], [Active Customers] + [Churned Customers])",
"Customer", "0.0%");

AddMeasure("ARPU (Average Revenue Per Customer)",
"DIVIDE([Total Revenue], DISTINCTCOUNT(dim_customer[customer_id]))",
"Customer", "#,0");

AddMeasure("Avg Gross Margin Per Customer",
"DIVIDE([Gross Margin], [Active Customers])",
"Customer", "#,0");

AddMeasure("Customer GM %",
"DIVIDE([Avg Gross Margin Per Customer], [ARPU (Average Revenue Per Customer)])",
"Customer", "0.0%");


//----------------------------------------------
// PRODUCT KPIs
//----------------------------------------------
AddMeasure("Product Revenue",
"SUM(fact_transactions[net_revenue])",
"Product", "#,0");

AddMeasure("Product Gross Margin",
"SUM(fact_transactions[net_revenue]) - SUM(fact_transactions[direct_cost])",
"Product", "#,0");

AddMeasure("Product GM %",
"DIVIDE([Product Gross Margin], [Product Revenue])",
"Product", "0.0%");

AddMeasure("Product Rank by Revenue",
"RANKX(ALL(dim_product[product_name]), [Product Revenue], , DESC)",
"Product", "");


//----------------------------------------------
// CHURN RISK KPIs (FULL SET)
//----------------------------------------------

AddMeasure("Avg Churn Probability",
"AVERAGE(predicted_churn[churn_probability])",
"Churn", "0.0%");

AddMeasure("High-Risk Customers",
"CALCULATE(DISTINCTCOUNT(dim_customer[customer_id]), predicted_churn[churn_probability] >= 0.7)",
"Churn", "#,0");

AddMeasure("Revenue at Risk",
"SUMX(FILTER(VALUES(dim_customer[customer_id]), CALCULATE(MAX(predicted_churn[churn_probability])) >= 0.7), CALCULATE([Total Revenue]))",
"Churn", "#,0");

AddMeasure("Avg Revenue Per High-Risk Customer",
"DIVIDE([Revenue at Risk], [High-Risk Customers])",
"Churn", "#,0");

AddMeasure("Churn Probability Weighted Revenue",
"SUMX(VALUES(dim_customer[customer_id]), [Total Revenue] * CALCULATE(MAX(predicted_churn[churn_probability])))",
"Churn", "#,0");

AddMeasure("High-Risk Customer %",
"DIVIDE([High-Risk Customers], [Active Customers])",
"Churn", "0.0%");


//----------------------------------------------
// SCRIPT COMPLETE
//----------------------------------------------
