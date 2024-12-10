import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates

# Load historical data from CSV
df = pd.read_csv('price_history.csv')
df['date'] = pd.to_datetime(df['date'])

unique_products = df['title'].unique()

# Visualization 1: Line Plot
plt.figure(figsize=(10,6))
for product in unique_products:
    product_data = df[df['title'] == product].sort_values(by='date')
    short_label = ' '.join(product.split()[:4])
    plt.plot(product_data['date'], product_data['price'], marker='o', linestyle='-', label=short_label)

plt.title("Historical Price Tracking for Multiple Products")
plt.xlabel("Date")
plt.ylabel("Price ($)")
plt.xticks(rotation=45)
plt.grid(True)
plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d %H:%M:%S'))
plt.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
plt.tight_layout()

# Visualization 2: Bar Chart of Average Prices
avg_price = df.groupby('title')['price'].mean().reset_index()
plt.figure(figsize=(8, 5))
sns.barplot(x='title', y='price', data=avg_price, palette='viridis')
plt.title("Average Price per Product")
plt.xlabel("Product")
plt.ylabel("Average Price ($)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Visualization 3: Boxplot of Price Distribution
plt.figure(figsize=(8, 5))
sns.boxplot(x='title', y='price', data=df, palette='Set2')
plt.title("Price Distribution per Product")
plt.xlabel("Product")
plt.ylabel("Price ($)")
plt.xticks(rotation=45, ha='right')
plt.tight_layout()

# Call show only once, after all figures are created
plt.show()
