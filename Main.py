
# MAIN

### Project Setup and Data Collection ###
import requests
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime

# RapidAPI setup
API_HOST = "real-time-amazon-data.p.rapidapi.com"
API_KEY = "YOUR_RAPIDAPI_KEY"

# Headers for API requests
headers = {
    "X-RapidAPI-Host": API_HOST,
    "X-RapidAPI-Key": API_KEY
}

# Product ASINs to track (add ASINs of products you want to monitor)
product_asins = ["B08J5F3G18", "B07XJ8C8F5"]

# Fetch product data for each ASIN
def fetch_product_data(asin):
    url = f"https://real-time-amazon-data.p.rapidapi.com/product/{asin}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return {
            "ASIN": asin,
            "title": data.get("title", ""),
            "price": data.get("price", None),
            "availability": data.get("availability", ""),
            "timestamp": datetime.now()
        }
    else:
        print(f"Error: {response.status_code} for ASIN {asin}")
        return None

# Collect data for all ASINs
product_data = [fetch_product_data(asin) for asin in product_asins]
product_df = pd.DataFrame([data for data in product_data if data])

### Data Cleaning and Transformation ###
# Drop rows with missing price values
product_df = product_df.dropna(subset=['price'])

# Convert price to numeric type, if needed
product_df['price'] = pd.to_numeric(product_df['price'], errors='coerce')

### Data Storage and Retrieval with SQL ###
# Connect to SQLite database
conn = sqlite3.connect("amazon_product_tracker.db")
cursor = conn.cursor()

# Create a table for product data if it doesn't exist
cursor.execute("""
CREATE TABLE IF NOT EXISTS ProductData (
    ASIN TEXT,
    title TEXT,
    price REAL,
    availability TEXT,
    timestamp TIMESTAMP
)
""")

# Insert product data into the SQL database
product_df.to_sql('ProductData', conn, if_exists='append', index=False)

# Retrieve all data for a specific product from the database
def get_product_data(asin):
    query = f"SELECT * FROM ProductData WHERE ASIN='{asin}'"
    return pd.read_sql_query(query, conn)

### Data Analysis and Visualization ###
# Generate price trend visualization for each product
for asin in product_asins:
    asin_data = get_product_data(asin)
    
    # Plot price over time
    plt.figure(figsize=(10, 6))
    plt.plot(asin_data['timestamp'], asin_data['price'], marker='o', label='Price')
    plt.title(f"Price Trend for {asin_data['title'][0]} (ASIN: {asin})")
    plt.xlabel("Timestamp")
    plt.ylabel("Price")
    plt.xticks(rotation=45)
    plt.legend()
    plt.show()

# Close the database connection
conn.close()

### Interpretation and Documentation ###
# README Documentation
readme_content = """
# Amazon Product Tracker

This project tracks specific Amazon products' prices and availability over time using the Real-Time Amazon Data API. This analysis provides insights into price trends and item availability for informed decision-making.

## Features
- **Data Collection**: Collects real-time data on product prices and availability.
- **Data Cleaning**: Cleans and structures data for analysis.
- **Data Storage**: Stores data in a SQL database for future analysis.
- **Data Visualization**: Displays price history and trends using Matplotlib.

## Setup
1. Replace `YOUR_RAPIDAPI_KEY` with your actual API key in the code.
2. Install required packages with `pip install -r requirements.txt`.
3. Run the Jupyter Notebook to track selected products.

## Data Source
- Real-Time Amazon Data API on RapidAPI.

## Interpretation
This analysis reveals pricing trends for selected products, offering insights for monitoring price changes or availability over time.
"""

# Write README to file
with open("README.md", "w") as file:
    file.write(readme_content)

