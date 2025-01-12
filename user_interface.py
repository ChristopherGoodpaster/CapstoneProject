import tkinter as tk
from tkinter import messagebox
import json
import threading
import time
import schedule
import subprocess
import os

URLS_FILE = "product_urls.json"

# Global variables for scheduler state and interval
scheduler_running = False
scheduler_thread = None
interval_var = 1  # Default interval in hours (can be 1, 6, 12, etc.)

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

def run_price_script():
    """Run the generate_data.py script with an absolute path."""
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        generate_data_path = os.path.join(script_dir, "generate_data.py")

        print(f"Running generate_data.py at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
        subprocess.run(["python", generate_data_path], check=True)
        print("Script executed successfully.\n")
    except Exception as e:
        print(f"Error running script: {e}\n")

def set_interval(hours, current_frequency_label):
    """
    Sets the global interval_var to 'hours'.
    Also updates the label showing the current frequency.
    """
    global interval_var
    interval_var = hours
    current_frequency_label.config(
        text=f"Current Frequency: Every {interval_var} Hour(s)"
    )
    print(f"Scheduler frequency set to {hours} hour(s).")

def start_scheduler():
    """Starts the scheduler to fetch data at the chosen interval."""
    def run_schedule():
        while scheduler_running:
            schedule.run_pending()
            time.sleep(1)

    global scheduler_running, scheduler_thread

    if not scheduler_running:
        scheduler_running = True
        # Clear any old jobs to avoid duplicates
        schedule.clear()

        # Schedule based on the chosen interval (in hours)
        schedule.every(interval_var).hours.do(run_price_script)

        # Start the background thread
        scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        scheduler_thread.start()
        print(f"Scheduler started. Interval: {interval_var} hour(s).")
    else:
        print("Scheduler is already running.")

def stop_scheduler():
    """Stops the scheduler."""
    global scheduler_running
    if scheduler_running:
        scheduler_running = False
        schedule.clear()
        print("Scheduler stopped.")

def toggle_scheduler(button):
    """Toggles the scheduler on and off, updating the button text and color."""
    if scheduler_running:
        stop_scheduler()
        button.config(text="Start Scheduler", bg="green")
    else:
        start_scheduler()
        button.config(text="Stop Scheduler", bg="red")

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

def show_gui():
    app = tk.Tk()
    app.title("Product Manager")
    app.geometry("400x580")

    # Frame for Adding Products
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

    # Frame for Managing Products
    manage_frame = tk.Frame(app)
    manage_frame.pack(pady=10)

    tk.Label(manage_frame, text="Products:").pack()

    global product_listbox
    product_listbox = tk.Listbox(manage_frame, width=50, height=10)
    product_listbox.pack(pady=5)

    delete_button = tk.Button(manage_frame, text="Delete Selected Product", command=delete_product)
    delete_button.pack(pady=5)

    refresh_product_list()

    # Frame for Scheduler Frequency
    freq_frame = tk.Frame(app, bd=2, relief="ridge")
    freq_frame.pack(pady=10, fill="x", padx=20)

    tk.Label(freq_frame, text="Select Scheduler Frequency (Hours):", font=("Arial", 12)).pack(pady=5)

    # Label to show the current frequency chosen
    current_frequency_label = tk.Label(freq_frame, text="Current Frequency: Every 1 Hour(s)", font=("Arial", 10))
    current_frequency_label.pack(pady=5)

    btn_1h = tk.Button(
        freq_frame,
        text="Every 1 Hour",
        command=lambda: set_interval(1, current_frequency_label)
    )
    btn_1h.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    btn_6h = tk.Button(
        freq_frame,
        text="Every 6 Hours",
        command=lambda: set_interval(6, current_frequency_label)
    )
    btn_6h.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    btn_12h = tk.Button(
        freq_frame,
        text="Every 12 Hours",
        command=lambda: set_interval(12, current_frequency_label)
    )
    btn_12h.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    # Scheduler Button
    scheduler_button = tk.Button(
        app,
        text="Start Scheduler",
        bg="green",
        command=lambda: toggle_scheduler(scheduler_button),
        font=("Arial", 12),
        width=20
    )
    scheduler_button.pack(pady=20)

    app.mainloop()

if __name__ == "__main__":
    show_gui()
