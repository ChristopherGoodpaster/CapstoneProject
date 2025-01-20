import tkinter as tk
from tkinter import messagebox
import json
import threading
import time
import schedule
import subprocess
import os
import pandas as pd

###############################################################################
# GLOBALS
###############################################################################
URLS_FILE = "product_urls.json"
scheduler_running = False
scheduler_thread = None

interval_value = 1       # numeric value
interval_unit = "hours"  # can be "minutes", "hours", or "daily_8_20"
daily_times = ["08:00", "20:00"]  # e.g. 8:00AM & 8:00PM daily (local time)

# We'll define these later in show_gui()
changes_text = None

###############################################################################
# HELPER FUNCTIONS
###############################################################################
def load_product_urls():
    try:
        with open(URLS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_product_urls(urls):
    with open(URLS_FILE, 'w') as file:
        json.dump(urls, file, indent=4)

def compute_48h_changes(df):
    """
    Returns a list of (nickname, price_diff) for products 
    that have data within the last 48 hours.
    price_diff = last_price - first_price in that window.
    """
    if df.empty:
        return []

    if 'date_only' not in df.columns or 'price' not in df.columns or 'nickname' not in df.columns:
        return []

    # Convert date_only to datetime if not already
    df['date_only'] = pd.to_datetime(df['date_only'], errors='coerce')
    df.dropna(subset=['date_only', 'price', 'nickname'], inplace=True)

    if df.empty:
        return []

    latest_date = df['date_only'].max()
    cutoff = latest_date - pd.Timedelta(hours=48)
    recent_df = df[df['date_only'] >= cutoff].copy()

    if recent_df.empty:
        return []

    # Sort by date so first is earliest, last is latest
    recent_df.sort_values('date_only', inplace=True)

    grouped = recent_df.groupby('nickname').agg(
        first_price=('price', 'first'),
        last_price=('price', 'last')
    )
    grouped['price_diff'] = grouped['last_price'] - grouped['first_price']
    grouped.reset_index(inplace=True)

    # Return list of tuples
    changes = []
    for _, row in grouped.iterrows():
        changes.append((row['nickname'], row['price_diff']))

    return changes

def update_48h_changes():
    """
    Loads the latest 'price_history.csv', computes 48h changes,
    then updates the 'changes_text' widget in the GUI.
    """
    global changes_text
    try:
        df = pd.read_csv("price_history.csv")
        if df.empty:
            changes_text.delete("1.0", tk.END)
            changes_text.insert(tk.END, "No data in price_history.csv.")
            return
    except Exception as e:
        changes_text.delete("1.0", tk.END)
        changes_text.insert(tk.END, f"Error loading price_history.csv: {e}")
        return

    # Compute changes
    changes = compute_48h_changes(df)

    # Display them
    changes_text.delete("1.0", tk.END)
    if not changes:
        changes_text.insert(tk.END, "No data or no price changes in the last 48 hours.")
    else:
        for (nick, diff) in changes:
            changes_text.insert(tk.END, f"{nick}: {diff:+.2f}\n")

###############################################################################
# MAIN SCHEDULER / SCRIPTS
###############################################################################
def run_price_script():
    """
    Runs generate_data.py, then clean_data.py, then updates 48h changes.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        generate_data_path = os.path.join(script_dir, "generate_data.py")
        clean_data_path = os.path.join(script_dir, "clean_data.py")

        # 1) Run generate_data.py
        print(f"Running generate_data.py at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
        subprocess.run(["python", generate_data_path], check=True)
        print("Script executed successfully.\n")

        # 2) Now run clean_data.py
        print("Now running clean_data.py...")
        subprocess.run(["python", clean_data_path], check=True)
        print("Clean data script executed successfully.\n")

        # 3) Update last 48h changes in the GUI
        update_48h_changes()

    except Exception as e:
        print(f"Error running script: {e}\n")

def set_interval(value, unit, current_frequency_label):
    global interval_value, interval_unit
    interval_value = value
    interval_unit = unit

    if unit == "minutes":
        current_frequency_label.config(text=f"Current Frequency: Every {value} Minute(s)")
    elif unit == "hours":
        current_frequency_label.config(text=f"Current Frequency: Every {value} Hour(s)")
    elif unit == "daily_8_20":
        current_frequency_label.config(text="Current Frequency: 8:00AM & 8:00PM Daily")
    else:
        current_frequency_label.config(text="Unknown frequency mode.")

    print(f"Scheduler set to: {current_frequency_label.cget('text')}")

def start_scheduler():
    """Starts the scheduler to fetch data at the chosen interval, then runs script immediately."""
    def run_schedule():
        while scheduler_running:
            schedule.run_pending()
            time.sleep(1)

    global scheduler_running, scheduler_thread, interval_value, interval_unit

    if not scheduler_running:
        scheduler_running = True
        schedule.clear()  # Clear any old jobs

        import schedule
        if interval_unit == "minutes":
            schedule.every(interval_value).minutes.do(run_price_script)
            print(f"Scheduler started (every {interval_value} minute(s)).")

        elif interval_unit == "hours":
            schedule.every(interval_value).hours.do(run_price_script)
            print(f"Scheduler started (every {interval_value} hour(s)).")

        elif interval_unit == "daily_8_20":
            for t in daily_times:
                schedule.every().day.at(t).do(run_price_script)
            print(f"Scheduler started (daily at {', '.join(daily_times)}).")

        else:
            print("No valid interval mode selected. Scheduler not started.")
            scheduler_running = False
            return

        scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        scheduler_thread.start()

        # Run immediately once
        print("Running script immediately after scheduler start...")
        run_price_script()
    else:
        print("Scheduler is already running.")

def stop_scheduler():
    global scheduler_running
    if scheduler_running:
        scheduler_running = False
        schedule.clear()
        print("Scheduler stopped.")

def toggle_scheduler(button, timestamp_label):
    if scheduler_running:
        stop_scheduler()
        button.config(text="Start Scheduler", bg="green")
        timestamp_label.config(text="Scheduler is OFF.")
    else:
        start_scheduler()
        button.config(text="Stop Scheduler", bg="red")
        turned_on_time = time.strftime('%Y-%m-%d %H:%M:%S')
        timestamp_label.config(text=f"Scheduler turned ON at {turned_on_time}")

###############################################################################
# PRODUCT MANAGEMENT
###############################################################################
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

###############################################################################
# NEW: RUN GRAPH.PY
###############################################################################
def run_graph_script():
    """
    Runs graph.py as a subprocess, which should open the graph interface/window
    if graph.py is set up to do that.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        graph_path = os.path.join(script_dir, "graph.py")

        print("Running graph.py now...")
        subprocess.run(["python", graph_path], check=True)
        print("Graph script executed successfully.\n")

    except Exception as e:
        print(f"Error running graph script: {e}")

###############################################################################
# GUI INIT
###############################################################################
def show_gui():
    app = tk.Tk()
    app.title("Product Manager")
    app.geometry("520x780")

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

    tk.Label(freq_frame, text="Select Scheduler Frequency:", font=("Arial", 12)).pack(pady=5)

    current_frequency_label = tk.Label(freq_frame, text="Current Frequency: Every 1 Hour(s)", font=("Arial", 10))
    current_frequency_label.pack(pady=5)

    btn_1m = tk.Button(freq_frame, text="Every 1 Minute",
                       command=lambda: set_interval(1, "minutes", current_frequency_label))
    btn_1m.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_1h = tk.Button(freq_frame, text="Every 1 Hour",
                       command=lambda: set_interval(1, "hours", current_frequency_label))
    btn_1h.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_3h = tk.Button(freq_frame, text="Every 3 Hours",
                       command=lambda: set_interval(3, "hours", current_frequency_label))
    btn_3h.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_6h = tk.Button(freq_frame, text="Every 6 Hours",
                       command=lambda: set_interval(6, "hours", current_frequency_label))
    btn_6h.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_12h = tk.Button(freq_frame, text="Every 12 Hours",
                        command=lambda: set_interval(12, "hours", current_frequency_label))
    btn_12h.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_8am_8pm = tk.Button(freq_frame, text="8:00 AM & 8:00 PM",
                            command=lambda: set_interval(None, "daily_8_20", current_frequency_label))
    btn_8am_8pm.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    # Scheduler Button & Timestamp
    scheduler_button = tk.Button(app, text="Start Scheduler", bg="green",
                                 font=("Arial", 12), width=20)
    scheduler_button.pack(pady=10)

    timestamp_label = tk.Label(app, text="Scheduler is OFF.", font=("Arial", 10), fg="blue")
    timestamp_label.pack(pady=5)

    scheduler_button.config(command=lambda: toggle_scheduler(scheduler_button, timestamp_label))

    # ---- Last 48h Changes Section ----
    tk.Label(app, text="Last 48h Changes:", font=("Arial", 12)).pack(pady=5)
    global changes_text
    changes_text = tk.Text(app, width=60, height=8, wrap="word")
    changes_text.pack(pady=5)

    # A button to run generate_data.py + clean_data.py on demand
    def on_check_changes_now():
        run_price_script()  # triggers new data fetch + update_48h_changes

    check_changes_btn = tk.Button(
        app,
        text="Check 48h Changes Now",
        bg="lightgreen",
        font=("Arial", 12),
        command=on_check_changes_now
    )
    check_changes_btn.pack(pady=5)

    # ---- NEW BUTTON: RUN GRAPH.PY ----
    run_graph_btn = tk.Button(
        app,
        text="Open Graph Program",
        bg="lightblue",
        font=("Arial", 12),
        command=run_graph_script
    )
    run_graph_btn.pack(pady=10)

    app.mainloop()

if __name__ == "__main__":
    show_gui()
