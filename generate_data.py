import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pandas as pd

def fetch_amazon_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        title_element = soup.find(id='productTitle')
        title = title_element.get_text(strip=True) if title_element else None

        price_element = soup.find('span', {'class': 'a-offscreen'})
        if price_element:
            price_str = price_element.get_text(strip=True).replace('$', '').replace(',', '')
            try:
                price = float(price_str)
            except ValueError:
                price = None
        else:
            price = None

        return {'title': title, 'price': price}
    else:
        # If we fail to fetch the page, raise an exception with the status code
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

def initialize_database(db_name='amazon_tracker.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price REAL,
            date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def store_data_in_db(data, db_name='amazon_tracker.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (title, price, date)
        VALUES (?, ?, ?)
    ''', (data['title'], data['price'], datetime.now()))
    conn.commit()
    conn.close()

def fetch_price_history(db_name='amazon_tracker.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT title, price, date FROM products ORDER BY date ASC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    # List of product URLs (use simple dp/ASIN format)
    product_urls = [
        "https://www.amazon.com/Ring-Battery-Doorbell-Head-to-Toe-Video-Satin-Nickel/dp/B0BZWRSRWV?ref=dlx_cyber_dg_dcl_B0BZWRSRWV_dt_sl7_1a", # Example product
        # Add more product URLs here
         "https://www.amazon.com/dp/B09HMV6K1W",  # Logitech Wireless Bluetooth Mouse
        "https://www.amazon.com/dp/B0BG1X8JGV"   # MOUNTAIN DISPLAYPAD
        # "https://www.amazon.com/Ring-Battery-Doorbell-Head-to-Toe-Video-Satin-Nickel/dp/B0BZWRSRWV?ref=dlx_cyber_dg_dcl_B0BZWRSRWV_dt_sl7_1a", # Example second product
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    initialize_database()

    # Attempt to fetch and store each product
    for url in product_urls:
        try:
            product_data = fetch_amazon_data(url, headers)
            if product_data['title'] and product_data['price'] is not None:
                store_data_in_db(product_data)
                print(f"Fetched data for {product_data['title']}: {product_data['price']}")
            else:
                print(f"Could not get valid data for URL: {url}")
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")

    # Fetch full price history and export to CSV
    history = fetch_price_history()
    if history:
        df = pd.DataFrame(history, columns=["title", "price", "date"])
        df.to_csv('price_history.csv', index=False)
        print("Price history has been saved to price_history.csv")
    else:
        print("No data found in database.")

if __name__ == "__main__":
    main()
