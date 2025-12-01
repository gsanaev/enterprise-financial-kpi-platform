# src/generate/cost_centers.py

import numpy as np
import pandas as pd

from src.config import NUM_COST_CENTERS

def generate_dim_cost_center() -> pd.DataFrame:
    base_departments = [
        "Sales",
        "Marketing",
        "Operations",
        "IT",
        "HR",
        "HQ",
    ]

    if NUM_COST_CENTERS <= len(base_departments):
        departments = base_departments[:NUM_COST_CENTERS]
    else:
        extra = [
            f"Dept{i}"
            for i in range(len(base_departments) + 1, NUM_COST_CENTERS + 1)
        ]
        departments = base_departments + extra

    cost_center_ids = np.arange(1, len(departments) + 1)

    df = pd.DataFrame(
        {
            "cost_center_id": cost_center_ids,
            "department": departments,
            "country": ["DE"] * len(departments),
            "manager": [f"Manager {d}" for d in departments],
        }
    )

    return df
