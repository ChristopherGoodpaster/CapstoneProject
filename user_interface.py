import tkinter as tk
from tkinter import messagebox
import json
import threading
import time
import schedule
import subprocess
import os

URLS_FILE = "product_urls.json"

scheduler_running = False
scheduler_thread = None

# We'll store scheduling info:
interval_value = 1       # numeric value
interval_unit = "hours"  # can be "minutes", "hours", or "daily_8_20"
daily_times = ["08:00", "20:00"]  # 8:00AM & 8:00PM daily (local time)

def load_product_urls():
    try:
        with open(URLS_FILE, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_product_urls(urls):
    with open(URLS_FILE, 'w') as file:
        json.dump(urls, file, indent=4)

def run_price_script():
    """
    Run generate_data.py, then automatically run clean_data.py.
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

    except Exception as e:
        print(f"Error running script: {e}\n")

def set_interval(value, unit, current_frequency_label):
    """
    Updates the global interval_value and interval_unit.
    Also updates the label so user knows which scheduling mode is selected.
    """
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
        schedule.clear()  # Clear any old jobs to avoid duplicates

        # Configure schedule based on interval_unit
        if interval_unit == "minutes":
            schedule.every(interval_value).minutes.do(run_price_script)
            print(f"Scheduler started (every {interval_value} minute(s)).")

        elif interval_unit == "hours":
            schedule.every(interval_value).hours.do(run_price_script)
            print(f"Scheduler started (every {interval_value} hour(s)).")

        elif interval_unit == "daily_8_20":
            # Schedule run_price_script at 8:00AM and 8:00PM daily
            for t in daily_times:
                schedule.every().day.at(t).do(run_price_script)
            print(f"Scheduler started (daily at {', '.join(daily_times)}).")

        else:
            print("No valid interval mode selected. Scheduler not started.")
            scheduler_running = False
            return

        # Start the background thread for schedule
        scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        scheduler_thread.start()

        # ---- RUN IMMEDIATELY ONCE ----
        # This triggers the scraping and cleaning right away
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
    """Toggles the scheduler on/off, updates the button text & color, 
       and sets a timestamp when turned on."""
    if scheduler_running:
        stop_scheduler()
        button.config(text="Start Scheduler", bg="green")
        timestamp_label.config(text="Scheduler is OFF.")
    else:
        start_scheduler()
        button.config(text="Stop Scheduler", bg="red")
        # Update the timestamp label with the current time
        turned_on_time = time.strftime('%Y-%m-%d %H:%M:%S')
        timestamp_label.config(text=f"Scheduler turned ON at {turned_on_time}")

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
    app.geometry("480x620")

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

    # Buttons for 1 Minute, 1 Hour, 6 Hours, 12 Hours
    btn_1m = tk.Button(freq_frame, text="Every 1 Minute",
                       command=lambda: set_interval(1, "minutes", current_frequency_label))
    btn_1m.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_1h = tk.Button(freq_frame, text="Every 1 Hour",
                       command=lambda: set_interval(1, "hours", current_frequency_label))
    btn_1h.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_6h = tk.Button(freq_frame, text="Every 6 Hours",
                       command=lambda: set_interval(6, "hours", current_frequency_label))
    btn_6h.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    btn_12h = tk.Button(freq_frame, text="Every 12 Hours",
                        command=lambda: set_interval(12, "hours", current_frequency_label))
    btn_12h.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    # "8:00AM & 8:00PM" Button
    btn_8am_8pm = tk.Button(freq_frame, text="8:00 AM & 8:00 PM",
                            command=lambda: set_interval(None, "daily_8_20", current_frequency_label))
    btn_8am_8pm.pack(side="left", expand=True, fill="both", padx=2, pady=2)

    # Scheduler ON/OFF Button & Timestamp Label
    scheduler_button = tk.Button(
        app,
        text="Start Scheduler",
        bg="green",
        font=("Arial", 12),
        width=20
    )
    scheduler_button.pack(pady=10)

    timestamp_label = tk.Label(app, text="Scheduler is OFF.", font=("Arial", 10), fg="blue")
    timestamp_label.pack(pady=5)

    # Link the toggle_scheduler function to the button
    scheduler_button.config(command=lambda: toggle_scheduler(scheduler_button, timestamp_label))

    app.mainloop()

if __name__ == "__main__":
    show_gui()
