# src/config.py

from pathlib import Path

# -----------------------------
# Global Parameters
# -----------------------------
START_DATE = "2020-01-01"
END_DATE = "2024-12-31"

NUM_CUSTOMERS = 3000
NUM_PRODUCTS = 20
NUM_COST_CENTERS = 6

ANNUAL_CHURN_RATE = 0.12
BASE_MARGIN = 0.45
OPEX_RATIO = 0.25

# Macro shocks for realism (COVID → Recovery → Inflation → Stabilization)
MACRO_SHOCKS = {
    2020: 0.80,
    2021: 0.90,
    2022: 1.15,
    2023: 1.05,
    2024: 1.02,
}

# Seasonal multipliers (quarterly)
REVENUE_SEASONALITY = {1: 1.00, 2: 0.95, 3: 1.05, 4: 1.20}

# Random seed for reproducibility
RNG_SEED = 42

# -----------------------------
# Paths
# -----------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_RAW = PROJECT_ROOT / "data/raw"
DATA_RAW.mkdir(parents=True, exist_ok=True)
