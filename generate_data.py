import requests
from bs4 import BeautifulSoup
import sqlite3
from datetime import datetime
import pandas as pd
import json
import tkinter as tk
from tkinter import messagebox

# File to store the product URLs and nicknames
URLS_FILE = "product_urls.json"

# Load and save functions for product URLs
def load_product_urls():
    """Loads product URLs and nicknames from a JSON file."""
    try:
        with open(URLS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_product_urls(urls):
    """Saves product URLs and nicknames to a JSON file."""
    with open(URLS_FILE, 'w') as file:
        json.dump(urls, file, indent=4)

# Amazon data fetching and database handling
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
                price = None
        else:
            price = None

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
    cursor.execute('DROP TABLE IF EXISTS products')  # Drop existing table
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

# Main logic for fetching data
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

# GUI for managing products
def add_product():
    nickname = nickname_entry.get().strip()
    url = url_entry.get().strip()

    if not nickname or not url:
        messagebox.showerror("Error", "Nickname and URL cannot be empty!")
        return

    product_urls = load_product_urls()
    if nickname in product_urls:
        messagebox.showerror("Error", f"Nickname '{nickname}' already exists.")
    else:
        product_urls[nickname] = url
        save_product_urls(product_urls)
        messagebox.showinfo("Success", f"Added product: {nickname}")
        refresh_product_list()

def delete_product():
    selected_product = product_listbox.get(tk.ACTIVE)
    if not selected_product:
        messagebox.showerror("Error", "No product selected!")
        return

    product_urls = load_product_urls()
    if selected_product in product_urls:
        del product_urls[selected_product]
        save_product_urls(product_urls)
        messagebox.showinfo("Success", f"Deleted product: {selected_product}")
        refresh_product_list()
    else:
        messagebox.showerror("Error", f"Product '{selected_product}' not found.")

def refresh_product_list():
    product_listbox.delete(0, tk.END)
    product_urls = load_product_urls()
    for nickname in product_urls.keys():
        product_listbox.insert(tk.END, nickname)

# GUI Setup
def show_gui():
    app = tk.Tk()
    app.title("Product Manager")
    app.geometry("400x400")

    add_frame = tk.Frame(app)
    add_frame.pack(pady=10)

    tk.Label(add_frame, text="Nickname:").grid(row=0, column=0, padx=5, pady=5)
    global nickname_entry
    nickname_entry = tk.Entry(add_frame)
    nickname_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(add_frame, text="URL:").grid(row=1, column=0, padx=5, pady=5)
    global url_entry
    url_entry = tk.Entry(add_frame, width=30)
    url_entry.grid(row=1, column=1, padx=5, pady=5)

    add_button = tk.Button(add_frame, text="Add Product", command=add_product)
    add_button.grid(row=2, column=0, columnspan=2, pady=10)

    manage_frame = tk.Frame(app)
    manage_frame.pack(pady=10)

    tk.Label(manage_frame, text="Products:").pack()

    global product_listbox
    product_listbox = tk.Listbox(manage_frame, width=50, height=10)
    product_listbox.pack(pady=5)

    delete_button = tk.Button(manage_frame, text="Delete Selected Product", command=delete_product)
    delete_button.pack(pady=5)

    refresh_product_list()
    app.mainloop()

if __name__ == "__main__":
    print("Options:")
    print("1. Fetch and update product data")
    print("2. Open Product Manager GUI")
    choice = input("Enter your choice (1/2): ").strip()

    if choice == "1":
        main()
    elif choice == "2":
        show_gui()
    else:
        print("Invalid choice. Exiting.")
