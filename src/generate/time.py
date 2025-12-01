# src/generate/time.py

import pandas as pd
from src.utils import date_key
from src.config import START_DATE, END_DATE

def generate_dim_time():
    dates = pd.date_range(start=START_DATE, end=END_DATE, freq="D")

    df = pd.DataFrame({"date": dates})
    df["date_key"] = df["date"].apply(date_key)
    df["day"] = df["date"].dt.day
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year
    df["weekday"] = df["date"].dt.weekday
    df["is_month_end"] = df["date"].dt.is_month_end.astype(int)

    return df[
        [
            "date_key",
            "date",
            "day",
            "month",
            "quarter",
            "year",
            "weekday",
            "is_month_end",
        ]
    ]
