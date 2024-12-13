import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pandas as pd
import json

# File containing product URLs and nicknames
URLS_FILE = "product_urls.json"

# Section: Load Product URLs
def load_product_urls():
    """Loads product URLs and nicknames from a JSON file."""
    try:
        with open(URLS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

# Section: Fetch Data from Amazon
def fetch_amazon_data(url, headers):
    """
    Fetches product data from an Amazon product page.
    Parses the HTML to extract the product title and price.
    Returns a dictionary with the nickname, title, price, and URL.
    """
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract the title of the product
        title_element = soup.find(id='productTitle')
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"

        # Extract the price of the product
        price_element = soup.find('span', {'class': 'a-offscreen'})
        if price_element:
            price_str = price_element.get_text(strip=True).replace('$', '').replace(',', '')
            try:
                price = float(price_str)
            except ValueError:
                price = None  # If price conversion fails, set to None
        else:
            price = None  # If price element is not found

        # Warn if no valid price was found
        if price is None:
            print(f"Warning: Could not fetch a valid price for {title}. Skipping...")
            return None

        return {
            'title': title,
            'price': price,
            'url': url
        }
    else:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

# Section: Initialize Database
def initialize_database(db_name='amazon_tracker.db'):
    """
    Creates and initializes the SQLite database.
    Drops the existing table if it exists and creates a fresh one.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS products')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT,
            title TEXT,
            price REAL,
            url TEXT,
            date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Section: Store Data in Database
def store_data_in_db(data, nickname, db_name='amazon_tracker.db'):
    """Inserts the fetched product data into the SQLite database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (nickname, title, price, url, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (nickname, data['title'], data['price'], data['url'], datetime.now()))
    conn.commit()
    conn.close()

# Section: Fetch Price History
def fetch_price_history(db_name='amazon_tracker.db'):
    """Fetches all historical price records from the SQLite database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT nickname, title, price, url, date FROM products ORDER BY date ASC')
    rows = cursor.fetchall()
    conn.close()
    return rows

# Section: Main Script Workflow
def main():
    """
    Main workflow for the script:
    1. Loads product URLs from a JSON file.
    2. Initializes the SQLite database.
    3. Fetches product data for each URL.
    4. Stores data in the database.
    5. Fetches price history and saves it to a CSV file.
    """
    product_urls = load_product_urls()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    # Initialize database
    initialize_database()

    # Fetch data for each product and store in the database
    for nickname, url in product_urls.items():
        try:
            product_data = fetch_amazon_data(url, headers)
            if product_data['title'] and product_data['price'] is not None:
                store_data_in_db(product_data, nickname)
                print(f"Fetched data for {nickname} ({product_data['title']}): {product_data['price']}")
            else:
                print(f"Could not get valid data for URL: {url}")
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")

    # Fetch and process price history
    history = fetch_price_history()
    if history:
        # Convert to DataFrame and preprocess
        df = pd.DataFrame(history, columns=["nickname", "title", "price", "url", "date"])
        df['date'] = pd.to_datetime(df['date'])
        df['date_only'] = df['date'].dt.date
        df['time_only'] = df['date'].dt.time

        # Save to CSV, avoiding duplicates
        csv_file = 'price_history.csv'
        try:
            existing_df = pd.read_csv(csv_file)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=["nickname", "price", "date_only", "time_only"], inplace=True)
        except FileNotFoundError:
            combined_df = df

        # Finalize and save the cleaned DataFrame
        combined_df = combined_df[["nickname", "title", "price", "url", "date_only", "time_only"]]
        combined_df.to_csv('price_history.csv', index=False)
        print("Price history has been updated and saved to price_history.csv")
    else:
        print("No data found in database.")

# Run the main function if executed as a script
if __name__ == "__main__":
    main()
