import pandas as pd
import numpy as np

df = pd.read_parquet('data/daily_sales_inventory.parquet')
dt = pd.read_csv('data/dev_truth.csv')

# Compute chain sales per SKU per day
chain_sales = df.groupby(['date', 'sku_id'])['units_sold'].sum().unstack('sku_id', fill_value=0)
n_stores_per_sku = df.groupby('sku_id')['store_id'].nunique()

# Find all SKUs where total sales across the entire chain is 0 for at least 14 consecutive days up to 2026-09-02,
# while having had robust chain sales (> 20 units/day) earlier
zero_ending_skus = []
for s in chain_sales.columns:
    s_sales = chain_sales[s]
    # Check if last sale was before July 2026
    last_sale_date = s_sales[s_sales > 0].index.max()
    stores_count = n_stores_per_sku[s]
    pre_june_sales = s_sales.loc[:'2026-06-20'].mean()
    if last_sale_date <= pd.Timestamp('2026-07-01') and stores_count >= 15 and pre_june_sales > 10:
        zero_ending_skus.append((s, last_sale_date, stores_count, pre_june_sales))

print("SKUs that completely ceased selling chain-wide before July 2026:")
for s, lsd, sc, pjs in zero_ending_skus:
    print(f"  {s}: last sale {lsd.strftime('%Y-%m-%d')}, carried in {sc} stores, historical mean {pjs:.1f}/day")

