# src/utils.py

import numpy as np
import pandas as pd

from src.config import RNG_SEED

# Reusable RNG for all modules
rng = np.random.default_rng(RNG_SEED)

def date_key(ts: pd.Timestamp) -> int:
    """Convert pandas Timestamp to YYYYMMDD integer key."""
    return int(ts.strftime("%Y%m%d"))
