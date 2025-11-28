"""
Synthetic data generator for the Enterprise Financial KPI Platform.

Generates:
- dim_time.csv
- dim_customer.csv
- dim_product.csv
- dim_account.csv
- dim_cost_center.csv
- fact_transactions.csv
- fact_financials.csv

All files are written to:  <project_root>/data/raw/
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, Tuple


# =========================
# Global parameters
# =========================

START_DATE = "2020-01-01"
END_DATE = "2024-12-31"

NUM_CUSTOMERS = 10_000
NUM_PRODUCTS = 12
NUM_COST_CENTERS = 6

ANNUAL_CHURN_RATE = 0.12        # approx annual churn probability
BASE_MARGIN = 0.45              # average gross margin
OPEX_RATIO = 0.25               # OPEX / Revenue target

# Quarterly revenue seasonality multipliers (Q1..Q4)
REVENUE_SEASONALITY = {
    1: 1.00,
    2: 0.95,
    3: 1.05,
    4: 1.20,
}

RNG_SEED = 42


# =========================
# Helpers / config
# =========================

@dataclass
class Paths:
    project_root: Path
    data_raw: Path


def get_paths() -> Paths:
    project_root = Path(__file__).resolve().parents[1]

    data_raw = project_root / "data" / "raw"
    data_raw.mkdir(parents=True, exist_ok=True)

    return Paths(project_root=project_root, data_raw=data_raw)



def date_key_from_timestamp(ts: pd.Timestamp) -> int:
    """Integer key YYYYMMDD."""
    return int(ts.strftime("%Y%m%d"))


# =========================
# Dimension generators
# =========================

def generate_dim_time(start_date: str, end_date: str) -> pd.DataFrame:
    dates = pd.date_range(start=start_date, end=end_date, freq="D")
    df = pd.DataFrame({"date": dates})
    df["date_key"] = df["date"].apply(date_key_from_timestamp)
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year
    df["weekday"] = df["date"].dt.weekday  # Monday=0
    # Month end flag
    df["is_month_end"] = df["date"].dt.is_month_end.astype(int)
    return df[
        ["date_key", "date", "day", "month", "quarter", "year", "weekday", "is_month_end"]
    ]


def generate_dim_customer(
    n_customers: int,
    dim_time: pd.DataFrame,
    annual_churn_rate: float,
    rng: np.random.Generator,
) -> pd.DataFrame:

    start = dim_time["date"].min()
    end = dim_time["date"].max()

    # -------------------------------
    # 1. Acquisition dates
    # -------------------------------
    # Spread over first 3 years of dataset
    acq_start = start
    acq_end = start + pd.DateOffset(years=3)

    acq_dates = acq_start + (acq_end - acq_start) * rng.random(n_customers)
    acq_dates = pd.to_datetime(acq_dates).floor("D")

    # -------------------------------
    # 2. Churn simulation (Patched!)
    # -------------------------------
    churn_dates = []

    for acq in acq_dates:
        churn_date = pd.NaT
        current_year = acq.year

        # For each year after acquisition, simulate a Bernoulli trial
        while current_year <= end.year:
            if rng.random() < annual_churn_rate:
                # Churn at a random month of this year
                month = rng.integers(1, 13)
                day = 1
                churn_candidate = pd.Timestamp(year=current_year, month=month, day=day)

                # Ensure churn date is after acquisition
                if churn_candidate > acq:
                    churn_date = churn_candidate
                break

            current_year += 1

        # Cap churn at dataset end
        if pd.notna(churn_date) and churn_date > end:
            churn_date = pd.NaT

        churn_dates.append(churn_date)

    churn_dates = pd.to_datetime(churn_dates)

    # -------------------------------
    # 3. Segments and regions
    # -------------------------------
    segments = ["Retail", "SME", "Corporate"]
    regions = ["North", "South", "West", "East", "Central", "International"]

    segment_probs = [0.6, 0.3, 0.1]  # more Retail customers
    region_probs = [0.2, 0.25, 0.2, 0.15, 0.15, 0.05]

    customer_segment = rng.choice(segments, size=n_customers, p=segment_probs)
    customer_region = rng.choice(regions, size=n_customers, p=region_probs)

    # -------------------------------
    # 4. Assemble dimension
    # -------------------------------
    df = pd.DataFrame(
        {
            "customer_id": np.arange(1, n_customers + 1),
            "segment": customer_segment,
            "region": customer_region,
            "acquisition_date": acq_dates,
            "churn_date": churn_dates,
        }
    )

    # -------------------------------
    # 5. Active flag (Patched!)
    # -------------------------------
    df["is_active"] = df["churn_date"].isna().astype(int)

    return df[
        ["customer_id", "segment", "region", "acquisition_date", "churn_date", "is_active"]
    ]


def generate_dim_product(
    n_products: int,
    base_margin: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    categories = ["Subscription", "Service", "Loan", "Advisory"]
    cat_probs = [0.4, 0.3, 0.2, 0.1]

    product_ids = np.arange(1, n_products + 1)
    product_names = [f"Product {i}" for i in product_ids]
    product_categories = rng.choice(categories, size=n_products, p=cat_probs)

    # base prices between 50 and 500
    base_prices = rng.uniform(50, 500, size=n_products)

    # direct cost ratio: around (1 - base_margin) with some noise
    direct_cost_ratios = np.clip(
        1 - base_margin + rng.normal(0, 0.05, size=n_products),
        0.2,
        0.8,
    )

    df = pd.DataFrame(
        {
            "product_id": product_ids,
            "product_name": product_names,
            "category": product_categories,
            "base_price": base_prices,
            "direct_cost_ratio": direct_cost_ratios,
        }
    )

    return df


def generate_dim_account() -> pd.DataFrame:
    # Simple P&L style chart of accounts
    records = [
        # Revenue
        (4000, "Revenue - Subscription", "Revenue", "Operating Revenue", "Revenue"),
        (4001, "Revenue - Service", "Revenue", "Operating Revenue", "Revenue"),
        (4002, "Revenue - Other", "Revenue", "Operating Revenue", "Revenue"),
        # COGS
        (5000, "Cost of Goods Sold", "COGS", "Direct Costs", "Gross Profit"),
        # OPEX
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


def generate_dim_cost_center(
    n_cost_centers: int,
) -> pd.DataFrame:
    # Predefined departments; if more requested, add generic ones
    base_departments = [
        "Sales",
        "Marketing",
        "Operations",
        "IT",
        "HR",
        "HQ",
    ]
    if n_cost_centers <= len(base_departments):
        departments = base_departments[:n_cost_centers]
    else:
        extra = [f"Dept{i}" for i in range(len(base_departments) + 1, n_cost_centers + 1)]
        departments = base_departments + extra

    countries = ["DE", "DE", "DE", "DE", "DE", "DE"]
    managers = [f"Manager {d}" for d in departments]

    cost_center_ids = np.arange(1, len(departments) + 1)

    df = pd.DataFrame(
        {
            "cost_center_id": cost_center_ids,
            "department": departments,
            "country": countries[: len(departments)],
            "manager": managers,
        }
    )

    return df


# =========================
# Fact table generators
# =========================

def build_date_index_by_month(dim_time: pd.DataFrame) -> Dict[Tuple[int, int], np.ndarray]:
    """Map (year, month) -> array of date_keys in that month."""
    by_month: Dict[Tuple[int, int], np.ndarray] = {}
    for (year, month), group in dim_time.groupby(["year", "month"]):
        by_month[(year, month)] = group["date_key"].to_numpy()
    return by_month


def get_quarter_from_month(month: int) -> int:
    return ((month - 1) // 3) + 1


def segment_monthly_lambda(segment: str) -> float:
    """Average number of transactions per month per customer by segment."""
    if segment == "Retail":
        return 0.4
    if segment == "SME":
        return 0.8
    if segment == "Corporate":
        return 1.2
    return 0.5


def segment_revenue_multiplier(segment: str) -> float:
    if segment == "Retail":
        return 1.0
    if segment == "SME":
        return 1.2
    if segment == "Corporate":
        return 1.5
    return 1.0


def category_revenue_account_id(category: str) -> int:
    if category == "Subscription":
        return 4000
    if category == "Service":
        return 4001
    return 4002


def department_to_opex_account_id(department: str) -> int:
    if department in ("Sales", "Marketing"):
        return 6000
    if department == "Operations":
        return 6100
    if department == "IT":
        return 6200
    return 6300


def generate_fact_transactions(
    dim_customer: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_time: pd.DataFrame,
    rng: np.random.Generator,
) -> pd.DataFrame:
    date_index_by_month = build_date_index_by_month(dim_time)

    transactions = []

    products = dim_product.set_index("product_id")
    product_ids = products.index.values

    # Precompute segment multipliers for speed
    seg_mult = {
        seg: segment_revenue_multiplier(seg) for seg in dim_customer["segment"].unique()
    }

    for _, row in dim_customer.iterrows():
        cust_id = int(row["customer_id"])
        seg = row["segment"]
        acq = row["acquisition_date"]
        churn = row["churn_date"]
        if pd.isna(churn):
            churn = dim_time["date"].max()

        acq_period = acq.to_period("M")
        churn_period = churn.to_period("M")

        # Range of months this customer is active
        months = pd.period_range(acq_period, churn_period, freq="M")

        lam = segment_monthly_lambda(seg)
        seg_factor = seg_mult[seg]

        for period in months:
            year = period.year
            month = period.month
            quarter = get_quarter_from_month(month)

            if (year, month) not in date_index_by_month:
                continue

            # seasonal multiplier by quarter
            seas_mult = REVENUE_SEASONALITY.get(quarter, 1.0)

            # number of transactions this month
            n_tx = rng.poisson(lam)
            if n_tx == 0:
                continue

            possible_dates = date_index_by_month[(year, month)]

            for _ in range(n_tx):
                date_key = int(rng.choice(possible_dates))
                prod_id = int(rng.choice(product_ids))
                prod = products.loc[prod_id]

                base_price = float(prod["base_price"].item())
                direct_cost_ratio = float(prod["direct_cost_ratio"].item())

                # quantity mostly 1, sometimes more
                quantity = int(max(1, rng.poisson(1.2)))

                # revenue with segment + seasonality multiplier + noise
                mean_price = base_price * seg_factor * seas_mult
                # lognormal noise around mean
                noise_factor = rng.lognormal(mean=np.log(1.0), sigma=0.2)
                unit_price = mean_price * noise_factor

                net_revenue = unit_price * quantity
                direct_cost = net_revenue * direct_cost_ratio

                channel = rng.choice(["Online", "Branch", "Partner"], p=[0.6, 0.25, 0.15])

                transactions.append(
                    (
                        cust_id,
                        date_key,
                        prod_id,
                        quantity,
                        net_revenue,
                        direct_cost,
                        channel,
                    )
                )

    if not transactions:
        # Edge case: if parameters produce no transactions
        return pd.DataFrame(
            columns=[
                "transaction_id",
                "date_key",
                "customer_id",
                "product_id",
                "quantity",
                "net_revenue",
                "direct_cost",
                "channel",
            ]
        )

    df = pd.DataFrame(
        transactions,
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
    # reorder columns
    df = df[
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
    return df


def generate_fact_financials(
    fact_transactions: pd.DataFrame,
    dim_product: pd.DataFrame,
    dim_account: pd.DataFrame,
    dim_cost_center: pd.DataFrame,
    dim_time: pd.DataFrame,
    opex_ratio: float,
    rng: np.random.Generator,
) -> pd.DataFrame:
    """
    Build GL-style postings:
    - Revenue by product category -> 4000/4001/4002
    - COGS -> 5000
    - OPEX by cost center -> 6000/6100/6200/6300
    """

    records = []

    # Merge transactions with products to map categories
    tx = fact_transactions.merge(
        dim_product[["product_id", "category"]],
        on="product_id",
        how="left",
    )

    # Revenue per date & category
    tx["account_id"] = tx["category"].apply(category_revenue_account_id)
    revenue_grouped = (
        tx.groupby(["date_key", "account_id"], as_index=False)["net_revenue"].sum()
    )

    for _, row in revenue_grouped.iterrows():
        records.append(
            (
                row["date_key"],
                int(row["account_id"]),
                np.nan,  # no cost center for revenue
                float(row["net_revenue"]),
                "EUR",
            )
        )

    # COGS: sum direct_cost, single account 5000
    cogs_grouped = (
        tx.groupby("date_key", as_index=False)["direct_cost"].sum()
    )
    for _, row in cogs_grouped.iterrows():
        records.append(
            (
                row["date_key"],
                5000,
                np.nan,
                -float(row["direct_cost"]),  # costs as negative
                "EUR",
            )
        )

    # OPEX: allocate based on monthly total revenue
    # First compute monthly revenue
    # join with dim_time to get year/month
    rev_daily = (
        revenue_grouped.groupby("date_key", as_index=False)["net_revenue"].sum()
    )
    rev_daily = rev_daily.merge(
        dim_time[["date_key", "year", "month", "is_month_end"]],
        on="date_key",
        how="left",
    )

    monthly_rev = (
        rev_daily.groupby(["year", "month"], as_index=False)["net_revenue"].sum()
    )
    monthly_rev.rename(columns={"net_revenue": "monthly_revenue"}, inplace=True)

    # Cost center weights (rough)
    departments = dim_cost_center["department"].tolist()
    n_cc = len(departments)
    base_weights = np.array([0.2, 0.15, 0.25, 0.15, 0.1, 0.15][:n_cc], dtype=float)
    base_weights = base_weights / base_weights.sum()

    # Map (year, month) -> date_key of month-end (posting date)
    month_end_dates = (
        dim_time[dim_time["is_month_end"] == 1]
        .groupby(["year", "month"], as_index=False)[["date_key"]]
        .max()
    )
    month_end_map = {
        (int(row["year"]), int(row["month"])): int(row["date_key"])
        for _, row in month_end_dates.iterrows()
    }

    cc_df = dim_cost_center.copy()
    cc_df["opex_account_id"] = cc_df["department"].apply(department_to_opex_account_id)

    for _, row in monthly_rev.iterrows():
        year = int(row["year"])
        month = int(row["month"])
        total_rev = float(row["monthly_revenue"])
        date_key = month_end_map.get((year, month))
        if date_key is None:
            continue

        total_opex = -total_rev * opex_ratio  # negative (cost)
        # randomise weights a bit per month
        noise = rng.normal(1.0, 0.05, size=n_cc)
        weights = base_weights * noise
        weights = weights / weights.sum()

        for (cc_idx, cc_row), w in zip(cc_df.iterrows(), weights):
            amount = total_opex * w
            records.append(
                (
                    date_key,
                    int(cc_row["opex_account_id"]),
                    int(cc_row["cost_center_id"]),
                    float(amount),
                    "EUR",
                )
            )

    df = pd.DataFrame(
        records,
        columns=["date_key", "account_id", "cost_center_id", "amount", "currency"],
    )
    df["posting_id"] = np.arange(1, len(df) + 1)
    df = df[
        ["posting_id", "date_key", "account_id", "cost_center_id", "amount", "currency"]
    ]
    return df


# =========================
# Main orchestration
# =========================

def main():
    rng = np.random.default_rng(RNG_SEED)
    paths = get_paths()

    print("Generating dimensions...")
    dim_time = generate_dim_time(START_DATE, END_DATE)
    dim_customer = generate_dim_customer(NUM_CUSTOMERS, dim_time, ANNUAL_CHURN_RATE, rng)
    dim_product = generate_dim_product(NUM_PRODUCTS, BASE_MARGIN, rng)
    dim_account = generate_dim_account()
    dim_cost_center = generate_dim_cost_center(NUM_COST_CENTERS)

    print("Generating fact_transactions...")
    fact_transactions = generate_fact_transactions(dim_customer, dim_product, dim_time, rng)

    print("Generating fact_financials...")
    fact_financials = generate_fact_financials(
        fact_transactions,
        dim_product,
        dim_account,
        dim_cost_center,
        dim_time,
        OPEX_RATIO,
        rng,
    )

    # Save to CSV
    print("Writing CSVs to data/raw ...")
    dim_time.to_csv(paths.data_raw / "dim_time.csv", index=False)
    dim_customer.to_csv(paths.data_raw / "dim_customer.csv", index=False)
    dim_product.to_csv(paths.data_raw / "dim_product.csv", index=False)
    dim_account.to_csv(paths.data_raw / "dim_account.csv", index=False)
    dim_cost_center.to_csv(paths.data_raw / "dim_cost_center.csv", index=False)
    fact_transactions.to_csv(paths.data_raw / "fact_transactions.csv", index=False)
    fact_financials.to_csv(paths.data_raw / "fact_financials.csv", index=False)

    print("Done.")
    print(f"- dim_time:          {len(dim_time):>8} rows")
    print(f"- dim_customer:      {len(dim_customer):>8} rows")
    print(f"- dim_product:       {len(dim_product):>8} rows")
    print(f"- dim_account:       {len(dim_account):>8} rows")
    print(f"- dim_cost_center:   {len(dim_cost_center):>8} rows")
    print(f"- fact_transactions: {len(fact_transactions):>8} rows")
    print(f"- fact_financials:   {len(fact_financials):>8} rows")


if __name__ == "__main__":
    main()
