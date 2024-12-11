import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Load historical data from CSV
df = pd.read_csv('price_history.csv')
df['date_only'] = pd.to_datetime(df['date_only'])  # Ensure date column is properly formatted

# Use the nickname column for readability
unique_products = df['nickname'].unique()

# Create a figure with a 2x2 grid layout
fig, axes = plt.subplots(2, 2, figsize=(16, 16))  # 2 rows, 2 columns

# Visualization 1: Line Plot for Price Trends Over Time
axes[0, 0].set_title("Price Trends Over Time for Multiple Products", fontsize=16)
for product in unique_products:
    product_data = df[df['nickname'] == product].sort_values(by='date_only')
    axes[0, 0].plot(product_data['date_only'], product_data['price'], marker='o', linestyle='-', label=product)

axes[0, 0].set_xlabel("Date", fontsize=12)
axes[0, 0].set_ylabel("Price ($)", fontsize=12)
axes[0, 0].tick_params(axis='x', rotation=45)
axes[0, 0].grid(True, linestyle='--', alpha=0.7)
axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
axes[0, 0].legend(title="Products", loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)

# Visualization 2: Bar Chart of Average Prices
avg_price = df.groupby('nickname')['price'].mean().reset_index()
sns.barplot(data=avg_price, x='nickname', y='price', palette='viridis', ax=axes[0, 1])
axes[0, 1].set_title("Average Price per Product", fontsize=16)
axes[0, 1].set_xlabel("Product", fontsize=12)
axes[0, 1].set_ylabel("Average Price ($)", fontsize=12)
axes[0, 1].tick_params(axis='x', rotation=45)
axes[0, 1].legend([], [], frameon=False)  # Suppress legend for bar chart

# Visualization 3: Boxplot of Price Distribution
sns.boxplot(data=df, x='nickname', y='price', palette='Set2', ax=axes[1, 0])
axes[1, 0].set_title("Price Distribution per Product", fontsize=16)
axes[1, 0].set_xlabel("Product", fontsize=12)
axes[1, 0].set_ylabel("Price ($)", fontsize=12)
axes[1, 0].tick_params(axis='x', rotation=45)
axes[1, 0].legend([], [], frameon=False)  # Suppress legend for boxplot

# Visualization 4: Pivot Table with Price Trends
pivot_table = pd.pivot_table(df, values='price', index='date_only', columns='nickname', aggfunc='mean')
for column in pivot_table.columns:
    axes[1, 1].plot(pivot_table.index, pivot_table[column], marker='o', label=column)

axes[1, 1].set_title("Pivot Table: Price Trends Over Time", fontsize=16)
axes[1, 1].set_xlabel("Date", fontsize=12)
axes[1, 1].set_ylabel("Average Price ($)", fontsize=12)
axes[1, 1].tick_params(axis='x', rotation=45)
axes[1, 1].grid(True, linestyle='--', alpha=0.7)
axes[1, 1].legend(title="Products", loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)

# Adjust spacing between subplots
plt.tight_layout()
plt.show()
