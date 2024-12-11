import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pandas as pd
import json

URLS_FILE = "product_urls.json"

def load_product_urls():
    """Loads product URLs and nicknames from a JSON file."""
    try:
        with open(URLS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def fetch_amazon_data(url, headers):
    """
    Fetches product data from an Amazon product page.
    Returns a dictionary with nickname, title, price, and url.
    """
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Fetch the title
        title_element = soup.find(id='productTitle')
        title = title_element.get_text(strip=True) if title_element else "Unknown Title"

        # Fetch the price
        price_element = soup.find('span', {'class': 'a-offscreen'})
        if price_element:
            price_str = price_element.get_text(strip=True).replace('$', '').replace(',', '')
            try:
                price = float(price_str)
            except ValueError:
                price = None  # If price conversion fails, set to None
        else:
            price = None  # If price element is not found

        # Handle missing price
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


def initialize_database(db_name='amazon_tracker.db'):
    """Initializes the SQLite database."""
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

def store_data_in_db(data, nickname, db_name='amazon_tracker.db'):
    """Stores product data in the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (nickname, title, price, url, date)
        VALUES (?, ?, ?, ?, ?)
    ''', (nickname, data['title'], data['price'], data['url'], datetime.now()))
    conn.commit()
    conn.close()

def fetch_price_history(db_name='amazon_tracker.db'):
    """Fetches price history from the database."""
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT nickname, title, price, url, date FROM products ORDER BY date ASC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    product_urls = load_product_urls()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    initialize_database()

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

    history = fetch_price_history()
    if history:
        df = pd.DataFrame(history, columns=["nickname", "title", "price", "url", "date"])
        df['date'] = pd.to_datetime(df['date'])
        df['date_only'] = df['date'].dt.date
        df['time_only'] = df['date'].dt.time

        csv_file = 'price_history.csv'
        try:
            existing_df = pd.read_csv(csv_file)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=["nickname", "price", "date_only", "time_only"], inplace=True)
        except FileNotFoundError:
            combined_df = df

        combined_df = combined_df[["nickname", "title", "price", "url", "date_only", "time_only"]]
        combined_df.to_csv('price_history.csv', index=False)
        print("Price history has been updated and saved to price_history.csv")
    else:
        print("No data found in database.")

if __name__ == "__main__":
    main()
