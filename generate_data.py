import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pandas as pd

# Dictionary mapping product URLs to nicknames
PRODUCT_NICKNAMES = {
    "https://www.amazon.com/Ring-Battery-Doorbell-Head-to-Toe-Video-Satin-Nickel/dp/B0BZWRSRWV?ref=dlx_cyber_dg_dcl_B0BZWRSRWV_dt_sl7_1a": "ring",
    "https://www.amazon.com/dp/B09HMV6K1W": "mouse",
    "https://www.amazon.com/dp/B0BG1X8JGV": "display_pad"
}

def fetch_amazon_data(url, headers):
    """
    Fetches product data from an Amazon product page.
    Returns a dictionary with nickname, title, and price.
    """
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

        return {
            'nickname': PRODUCT_NICKNAMES.get(url, "unknown"),
            'title': title,
            'price': price
        }
    else:
        raise Exception(f"Failed to fetch the page. Status code: {response.status_code}")

def initialize_database(db_name='amazon_tracker.db'):
    """
    Initializes the SQLite database to store product data.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS products')  # Drop existing table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nickname TEXT,
            title TEXT,
            price REAL,
            date TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def store_data_in_db(data, db_name='amazon_tracker.db'):
    """
    Stores product data into the database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO products (nickname, title, price, date)
        VALUES (?, ?, ?, ?)
    ''', (data['nickname'], data['title'], data['price'], datetime.now()))
    conn.commit()
    conn.close()

def fetch_price_history(db_name='amazon_tracker.db'):
    """
    Fetches the price history of all products from the database.
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    cursor.execute('SELECT nickname, title, price, date FROM products ORDER BY date ASC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def main():
    """
    Main function to fetch product data, store it in the database, and export it to CSV.
    """
    product_urls = [
        "https://www.amazon.com/Ring-Battery-Doorbell-Head-to-Toe-Video-Satin-Nickel/dp/B0BZWRSRWV?ref=dlx_cyber_dg_dcl_B0BZWRSRWV_dt_sl7_1a",
        "https://www.amazon.com/dp/B09HMV6K1W",
        "https://www.amazon.com/dp/B0BG1X8JGV"
    ]

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9"
    }

    initialize_database()

    for url in product_urls:
        try:
            product_data = fetch_amazon_data(url, headers)
            if product_data['title'] and product_data['price'] is not None:
                store_data_in_db(product_data)
                print(f"Fetched data for {product_data['nickname']} ({product_data['title']}): {product_data['price']}")
            else:
                print(f"Could not get valid data for URL: {url}")
        except Exception as e:
            print(f"Error fetching URL {url}: {e}")

    history = fetch_price_history()
    if history:
        df = pd.DataFrame(history, columns=["nickname", "title", "price", "date"])

        # Convert date column to a datetime object
        df['date'] = pd.to_datetime(df['date'])

        # Create separate columns for date and time
        df['date_only'] = df['date'].dt.date
        df['time_only'] = df['date'].dt.time

        # Load existing CSV if it exists
        csv_file = 'price_history.csv'
        try:
            existing_df = pd.read_csv(csv_file)
            combined_df = pd.concat([existing_df, df], ignore_index=True)
            combined_df.drop_duplicates(subset=["nickname", "price", "date_only", "time_only"], inplace=True)
        except FileNotFoundError:
            combined_df = df

        # Save only the required columns to the CSV
        combined_df = combined_df[["nickname", "title", "price", "date_only", "time_only"]]
        combined_df.to_csv('price_history.csv', index=False)
        print("Price history has been updated and saved to price_history.csv")
    else:
        print("No data found in database.")

if __name__ == "__main__":
    main()
