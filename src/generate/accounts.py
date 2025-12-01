# src/generate/accounts.py

import pandas as pd

def generate_dim_account() -> pd.DataFrame:
    records = [
        (4000, "Revenue - Subscription", "Revenue", "Operating Revenue", "Revenue"),
        (4001, "Revenue - Service", "Revenue", "Operating Revenue", "Revenue"),
        (4002, "Revenue - Other", "Revenue", "Operating Revenue", "Revenue"),

        (5000, "Cost of Goods Sold", "COGS", "Direct Costs", "Gross Profit"),

        (6000, "Sales & Marketing", "OPEX", "Indirect Costs", "Operating Profit"),
        (6100, "Operations", "OPEX", "Indirect Costs", "Operating Profit"),
        (6200, "IT & Infrastructure", "OPEX", "Indirect Costs", "Operating Profit"),
        (6300, "HQ & Admin", "OPEX", "Indirect Costs", "Operating Profit"),
    ]

    df = pd.DataFrame(
        records,
        columns=[
            "account_id",
            "account_name",
            "account_type",
            "account_group",
            "reporting_line",
        ],
    )

    return df
