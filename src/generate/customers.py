# src/generate/customers.py

import pandas as pd
import numpy as np

from src.utils import rng
from src.config import NUM_CUSTOMERS, ANNUAL_CHURN_RATE

def generate_dim_customer(dim_time: pd.DataFrame) -> pd.DataFrame:
    start = dim_time["date"].min()
    end = dim_time["date"].max()

    # -----------------------------
    # 1. Acquisition distribution
    # -----------------------------
    acq_start = start
    acq_end = start + pd.DateOffset(years=3)

    acq_dates = acq_start + (acq_end - acq_start) * rng.random(NUM_CUSTOMERS)
    acq_dates = pd.to_datetime(acq_dates).floor("D")

    # -----------------------------
    # 2. Churn simulation
    # -----------------------------
    churn_dates = []

    for acq in acq_dates:
        churn_year = acq.year
        churn_date = pd.NaT

        while churn_year <= end.year:
            if rng.random() < ANNUAL_CHURN_RATE:
                month = int(rng.integers(1, 13))
                churn_candidate = pd.Timestamp(year=churn_year, month=month, day=1)

                if churn_candidate > acq:
                    churn_date = churn_candidate
                break

            churn_year += 1

        if pd.notna(churn_date) and churn_date > end:
            churn_date = pd.NaT

        churn_dates.append(churn_date)

    churn_dates = pd.to_datetime(churn_dates)

    # -----------------------------
    # 3. Segments, regions, risk score
    # -----------------------------
    segments = ["Retail", "SME", "Corporate"]
    regions = ["North", "South", "West", "East", "Central", "International"]

    segment_probs = [0.6, 0.3, 0.1]
    region_probs = [0.2, 0.25, 0.2, 0.15, 0.15, 0.05]

    segment = rng.choice(segments, size=NUM_CUSTOMERS, p=segment_probs)
    region = rng.choice(regions, size=NUM_CUSTOMERS, p=region_probs)

    # FICO-like risk score enhances ML realism
    risk_score = rng.normal(600, 100, size=NUM_CUSTOMERS).clip(300, 850)

    # -----------------------------
    # 4. Construct final dimension
    # -----------------------------
    df = pd.DataFrame(
        {
            "customer_id": np.arange(1, NUM_CUSTOMERS + 1),
            "segment": segment,
            "region": region,
            "risk_score": risk_score,
            "acquisition_date": acq_dates,
            "churn_date": churn_dates,
        }
    )

    df["is_active"] = df["churn_date"].isna().astype(int)

    return df[
        [
            "customer_id",
            "segment",
            "region",
            "risk_score",
            "acquisition_date",
            "churn_date",
            "is_active",
        ]
    ]
