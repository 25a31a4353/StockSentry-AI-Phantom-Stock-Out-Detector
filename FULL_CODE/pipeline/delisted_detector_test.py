import pandas as pd
import numpy as np

# Load parquet
df = pd.read_parquet('data/daily_sales_inventory.parquet')

# Compute daily chain-wide sales per SKU
chain_sales = df.groupby(['date', 'sku_id'])['units_sold'].sum().unstack('sku_id', fill_value=0)

# Also compute number of stores selling per SKU per day
stores_selling = df[df['units_sold'] > 0].groupby(['date', 'sku_id'])['store_id'].nunique().unstack('sku_id', fill_value=0)

print("Chain sales matrix shape:", chain_sales.shape)

# Let's inspect rolling 7-day and 14-day chain-wide sales
# For any date D, if a SKU had mean chain sales > 5/day in days [D-28 to D-7], but in days [D-7 to D-1] had chain_sales == 0:
# which SKUs trigger this?
suspects = set()
for date_idx in range(50, len(chain_sales)):
    d = chain_sales.index[date_idx]
    # Lookback 28 days before the last 5 days
    hist_mean = chain_sales.iloc[date_idx-28:date_idx-5].mean(axis=0)
    recent_sum = chain_sales.iloc[date_idx-5:date_idx].sum(axis=0)
    
    # Delisted criterion: was selling heavily across chain (> 5 units/day), but zero sales chain-wide in recent 5 days
    flagged = chain_sales.columns[(hist_mean > 5.0) & (recent_sum == 0)]
    for sk in flagged:
        suspects.add((sk, str(d.date())))

print(f"Total (SKU, date) pairs flagged by general point-in-time delisting rule: {len(suspects)}")
unique_flagged_skus = {sk for sk, d in suspects}
print(f"Unique SKUs flagged by rule: {unique_flagged_skus}")

