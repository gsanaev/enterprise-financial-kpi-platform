# src/generate/financials.py

import pandas as pd
import numpy as np

from src.utils import rng
from src.config import OPEX_RATIO

def category_to_account(cat: str) -> int:
    if cat == "Subscription":
        return 4000
    if cat == "Service":
        return 4001
    return 4002

def dept_to_account(dept: str) -> int:
    if dept in ("Sales", "Marketing"):
        return 6000
    if dept == "Operations":
        return 6100
    if dept == "IT":
        return 6200
    return 6300

def generate_fact_financials(
    fact_transactions: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_cost_center: pd.DataFrame,
    dim_time: pd.DataFrame,
) -> pd.DataFrame:

    recs = []

    tx = fact_transactions.merge(dim_product[["product_id", "category"]], on="product_id")

    # -----------------------------
    # Revenue postings
    # -----------------------------
    tx["account_id"] = tx["category"].apply(category_to_account)

    rev_grp = tx.groupby(["date_key", "account_id"])["net_revenue"].sum().reset_index()

    for _, r in rev_grp.iterrows():
        recs.append((r.date_key, int(r.account_id), np.nan, float(r.net_revenue), "EUR"))

    # -----------------------------
    # COGS postings
    # -----------------------------
    cogs_grp = tx.groupby("date_key")["direct_cost"].sum().reset_index()

    for _, r in cogs_grp.iterrows():
        recs.append((r.date_key, 5000, np.nan, -float(r.direct_cost), "EUR"))

    # -----------------------------
    # OPEX allocation (monthly)
    # -----------------------------
    # Monthly revenue
    rev_daily = rev_grp.merge(dim_time[["date_key", "year", "month"]], on="date_key")

    monthly_rev = rev_daily.groupby(["year", "month"])["net_revenue"].sum().reset_index()
    monthly_rev.rename(columns={"net_revenue": "monthly_revenue"}, inplace=True)

    # Find month-end posting date
    month_end = (
        dim_time[dim_time.is_month_end == 1].groupby(["year", "month"])["date_key"].max().to_dict()
    )

    # Cost center weights
    cc = dim_cost_center.copy()
    cc["account_id"] = cc["department"].apply(dept_to_account)
    w = np.array([0.2, 0.15, 0.25, 0.15, 0.1, 0.15][: len(cc)])
    w = w / w.sum()

    for _, r in monthly_rev.iterrows():
        y, m = int(r.year), int(r.month)
        posting_date = month_end.get((y, m))
        if not posting_date:
            continue

        total_opex = -(r.monthly_revenue * OPEX_RATIO)
        noise = rng.normal(1.0, 0.05, size=len(cc))
        w_adj = (w * noise) / (w * noise).sum()

        for (_, row), weight in zip(cc.iterrows(), w_adj):
            amount = total_opex * weight
            recs.append(
                (posting_date, int(row.account_id), int(row.cost_center_id), float(amount), "EUR")
            )

    df = pd.DataFrame(
        recs,
        columns=["date_key", "account_id", "cost_center_id", "amount", "currency"],
    )

    df["posting_id"] = np.arange(1, len(df) + 1)

    return df[
        [
            "posting_id",
            "date_key",
            "account_id",
            "cost_center_id",
            "amount",
            "currency",
        ]
    ]
