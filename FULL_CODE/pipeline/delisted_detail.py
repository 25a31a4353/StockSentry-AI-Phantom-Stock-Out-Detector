import pandas as pd
import numpy as np

df = pd.read_parquet('data/daily_sales_inventory.parquet')
dt = pd.read_csv('data/dev_truth.csv')
delisted_skus = set(dt[dt['label_type'] == 'delisted']['sku_id'].unique())
phantom_skus = set(dt[dt['label_type'] == 'phantom']['sku_id'].unique())
misplaced_skus = set(dt[dt['label_type'] == 'misplaced']['sku_id'].unique())

print("Delisted SKUs in dev truth:", delisted_skus)

# Look at chain-wide statistics per SKU
for s in delisted_skus:
    sub = df[df['sku_id'] == s]
    n_stores = sub['store_id'].nunique()
    # Check chain sales by date
    cs = sub.groupby('date')['units_sold'].sum()
    # Check chain on hand
    co = sub.groupby('date')['on_hand_eod'].sum()
    print(f"\nDelisted {s}: carried in {n_stores} stores")
    # Show last date with sales > 0
    selling_dates = cs[cs > 0].index
    print(f"  Last sale anywhere in chain: {selling_dates.max()}")
    print(f"  Sales on 2026-06-21: {cs.get('2026-06-21', 0)}, on 2026-06-22: {cs.get('2026-06-22', 0)}")
    print(f"  Chain on hand on 2026-06-22: {co.get('2026-06-22', 0)}, on 2026-09-01: {co.get('2026-09-01', 0)}")

