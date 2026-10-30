import pandas as pd
import numpy as np

dt = pd.read_csv('data/dev_truth.csv')
delisted_rows = dt[dt['label_type'] == 'delisted']
print('Delisted rows:', len(delisted_rows))
print('Unique SKUs:', delisted_rows['sku_id'].unique().tolist())
print(delisted_rows.groupby('sku_id')['store_id'].nunique())
for s, g in delisted_rows.groupby('sku_id'):
    dmin = g['date'].min()
    dmax = g['date'].max()
    stores = g['store_id'].nunique()
    print(f"  {s}: min {dmin} max {dmax} ({len(g)} rows across {stores} stores)")

# Let's inspect daily_sales_inventory for these SKUs to see chain-wide behavior across ALL 25 stores!
df = pd.read_parquet('data/daily_sales_inventory.parquet')
for s in delisted_rows['sku_id'].unique():
    sub = df[df['sku_id'] == s]
    daily_sales = sub.groupby('date')['units_sold'].sum()
    daily_stores_selling = sub[sub['units_sold'] > 0].groupby('date')['store_id'].nunique()
    print(f"\nSKU {s}:")
    print(f"  Total sales 2025-04 to 2026-06-01: {daily_sales.loc[:'2026-06-01'].sum():.0f}")
    print(f"  Total sales after 2026-06-25: {daily_sales.loc['2026-06-25':].sum():.0f}")
    # When did chain-wide sales drop to 0?
    zero_chain_days = daily_sales[daily_sales == 0].index
    print(f"  First day with zero total chain sales: {zero_chain_days.min()}")
    # How many stores carry it?
    print(f"  Stores stocking this SKU: {sub['store_id'].nunique()}")

