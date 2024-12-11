import tkinter as tk
from tkinter import messagebox
import json
import subprocess
import os

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

# Variables to manage the scheduler process
scheduler_process = None

def toggle_scheduler():
    """
    Starts or stops the scheduler.py script when the button is clicked.
    """
    global scheduler_process
    if scheduler_process is None:
        try:
            scheduler_process = subprocess.Popen(["python", "scheduler.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            scheduler_button.config(text="Stop Scheduler")
            messagebox.showinfo("Scheduler", "Scheduler started successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scheduler: {e}")
    else:
        try:
            scheduler_process.terminate()
            scheduler_process = None
            scheduler_button.config(text="Start Scheduler")
            messagebox.showinfo("Scheduler", "Scheduler stopped successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to stop scheduler: {e}")

# GUI functions for managing products
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
    global nickname_entry, url_entry, product_listbox, scheduler_button

    app = tk.Tk()
    app.title("Product Manager")
    app.geometry("400x500")

    add_frame = tk.Frame(app)
    add_frame.pack(pady=10)

    tk.Label(add_frame, text="Nickname:").grid(row=0, column=0, padx=5, pady=5)
    nickname_entry = tk.Entry(add_frame)
    nickname_entry.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(add_frame, text="URL:").grid(row=1, column=0, padx=5, pady=5)
    url_entry = tk.Entry(add_frame, width=30)
    url_entry.grid(row=1, column=1, padx=5, pady=5)

    add_button = tk.Button(add_frame, text="Add Product", command=add_product)
    add_button.grid(row=2, column=0, columnspan=2, pady=10)

    manage_frame = tk.Frame(app)
    manage_frame.pack(pady=10)

    tk.Label(manage_frame, text="Products:").pack()

    product_listbox = tk.Listbox(manage_frame, width=50, height=10)
    product_listbox.pack(pady=5)

    delete_button = tk.Button(manage_frame, text="Delete Selected Product", command=delete_product)
    delete_button.pack(pady=5)

    # Scheduler Control
    scheduler_button = tk.Button(app, text="Start Scheduler", command=toggle_scheduler, bg="green", fg="white")
    scheduler_button.pack(pady=20)

    refresh_product_list()
    app.mainloop()

if __name__ == "__main__":
    show_gui()
