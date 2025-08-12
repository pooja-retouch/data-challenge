import pandas as pd
import numpy as np

# Load dataset
df = pd.read_csv("nigeria_agricultural_exports.csv")
df['Date'] = pd.to_datetime(df['Date'])
df['Year'] = df['Date'].dt.year
df['Month'] = df['Date'].dt.month
df['Quarter'] = df['Date'].dt.to_period('Q')

# Ensure numeric export value
df['Export Value'] = pd.to_numeric(df['Export Value'], errors='coerce')

# 1. Product with highest % increase in export value over years
product_year_value = df.groupby(['Product Name', 'Year'])['Export Value'].sum().reset_index()
first_last = product_year_value.groupby('Product Name').agg(
    first_year=('Year', 'min'),
    last_year=('Year', 'max'),
    first_value=('Export Value','first'),
    last_value=('Export Value', 'last')
).reset_index()
first_last['pct_increase'] = ((first_last['last_value'] - first_last['first_value']) / first_last['first_value']) * 100
top_increase_product = first_last.sort_values('pct_increase', ascending=False).iloc[0]
print("\n1. Product with highest % increase in export value:")
print(top_increase_product[['Product Name', 'pct_increase']])

# 2. Seasonal pattern (quarterly or monthly) for perishable products
# Assuming a 'Product Type' column exists and marks 'Perishable'
if 'Product Type' in df.columns:
    perishables = df[df['Product Type'].str.lower() == 'perishable']
else:
    # If no such column, you need to define perishables list manually
    perishables_list = []  # e.g., ["Tomatoes", "Yam", ...]
    perishables = df[df['Product Name'].isin(perishables_list)]

seasonal_pattern = perishables.groupby(['Year', 'Quarter'])['Export Value'].sum().unstack(fill_value=0)
print("\n2. Seasonal pattern for perishables (Quarterly export values):")
print(seasonal_pattern)

# 3. Share of total export revenue from top 3 products each year
top3_share_per_year = []
for year, group in df.groupby('Year'):
    total_revenue = group['Export Value'].sum()
    top3_revenue = group.groupby('Product Name')['Export Value'].sum().nlargest(3).sum()
    share = (top3_revenue / total_revenue) * 100
    top3_share_per_year.append({'Year': year, 'Top3_Share_%': share})

top3_share_df = pd.DataFrame(top3_share_per_year)
print("\n3. Share of total export revenue by top 3 products each year:")
print(top3_share_df)

# 4. Export Countrys with most consistent export performance (lowest variance year-to-year)
Export_Country_year_value = df.groupby(['Export Country', 'Year'])['Export Value'].sum().reset_index()
Export_Country_variance = Export_Country_year_value.groupby('Export Country')['Export Value'].var().reset_index()
Export_Country_variance.rename(columns={'Export Value': 'Variance'}, inplace=True)
consistent_Export_Countrys = Export_Country_variance.sort_values('Variance').head(5)
print("\n4. Export Countrys with most consistent export performance:")
print(consistent_Export_Countrys)
