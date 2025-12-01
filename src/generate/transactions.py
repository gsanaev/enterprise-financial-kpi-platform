# src/generate/transactions.py

import pandas as pd
import numpy as np

from src.config import REVENUE_SEASONALITY, MACRO_SHOCKS
from src.utils import rng

def generate_fact_transactions(
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_time: pd.DataFrame,
) -> pd.DataFrame:

    # Lookup by (year, month)
    date_index = {}
    for (year, month), group in dim_time.groupby(["year", "month"]):
        date_index[(year, month)] = group.date_key.values

    products = dim_product.set_index("product_id")
    product_ids = products.index.values

    tx_records = []

    # Precompute spend tiers (customer heterogeneity)
    spend_tiers = rng.choice([0.5, 1.0, 2.0, 4.0], size=len(dim_customer), p=[0.25, 0.45, 0.25, 0.05])
    spend_map = dict(zip(dim_customer["customer_id"], spend_tiers))

    # Segment multipliers
    seg_rev_mult = {"Retail": 1.0, "SME": 1.2, "Corporate": 1.5}
    seg_cost_mult = {"Retail": 1.00, "SME": 0.95, "Corporate": 0.88}

    # Baseline monthly transaction rate per segment
    seg_lambda = {"Retail": 0.4, "SME": 0.8, "Corporate": 1.2}

    for _, cust in dim_customer.iterrows():
        cid = int(cust.customer_id)
        seg = cust.segment
        acq = cust.acquisition_date
        churn = cust.churn_date if pd.notna(cust.churn_date) else dim_time.date.max()

        months = pd.period_range(acq.to_period("M"), churn.to_period("M"), freq="M")

        for period in months:
            year, month = period.year, period.month

            if (year, month) not in date_index:
                continue

            # Seasonality * Macro shock
            seas = REVENUE_SEASONALITY[period.quarter]
            macro = MACRO_SHOCKS.get(year, 1.0)

            # Monthly expected number of transactions
            lam = seg_lambda[seg] * spend_map[cid]
            lam = max(lam, 0.05)

            n_tx = rng.poisson(lam)
            if n_tx == 0:
                continue

            possible_dates = date_index[(year, month)]

            for _ in range(n_tx):
                date_key = int(rng.choice(possible_dates))
                pid = int(rng.choice(product_ids))

                p = products.loc[pid]
                base_price = p.base_price
                dcr = p.direct_cost_ratio

                qty = max(1, int(rng.poisson(1.1)))

                noise = rng.lognormal(mean=0, sigma=0.15)
                unit_price = base_price * seg_rev_mult[seg] * spend_map[cid] * seas * macro * noise

                revenue = unit_price * qty
                cost = revenue * (dcr * seg_cost_mult[seg])

                channel = rng.choice(["Online", "Branch", "Partner"], p=[0.6, 0.25, 0.15])

                tx_records.append(
                    (cid, date_key, pid, qty, revenue, cost, channel)
                )

    df = pd.DataFrame(
        tx_records,
        columns=[
            "customer_id",
            "date_key",
            "product_id",
            "quantity",
            "net_revenue",
            "direct_cost",
            "channel",
        ],
    )

    df["transaction_id"] = np.arange(1, len(df) + 1)

    return df[
        [
            "transaction_id",
            "date_key",
            "customer_id",
            "product_id",
            "quantity",
            "net_revenue",
            "direct_cost",
            "channel",
        ]
    ]
