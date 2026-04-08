import pandas as pd
import json

# Load the data
mumbai = pd.read_csv("mumbai_cleaned.csv", encoding="latin1")
mumbai.columns = mumbai.columns.str.strip().str.lower()

# Calculate median price per sqft for each region
region_stats = mumbai.groupby("region")["price_per_sqft"].median().sort_values()

# Define 6 quantiles for 6 buckets
qs = [region_stats.quantile(i/6) for i in range(1, 6)]
print(f"Quantiles (6-Bucket): {qs}")

def categorize_6(price):
    if price <= qs[0]: return "Budget"
    if price <= qs[1]: return "Value"
    if price <= qs[2]: return "Mid-Range"
    if price <= qs[3]: return "Premium"
    if price <= qs[4]: return "Luxury"
    return "Ultra-Luxury"

region_buckets = region_stats.apply(categorize_6)
print("\n6-Bucket Region Summary:")
print(region_buckets.value_counts())

# Save to JSON
with open("region_buckets.json", "w") as f:
    json.dump(region_buckets.to_dict(), f, indent=4)

print("\nSaved updated region_buckets.json (6 Buckets)")
