# src/ml/churn_model.py

"""
Churn prediction model.

Pipeline:
1. Connect to DuckDB warehouse (finance.duckdb)
2. Build customer-level feature set from:
   - dim_customer
   - vw_customer_activity_monthly (SQL view)
3. Train a classification model to predict churn (is_active=0 → churned)
4. Evaluate model performance (ROC-AUC, accuracy)
5. Write predictions to:
   - DuckDB table: predicted_churn
   - CSV: data/processed/predicted_churn.csv

This integrates with the rest of the platform:
- Power BI can read predicted_churn via finance.sqlite
- Business users can see churn risk per customer/segment/region
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


# -----------------------------
# Paths & constants
# -----------------------------
DUCKDB_PATH = PROJECT_ROOT / "finance.duckdb"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
DATA_PROCESSED.mkdir(parents=True, exist_ok=True)


# -----------------------------
# 1. Load data from DuckDB
# -----------------------------
def load_feature_table() -> pd.DataFrame:
    """
    Build a customer-level feature table from DuckDB.

    Uses:
      - dim_customer
      - vw_customer_activity_monthly
    """

    con = duckdb.connect(str(DUCKDB_PATH))

    # Aggregate customer activity into features
    # (You can adjust / extend this SQL if you want more features.)
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

    # Basic feature engineering in pandas
    df["acquisition_date"] = pd.to_datetime(df["acquisition_date"])
    df["churn_date"] = pd.to_datetime(df["churn_date"])

    # Tenure in days up to either churn date or dataset end
    dataset_end = df["acquisition_date"].max()  # rough, you can also plug END_DATE from config
    dataset_end = max(dataset_end, df["churn_date"].max(skipna=True))

    # If churned: tenure = churn_date - acquisition_date
    # If active: tenure = dataset_end - acquisition_date
    df["tenure_days"] = np.where(
        df["churn_date"].notna(),
        (df["churn_date"] - df["acquisition_date"]).dt.days,
        (dataset_end - df["acquisition_date"]).dt.days,
    )

    # Label: churned = 1 if NOT active
    df["churn_label"] = (df["is_active"] == 0).astype(int)

    # Keep only customers with some tenure > 0
    df = df[df["tenure_days"].fillna(0) >= 0]

    return df


# -----------------------------
# 2. Build model pipeline
# -----------------------------
def build_model_pipeline() -> tuple[Pipeline, list[str], list[str]]:
    """
    Create a scikit-learn pipeline with:
    - OneHotEncoder for categorical features
    - RandomForestClassifier as the model
    """

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
        max_depth=None,
        random_state=RNG_SEED,
        n_jobs=-1,
    )

    clf = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("model", model),
        ]
    )

    return clf, numeric_features, categorical_features


# -----------------------------
# 3. Train, evaluate, save predictions
# -----------------------------
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

    clf, num_cols, cat_cols = build_model_pipeline()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=RNG_SEED, stratify=y
    )

    print("Training churn model...")
    clf.fit(X_train, y_train)

    print("Evaluating model...")
    y_proba = clf.predict_proba(X_test)[:, 1]
    y_pred = (y_proba >= 0.5).astype(int)

    roc = roc_auc_score(y_test, y_proba)
    acc = accuracy_score(y_test, y_pred)

    print(f"ROC-AUC: {roc:.3f}")
    print(f"Accuracy: {acc:.3f}")
    print("Classification report:")
    print(classification_report(y_test, y_pred, digits=3))

    # Fit on full data for final predictions
    clf.fit(X, y)
    df["churn_probability"] = clf.predict_proba(X)[:, 1]

    # Save predictions
    save_predictions(df[["customer_id", "churn_label", "churn_probability"]])

    print("Churn prediction completed.")


# -----------------------------
# 4. Persist predictions
# -----------------------------
def save_predictions(pred_df: pd.DataFrame):
    """
    Save predictions to:
      - DuckDB table: predicted_churn
      - CSV: data/processed/predicted_churn.csv
    """

    run_date = date.today().isoformat()
    pred_df = pred_df.copy()
    pred_df["run_date"] = run_date

    # Save CSV for inspection / Power BI via SQLite export
    csv_path = DATA_PROCESSED / "predicted_churn.csv"
    pred_df.to_csv(csv_path, index=False)
    print(f"Saved predictions to: {csv_path}")

    # Write to DuckDB table
    con = duckdb.connect(str(DUCKDB_PATH))
    con.execute("DROP TABLE IF EXISTS predicted_churn")
    con.execute(
        """
        CREATE TABLE predicted_churn AS
        SELECT * FROM pred_df
        """
    )
    con.close()
    print("Saved predictions to DuckDB table: predicted_churn")


if __name__ == "__main__":
    train_and_predict()
