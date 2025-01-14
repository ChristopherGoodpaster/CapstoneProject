import tkinter as tk
from tkinter import messagebox
import json
import threading
import time
import schedule
import subprocess
import os

URLS_FILE = "product_urls.json"

# Globals for scheduling
scheduler_running = False
scheduler_thread = None

# We'll store the user-chosen interval in two parts:
interval_value = 1       # numeric value
interval_unit = "hours"  # "minutes" or "hours"

# For auto-clean logic
auto_clean_var = None

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
    Run generate_data.py, then optionally run clean_data.py 
    if 'auto_clean_var' (checkbox) is checked.
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        generate_data_path = os.path.join(script_dir, "generate_data.py")
        clean_data_path = os.path.join(script_dir, "clean_data.py")

        print(f"Running generate_data.py at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
        subprocess.run(["python", generate_data_path], check=True)
        print("Script executed successfully.\n")

        # If user checked the auto-clean box, run clean_data.py
        if auto_clean_var.get():
            print("Now running clean_data.py...")
            subprocess.run(["python", clean_data_path], check=True)
            print("Clean data script executed successfully.\n")

    except Exception as e:
        print(f"Error running script: {e}\n")

def set_interval(value, unit, current_frequency_label):
    """
    Sets the scheduling interval (value + unit).
    Updates the label so the user knows which frequency is selected.
    """
    global interval_value, interval_unit
    interval_value = value
    interval_unit = unit

    if unit == "minutes":
        current_frequency_label.config(
            text=f"Current Frequency: Every {value} Minute(s)"
        )
        print(f"Scheduler frequency set to {value} minute(s).")
    else:
        current_frequency_label.config(
            text=f"Current Frequency: Every {value} Hour(s)"
        )
        print(f"Scheduler frequency set to {value} hour(s).")

def start_scheduler():
    """
    Starts the scheduler to fetch data at the chosen interval 
    (either minutes or hours).
    """
    def run_schedule():
        while scheduler_running:
            schedule.run_pending()
            time.sleep(1)

    global scheduler_running, scheduler_thread, interval_value, interval_unit

    if not scheduler_running:
        scheduler_running = True
        schedule.clear()  # Clear old jobs to avoid duplicates

        # Schedule based on user-chosen interval
        if interval_unit == "minutes":
            schedule.every(interval_value).minutes.do(run_price_script)
            print(f"Scheduler started. Interval: {interval_value} minute(s).")
        else:
            schedule.every(interval_value).hours.do(run_price_script)
            print(f"Scheduler started. Interval: {interval_value} hour(s).")

        scheduler_thread = threading.Thread(target=run_schedule, daemon=True)
        scheduler_thread.start()

    else:
        print("Scheduler is already running.")

def stop_scheduler():
    global scheduler_running
    if scheduler_running:
        scheduler_running = False
        schedule.clear()
        print("Scheduler stopped.")

def toggle_scheduler(button):
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
    app.geometry("400x680")

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

    # Label for showing the current frequency
    current_frequency_label = tk.Label(freq_frame, text="Current Frequency: Every 1 Hour(s)", font=("Arial", 10))
    current_frequency_label.pack(pady=5)

    # Button: 1 Minute
    btn_1m = tk.Button(freq_frame, text="Every 1 Minute",
                       command=lambda: set_interval(1, "minutes", current_frequency_label))
    btn_1m.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    # Button: 1 Hour
    btn_1h = tk.Button(freq_frame, text="Every 1 Hour",
                       command=lambda: set_interval(1, "hours", current_frequency_label))
    btn_1h.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    # Button: 6 Hours
    btn_6h = tk.Button(freq_frame, text="Every 6 Hours",
                       command=lambda: set_interval(6, "hours", current_frequency_label))
    btn_6h.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    # Button: 12 Hours
    btn_12h = tk.Button(freq_frame, text="Every 12 Hours",
                        command=lambda: set_interval(12, "hours", current_frequency_label))
    btn_12h.pack(side="left", expand=True, fill="both", padx=5, pady=5)

    # Checkbox to auto-run clean_data.py
    global auto_clean_var
    auto_clean_var = tk.BooleanVar(value=False)
    auto_clean_check = tk.Checkbutton(
        app,
        text="Auto-run clean_data.py after scraping",
        variable=auto_clean_var
    )
    auto_clean_check.pack(pady=10)

    # Scheduler Start/Stop Button
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
