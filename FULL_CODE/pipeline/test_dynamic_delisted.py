import pandas as pd
import numpy as np

# Load parquet
df = pd.read_parquet('data/daily_sales_inventory.parquet')
dt = pd.read_csv('data/dev_truth.csv')

# Unique dates, stores, skus
dates = np.sort(df['date'].unique())
dates_idx = pd.DatetimeIndex(dates)
chain_sales = df.groupby(['date', 'sku_id'])['units_sold'].sum().unstack('sku_id', fill_value=0)
n_stores_per_sku = df.groupby('sku_id')['store_id'].nunique()

print(f"Total dates: {len(dates)}, SKUs: {chain_sales.shape[1]}")

# Test the dynamic delisting detector for each date in DEV_WINDOW: 2026-06-04 to 2026-09-02
delisted_by_rule = {}
for D in pd.date_range('2026-06-04', '2026-09-02', freq='D'):
    t = int(np.searchsorted(dates_idx.values, np.datetime64(D - pd.Timedelta(days=1))))
    if t < 28:
        continue
    # Look at recent 10 days
    recent_k = 10
    recent_sales = chain_sales.iloc[max(0, t - recent_k + 1):t + 1].sum(axis=0)
    # Look at historical sales before recent_k days
    hist_span = 28
    hist_sales = chain_sales.iloc[max(0, t - recent_k - hist_span + 1):max(0, t - recent_k + 1)].mean(axis=0)
    
    # Dynamic rule: was selling >= 10 units/day across chain, carried in >= 10 stores, now 0 across entire chain for 10 days
    is_delisted = (hist_sales >= 10.0) & (recent_sales == 0) & (n_stores_per_sku >= 10)
    flagged_skus = set(chain_sales.columns[is_delisted])
    if flagged_skus:
        delisted_by_rule[D.strftime('%Y-%m-%d')] = flagged_skus

print(f"Dates with dynamic delisting active: {len(delisted_by_rule)}")
first_date = min(delisted_by_rule.keys()) if delisted_by_rule else None
print(f"First date delisting detected dynamically: {first_date}")
all_detected_skus = set().union(*delisted_by_rule.values()) if delisted_by_rule else set()
print(f"All dynamically detected delisted SKUs: {all_detected_skus}")

# Check against true delisted labels in dev_truth
true_delisted = set(dt[dt['label_type'] == 'delisted']['sku_id'].unique())
print(f"True delisted SKUs in dev truth: {true_delisted}")
print(f"Exact match with true delisted: {all_detected_skus == true_delisted}")

