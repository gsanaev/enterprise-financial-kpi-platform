# src/ml/churn_model.py
"""
Churn prediction model.

Pipeline:
1. Load customer-level features from DuckDB.
2. Train a RandomForest churn classifier.
3. Evaluate (ROC-AUC, accuracy).
4. Save predictions back into DuckDB + CSV.
5. Exported churn scores feed Power BI (Page 4: Churn Risk).

This module is part of the Enterprise Financial KPI Platform.
"""

from datetime import date
import duckdb
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, accuracy_score, classification_report

from src.config import PROJECT_ROOT, RNG_SEED


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
DUCKDB_PATH = PROJECT_ROOT / "finance.duckdb"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------
# 1. Load Feature Table
# ---------------------------------------------------------------------
def load_feature_table() -> pd.DataFrame:
    """
    Build a customer-level feature set from DuckDB using:

    - dim_customer
    - vw_customer_activity_monthly
    """

    con = duckdb.connect(str(DUCKDB_PATH))

    query = """
    WITH activity AS (
        SELECT
            customer_id,
            COUNT(DISTINCT year_month_key) AS active_months,
            SUM(revenue) AS total_revenue,
            AVG(revenue) AS avg_monthly_revenue,
            MAX(revenue) AS max_monthly_revenue,
            SUM(num_transactions) AS total_transactions,
            AVG(num_transactions) AS avg_tx_per_month
        FROM vw_customer_activity_monthly
        GROUP BY customer_id
    )
    SELECT
        c.customer_id,
        c.segment,
        c.region,
        c.risk_score,
        c.acquisition_date,
        c.churn_date,
        c.is_active,

        COALESCE(a.active_months, 0)        AS active_months,
        COALESCE(a.total_revenue, 0)        AS total_revenue,
        COALESCE(a.avg_monthly_revenue, 0)  AS avg_monthly_revenue,
        COALESCE(a.max_monthly_revenue, 0)  AS max_monthly_revenue,
        COALESCE(a.total_transactions, 0)   AS total_transactions,
        COALESCE(a.avg_tx_per_month, 0)     AS avg_tx_per_month
    FROM dim_customer c
    LEFT JOIN activity a USING(customer_id)
    """

    df = con.execute(query).fetchdf()
    con.close()

    # Convert date columns
    df["acquisition_date"] = pd.to_datetime(df["acquisition_date"])
    df["churn_date"] = pd.to_datetime(df["churn_date"])

    # Determine dataset end
    dataset_end = df["acquisition_date"].max()
    last_churn = df["churn_date"].max(skipna=True)
    dataset_end = max(dataset_end, last_churn)

    # ------------------------------------------------------------------
    # Tenure computation (Pylance-safe: no .dt.days)
    # ------------------------------------------------------------------
    delta_churn = (df["churn_date"] - df["acquisition_date"]).astype("timedelta64[ns]")
    delta_end = (dataset_end - df["acquisition_date"]).astype("timedelta64[ns]")

    df["tenure_days"] = np.where(
        df["churn_date"].notna(),
        delta_churn / np.timedelta64(1, "D"),
        delta_end / np.timedelta64(1, "D")
    ).astype(int)

    # Label (1 = churned)
    df["churn_label"] = (df["is_active"] == 0).astype(int)

    return df


# ---------------------------------------------------------------------
# 2. Model Pipeline
# ---------------------------------------------------------------------
def build_model_pipeline():
    numeric_features = [
        "risk_score",
        "active_months",
        "total_revenue",
        "avg_monthly_revenue",
        "max_monthly_revenue",
        "total_transactions",
        "avg_tx_per_month",
        "tenure_days",
    ]

    categorical_features = ["segment", "region"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=RNG_SEED,
        n_jobs=-1
    )

    clf = Pipeline(steps=[
        ("preprocess", preprocessor),
        ("model", model)
    ])

    return clf, numeric_features, categorical_features


# ---------------------------------------------------------------------
# 3. Train + Predict
# ---------------------------------------------------------------------
def train_and_predict():
    df = load_feature_table()

    feature_cols = [
        "risk_score",
        "active_months",
        "total_revenue",
        "avg_monthly_revenue",
        "max_monthly_revenue",
        "total_transactions",
        "avg_tx_per_month",
        "tenure_days",
        "segment",
        "region",
    ]

    X = df[feature_cols]
    y = df["churn_label"]

    clf, _, _ = build_model_pipeline()

    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RNG_SEED
    )

    print("Training churn model...")
    clf.fit(X_train, y_train)

    print("Evaluating model...")
    y_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    print(f"ROC-AUC: {roc_auc_score(y_test, y_proba):.3f}")
    print(f"Accuracy: {accuracy_score(y_test, y_pred):.3f}")
    print(classification_report(y_test, y_pred, digits=3))

    # Final fit on entire dataset
    clf.fit(X, y)
    df["churn_probability"] = clf.predict_proba(X)[:, 1]

    # --------------------------------------------------------------
    #  NEW BUSINESS-FRIENDLY CHURN PROBABILITY BANDS
    # --------------------------------------------------------------
    df["churn_probability_band"] = pd.cut(
        df["churn_probability"],
        bins=[0, 0.30, 0.70, 1.0],
        labels=["Low (0–30%)", "Medium (30–70%)", "High (70–100%)"],
        include_lowest=True
    )

    df["churn_probability_band_sort"] = pd.cut(
        df["churn_probability"],
        bins=[0, 0.30, 0.70, 1.0],
        labels=[1, 2, 3],
        include_lowest=True
    ).astype(int)

    # Save
    save_predictions(df[[
        "customer_id",
        "churn_label",
        "churn_probability",
        "churn_probability_band",
        "churn_probability_band_sort"
    ]])

    print("Churn prediction completed.")


# ---------------------------------------------------------------------
# 4. Save Predictions to DuckDB + CSV
# ---------------------------------------------------------------------
def save_predictions(pred_df: pd.DataFrame):
    pred_df = pred_df.copy()
    pred_df["run_date"] = date.today().isoformat()

    # CSV
    csv_path = DATA_PROCESSED / "predicted_churn.csv"
    pred_df.to_csv(csv_path, index=False)
    print(f"Saved predictions to: {csv_path}")

    # DuckDB
    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute("DROP TABLE IF EXISTS predicted_churn")
    con.register("pred_df", pred_df)
    con.execute("CREATE TABLE predicted_churn AS SELECT * FROM pred_df")
    con.close()

    print("Saved predictions to DuckDB table: predicted_churn")


# ---------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------
if __name__ == "__main__":
    train_and_predict()
