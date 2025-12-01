# src/synthetic_pipeline.py

from src.config import DATA_RAW
from src.generate.time import generate_dim_time
from src.generate.customers import generate_dim_customer
from src.generate.products import generate_dim_product
from src.generate.accounts import generate_dim_account
from src.generate.cost_centers import generate_dim_cost_center
from src.generate.transactions import generate_fact_transactions
from src.generate.financials import generate_fact_financials

def main():
    print("Generating dimensions...")

    dim_time = generate_dim_time()
    dim_customer = generate_dim_customer(dim_time)
    dim_product = generate_dim_product()
    dim_account = generate_dim_account()
    dim_cost_center = generate_dim_cost_center()

    print("Generating fact tables...")

    fact_transactions = generate_fact_transactions(dim_customer, dim_product, dim_time)
    fact_financials = generate_fact_financials(
        fact_transactions, dim_product, dim_cost_center, dim_time
    )

    print("Writing CSVs...")
    dim_time.to_csv(DATA_RAW / "dim_time.csv", index=False)
    dim_customer.to_csv(DATA_RAW / "dim_customer.csv", index=False)
    dim_product.to_csv(DATA_RAW / "dim_product.csv", index=False)
    dim_account.to_csv(DATA_RAW / "dim_account.csv", index=False)
    dim_cost_center.to_csv(DATA_RAW / "dim_cost_center.csv", index=False)
    fact_transactions.to_csv(DATA_RAW / "fact_transactions.csv", index=False)
    fact_financials.to_csv(DATA_RAW / "fact_financials.csv", index=False)

    print("✓ Synthetic dataset complete.")

if __name__ == "__main__":
    main()
