# src/generate/products.py

import numpy as np
import pandas as pd

from src.utils import rng
from src.config import NUM_PRODUCTS, BASE_MARGIN

def generate_dim_product() -> pd.DataFrame:
    categories = ["Subscription", "Service", "Loan", "Advisory"]
    cat_probs = [0.40, 0.30, 0.20, 0.10]

    product_ids = np.arange(1, NUM_PRODUCTS + 1)
    product_names = [f"Product {i}" for i in product_ids]
    product_categories = rng.choice(categories, size=NUM_PRODUCTS, p=cat_probs)

    base_prices = []
    direct_cost_ratios = []

    for cat in product_categories:
        if cat == "Subscription":
            price = rng.uniform(50, 200)
            dcr = np.clip(1 - BASE_MARGIN + rng.normal(0.00, 0.04), 0.25, 0.70)

        elif cat == "Service":
            price = rng.uniform(100, 400)
            dcr = np.clip(1 - BASE_MARGIN + rng.normal(0.05, 0.05), 0.30, 0.75)

        elif cat == "Loan":
            price = rng.uniform(300, 800)
            dcr = np.clip(1 - BASE_MARGIN + rng.normal(-0.05, 0.05), 0.20, 0.65)

        else:  # Advisory
            price = rng.uniform(150, 600)
            dcr = np.clip(1 - BASE_MARGIN + rng.normal(0.02, 0.05), 0.25, 0.72)

        base_prices.append(price)
        direct_cost_ratios.append(dcr)

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
