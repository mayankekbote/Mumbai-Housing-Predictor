import pandas as pd

print('Reading files from C:\\ML_Project')

df = pd.read_csv('mumbai_region_coords.csv', encoding='latin1')
mumbai = pd.read_csv('mumbai_cleaned.csv', encoding='latin1')

# normalize column names like mlfrontend.py does
for df_name, d in [('coords', df), ('mumbai', mumbai)]:
    d.columns = d.columns.str.strip().str.lower()
    print(f"{df_name} columns: {list(d.columns)}\n")

median_prices = mumbai.groupby('region')['price_per_sqft'].median().reset_index()
median_prices.rename(columns={'price_per_sqft': 'median_price'}, inplace=True)
print('median_prices columns:', list(median_prices.columns))

merged = pd.merge(df, median_prices, on='region', how='left')
print('merged columns:', list(merged.columns))

# show a few rows
print('\nmerged head:')
print(merged.head().to_string())
