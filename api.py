#this will be my api code

!pip install requests pandas sqlalchemy


# MAIN
import requests
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
from datetime import datetime
import os

# Set up your API key and endpoint URL
API_KEY = 'YOUR_RAPIDAPI_KEY'
API_HOST = 'real-time-amazon-data.p.rapidapi.com'
SEARCH_ENDPOINT = f"https://{API_HOST}/search"

# 1. Function to fetch product details using ASIN
def fetch_product_details(asin):
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": API_HOST,
    }
    querystring = {"asin": asin}
    
    response = requests.get(f"https://{API_HOST}/product", headers=headers, params=querystring)
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} for ASIN {asin}")
        return None

# 2. Function to extract necessary fields from the API response
def parse_product_data(api_data):
    return {
        "asin": api_data.get("asin"),
        "title": api_data.get("title"),
        "price": api_data.get("prices", [{}])[0].get("price"),
        "availability": api_data.get("availability"),
        "timestamp": datetime.now().isoformat()
    }

# 3. Function to save data to SQLite database
def save_to_database(data, db_name="amazon_products.db"):
    engine = create_engine(f'sqlite:///{db_name}')
    df = pd.DataFrame([data])
    df.to_sql("products", con=engine, if_exists="append", index=False)
    engine.dispose()
    print("Data saved to database.")

# 4. Function to export data for Tableau
def export_for_tableau(db_name="amazon_products.db", export_name="amazon_products.csv"):
    engine = create_engine(f'sqlite:///{db_name}')
    query = "SELECT * FROM products"
    df = pd.read_sql(query, con=engine)
    df.to_csv(export_name, index=False)
    engine.dispose()
    print(f"Data exported for Tableau to {export_name}.")

# 5. MAIN Script Execution: Fetch, Parse, Save, and Export Data
def main(asins):
    for asin in asins:
        api_data = fetch_product_details(asin)
        if api_data:
            product_data = parse_product_data(api_data)
            save_to_database(product_data)

    # Export final dataset for Tableau
    export_for_tableau()

# ASINs to Track
asins_to_track = ["B08N5WRWNW", "B09G3HRMVB", "B07FZ8S74R"]  # Replace with ASINs you want to track
main(asins_to_track)
