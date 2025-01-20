import tkinter as tk
from tkinter import Toplevel, messagebox
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import mplcursors
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import seaborn as sns

###############################################################################
# 1. LOADING THE CSV DATA
###############################################################################
def load_data(csv_file='price_history.csv'):
    """
    Loads a CSV containing columns like: nickname, price, date_only, ...
    Returns a DataFrame with date_only as datetime.
    """
    try:
        df = pd.read_csv(csv_file)
        df['date_only'] = pd.to_datetime(df['date_only'], errors='coerce')
        df.dropna(subset=['nickname', 'price', 'date_only'], inplace=True)
        return df
    except Exception as e:
        print("Error loading data:", e)
        return pd.DataFrame()

###############################################################################
# 2. FIGURE CREATION FUNCTIONS
###############################################################################
def create_line_figure(filtered_df, title="Price Over Time"):
    """
    A line chart (price vs. date) for the entire date range in filtered_df.
    Each product is a separate line. Hover tooltips vanish on mouseout.
    """
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Date", fontsize=10)
    ax.set_ylabel("Price ($)", fontsize=10)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

    for product in filtered_df['nickname'].unique():
        product_data = filtered_df[filtered_df['nickname'] == product].sort_values(by='date_only')
        line, = ax.plot(product_data['date_only'], product_data['price'],
                        marker='o', linestyle='-', label=product)
        # Use mplcursors for hover
        cursor = mplcursors.cursor(line, hover=True)

        def on_add(sel, prod=product):
            sel.annotation.set_text(
                f"{prod}\n"
                f"Date: {pd.to_datetime(sel.target[0]).strftime('%Y-%m-%d')}\n"
                f"Price: ${sel.target[1]:.2f}"
            )
            # Ensure tooltip disappears when mouse moves away
            sel.annotation.set_sticky(False)

        cursor.connect("add", on_add)
        cursor.connect("remove", lambda sel: sel.annotation.set_visible(False))

    ax.legend(title="Products", loc='best', fontsize=8)
    fig.tight_layout()
    return fig

def create_48h_line_figure(filtered_df):
    """
    A line chart focusing on the last 48 hours of data (price vs date/time).
    """
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title("Price Over Last 48 Hours", fontsize=12)
    ax.set_xlabel("Date/Time", fontsize=10)
    ax.set_ylabel("Price ($)", fontsize=10)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))

    if filtered_df.empty:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center',
                transform=ax.transAxes, fontsize=12)
        return fig

    latest_date = filtered_df['date_only'].max()
    cutoff = latest_date - pd.Timedelta(hours=48)
    recent_data = filtered_df[filtered_df['date_only'] >= cutoff].copy()

    if recent_data.empty:
        ax.text(0.5, 0.5, "No data in the last 48 hours",
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        return fig

    for product in recent_data['nickname'].unique():
        product_data = recent_data[recent_data['nickname'] == product].sort_values(by='date_only')
        line, = ax.plot(product_data['date_only'], product_data['price'],
                        marker='o', linestyle='-', label=product)
        cursor = mplcursors.cursor(line, hover=True)

        def on_add(sel, prod=product):
            sel.annotation.set_text(
                f"{prod}\n"
                f"Date: {pd.to_datetime(sel.target[0]).strftime('%m-%d %H:%M')}\n"
                f"Price: ${sel.target[1]:.2f}"
            )
            sel.annotation.set_sticky(False)

        cursor.connect("add", on_add)
        cursor.connect("remove", lambda sel: sel.annotation.set_visible(False))

    ax.legend(title="Products", loc='best', fontsize=8)
    fig.tight_layout()
    return fig

def create_48h_bar_figure(filtered_df):
    """
    A bar chart showing the price change in the last 48 hours:
      price_diff = last_price - first_price
    If no data, display a message.
    """
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.set_title("Price Changes (Last 48 Hours)", fontsize=12)
    ax.set_xlabel("Product", fontsize=10)
    ax.set_ylabel("Price Change ($)", fontsize=10)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, linestyle='--', alpha=0.7)

    if filtered_df.empty:
        ax.text(0.5, 0.5, "No data available", ha='center', va='center',
                transform=ax.transAxes, fontsize=12)
        return fig

    latest_date = filtered_df['date_only'].max()
    cutoff = latest_date - pd.Timedelta(hours=48)
    recent_df = filtered_df[filtered_df['date_only'] >= cutoff].copy()
    if recent_df.empty:
        ax.text(0.5, 0.5, "No data in the last 48 hours",
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        return fig

    # Sort by date to ensure first=earliest, last=latest in the 48h
    recent_df.sort_values('date_only', inplace=True)

    # Group by product, get first & last price
    change_df = recent_df.groupby('nickname').agg(
        first_price=('price', 'first'),
        last_price=('price', 'last')
    )
    change_df['price_diff'] = change_df['last_price'] - change_df['first_price']
    change_df.reset_index(inplace=True)

    if change_df.empty:
        ax.text(0.5, 0.5, "No data in the last 48 hours",
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        return fig

    # Bar chart
    sns.barplot(data=change_df, x='nickname', y='price_diff',
                palette='rocket', ax=ax)
    for i, row in change_df.iterrows():
        diff_val = row['price_diff']
        ax.text(i, diff_val, f"{diff_val:+.2f}",
                ha='center',
                va='bottom' if diff_val >= 0 else 'top',
                fontsize=8)

    fig.tight_layout()
    return fig

###############################################################################
# 3. SHOWING THE GRAPHS WINDOW
###############################################################################
def show_graphs_window(parent, selected_products, df):
    """
    Creates a Toplevel with 3 charts:
      1) Historical line chart
      2) 48h line chart
      3) 48h bar chart
    Also has 'Close Program' button to end entire app.
    """
    global graph_win
    graph_win = Toplevel(parent)
    graph_win.title("Graphs Window")
    graph_win.geometry("1000x800")

    # Filter
    if selected_products:
        filtered_df = df[df['nickname'].isin(selected_products)]
    else:
        filtered_df = df

    if filtered_df.empty:
        messagebox.showinfo("No Data", "No data available for the selected product(s).")
        return

    # --- Top Frame: historical line chart ---
    frame_top = tk.Frame(graph_win)
    frame_top.pack(side="top", fill="both", expand=True)
    fig_hist = create_line_figure(filtered_df, title="Price Over Time (Full History)")
    canvas_hist = FigureCanvasTkAgg(fig_hist, master=frame_top)
    canvas_hist.get_tk_widget().pack(side="left", fill="both", expand=True)

    # --- Middle Frame: 48h line chart ---
    frame_middle = tk.Frame(graph_win)
    frame_middle.pack(side="top", fill="both", expand=True)
    fig_48h = create_48h_line_figure(filtered_df)
    canvas_48h = FigureCanvasTkAgg(fig_48h, master=frame_middle)
    canvas_48h.get_tk_widget().pack(side="left", fill="both", expand=True)

    # --- Bottom Frame: 48h bar chart ---
    frame_bottom = tk.Frame(graph_win)
    frame_bottom.pack(side="top", fill="both", expand=True)
    fig_bar = create_48h_bar_figure(filtered_df)
    canvas_bar = FigureCanvasTkAgg(fig_bar, master=frame_bottom)
    canvas_bar.get_tk_widget().pack(side="left", fill="both", expand=True)

    def close_entire_program():
        """Completely end both windows."""
        parent.quit()
        parent.destroy()
        graph_win.destroy()

    close_btn = tk.Button(graph_win, text="Close Program", bg="red", fg="white",
                          font=("Arial", 12), command=close_entire_program)
    close_btn.pack(pady=10)

###############################################################################
# 4. MAIN GUI
###############################################################################
graph_win = None

def main_gui():
    root = tk.Tk()
    root.title("Select Products")
    root.geometry("400x500")

    df = load_data('price_history.csv')
    product_list = df['nickname'].unique() if not df.empty else []

    tk.Label(root, text="Select Product(s):", font=("Arial", 14)).pack(pady=10)

    listbox = tk.Listbox(root, selectmode=tk.MULTIPLE, width=30, height=10)
    for p in product_list:
        listbox.insert(tk.END, p)
    listbox.pack(pady=5)

    def on_generate_graphs():
        global graph_win
        if graph_win and tk.Toplevel.winfo_exists(graph_win):
            messagebox.showinfo("Already Open", "Graphs window is already open.")
            return

        sel_indices = listbox.curselection()
        selected = [listbox.get(i) for i in sel_indices]
        show_graphs_window(root, selected, df)

    gen_btn = tk.Button(root, text="Generate Graphs", font=("Arial", 12),
                        command=on_generate_graphs)
    gen_btn.pack(pady=10)

    def close_graph_window():
        """Close only the graphs window if open (without ending entire program)."""
        global graph_win
        if graph_win and tk.Toplevel.winfo_exists(graph_win):
            graph_win.destroy()
            graph_win = None
        else:
            messagebox.showinfo("No Graph Window", "No graphs window is open.")

    close_graph_btn = tk.Button(root, text="Close Graph Program", font=("Arial", 12),
                                bg="lightcoral", command=close_graph_window)
    close_graph_btn.pack(pady=5)

    root.mainloop()

if __name__ == "__main__":
    main_gui()
