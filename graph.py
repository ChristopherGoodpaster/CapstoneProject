import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from tkinter import Tk, Listbox, Button, Label, MULTIPLE, messagebox, Frame
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import mplcursors

def load_data(csv_file='price_history.csv'):
    """Loads historical price data from the CSV and removes rows with NaN nicknames."""
    try:
        df = pd.read_csv(csv_file)
        df['date_only'] = pd.to_datetime(df['date_only'], errors='coerce')
        if df['nickname'].isna().any():
            print("Found rows with NaN in 'nickname'. Removing them...")
            df = df.dropna(subset=['nickname'])
            df.to_csv(csv_file, index=False)
            print("Cleaned dataset saved back to CSV.")
        return df
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{csv_file}' not found!")
        exit()
    except Exception as e:
        print(f"Error loading data: {e}")
        messagebox.showerror("Error", "Failed to load data.")
        exit()

def create_pages(filtered_df):
    """
    Returns a list of Matplotlib Figure objects (pages), each with 2 graphs (2 subplots).
    We'll produce 3 pages (6 total graphs) like the earlier examples:
       Page 1: (Line Plot), (Bar Chart)
       Page 2: (Box Plot), (Pivot/Last 24h)
       Page 3: (Histogram), (KDE Plot)
    """
    figures = []

    # ----------------- PAGE 1: LINE PLOT, BAR CHART ------------------
    fig1, axes1 = plt.subplots(1, 2, figsize=(12, 5))

    # 1) Line Plot: Price Over Time
    ax_line = axes1[0]
    ax_line.set_title("Price Trends Over Time", fontsize=12)
    for product in filtered_df['nickname'].unique():
        product_data = filtered_df[filtered_df['nickname'] == product].sort_values(by='date_only')
        line, = ax_line.plot(product_data['date_only'], product_data['price'], marker='o', linestyle='-', label=product)
        # Optional hover
        cursor_line = mplcursors.cursor(line, hover=True)
        cursor_line.connect("add", lambda sel, p=product: sel.annotation.set_text(
            f"{p}\nDate: {pd.to_datetime(sel.target[0]).strftime('%Y-%m-%d')}\nPrice: ${sel.target[1]:.2f}"
        ))

    ax_line.set_xlabel("Date", fontsize=10)
    ax_line.set_ylabel("Price ($)", fontsize=10)
    ax_line.tick_params(axis='x', rotation=45)
    ax_line.grid(True, linestyle='--', alpha=0.7)
    ax_line.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax_line.legend(title="Products", fontsize=8)

    # 2) Bar Chart: Average Price per Product
    ax_bar = axes1[1]
    ax_bar.set_title("Average Price per Product", fontsize=12)
    avg_price = filtered_df.groupby('nickname')['price'].mean().reset_index()
    bar = sns.barplot(data=avg_price, x='nickname', y='price', hue='nickname', dodge=False, palette='viridis', ax=ax_bar)
    ax_bar.set_xlabel("Product", fontsize=10)
    ax_bar.set_ylabel("Avg. Price ($)", fontsize=10)
    ax_bar.tick_params(axis='x', rotation=45)
    legend_bar = ax_bar.get_legend()
    if legend_bar:
        legend_bar.remove()
    # Hover for bar patches
    cursor_bar = mplcursors.cursor(bar.patches, hover=True)
    cursor_bar.connect("add", lambda sel: sel.annotation.set_text(
        f"Product: {avg_price.iloc[int(sel.index)].nickname}\nAvg Price: ${avg_price.iloc[int(sel.index)].price:.2f}"
    ))

    fig1.tight_layout()
    figures.append(fig1)

    # ----------------- PAGE 2: BOX PLOT, PIVOT (LAST 24H) ------------------
    fig2, axes2 = plt.subplots(1, 2, figsize=(12, 5))

    # 3) Box Plot
    ax_box = axes2[0]
    ax_box.set_title("Price Distribution per Product", fontsize=12)
    box = sns.boxplot(data=filtered_df, x='nickname', y='price', hue='nickname', dodge=False, palette='Set2', ax=ax_box)
    ax_box.set_xlabel("Product", fontsize=10)
    ax_box.set_ylabel("Price ($)", fontsize=10)
    ax_box.tick_params(axis='x', rotation=45)
    legend_box = ax_box.get_legend()
    if legend_box:
        legend_box.remove()

    # 4) Pivot Table: Last 24 Hours
    ax_pivot = axes2[1]
    ax_pivot.set_title("Price Trends (Last 24h)", fontsize=12)
    ax_pivot.set_xlabel("Time", fontsize=10)
    ax_pivot.set_ylabel("Avg. Price ($)", fontsize=10)
    ax_pivot.grid(True, linestyle='--', alpha=0.7)

    last_24 = filtered_df[filtered_df['date_only'] > (filtered_df['date_only'].max() - pd.Timedelta(hours=24))]
    pivot_table = pd.pivot_table(last_24, values='price', index='date_only', columns='nickname', aggfunc='mean')
    if not pivot_table.empty:
        for col in pivot_table.columns:
            linep, = ax_pivot.plot(pivot_table.index, pivot_table[col], marker='o', label=col)
            cursor_pivot = mplcursors.cursor(linep, hover=True)
            cursor_pivot.connect("add", lambda sel, c=col: sel.annotation.set_text(
                f"Product: {c}\nDate: {pd.to_datetime(sel.target[0]).strftime('%Y-%m-%d %H:%M:%S')}\nPrice: ${sel.target[1]:.2f}"
            ))
        ax_pivot.legend(title="Products", fontsize=8)
        ax_pivot.tick_params(axis='x', rotation=45)
    else:
        ax_pivot.text(0.5, 0.5, "No data in last 24h", ha='center', va='center')

    fig2.tight_layout()
    figures.append(fig2)

    # ----------------- PAGE 3: HISTOGRAM, KDE ------------------
    fig3, axes3 = plt.subplots(1, 2, figsize=(12, 5))

    # 5) Histogram
    ax_hist = axes3[0]
    ax_hist.set_title("Histogram of Price Distributions", fontsize=12)
    sns.histplot(data=filtered_df, x='price', hue='nickname', multiple='stack', palette='rocket', alpha=0.7, ax=ax_hist)
    ax_hist.set_xlabel("Price ($)", fontsize=10)
    ax_hist.set_ylabel("Count", fontsize=10)
    ax_hist.tick_params(axis='x', rotation=45)

    # 6) KDE Plot
    ax_kde = axes3[1]
    ax_kde.set_title("KDE of Price Distributions", fontsize=12)
    sns.kdeplot(data=filtered_df, x='price', hue='nickname', fill=True, common_norm=False, alpha=0.4, palette='crest', ax=ax_kde)
    ax_kde.set_xlabel("Price ($)", fontsize=10)
    ax_kde.set_ylabel("Density", fontsize=10)
    ax_kde.tick_params(axis='x', rotation=45)

    fig3.tight_layout()
    figures.append(fig3)

    return figures

def display_paginated_figures(figures, parent_window):
    """
    Displays the Figures one at a time in a Frame within the parent_window.
    Provides Next/Prev buttons to navigate pages, plus a close function.
    """
    current_index = 0

    # A frame to hold the canvas
    canvas_frame = Frame(parent_window)
    canvas_frame.pack(side="top", fill="both", expand=True)

    page_label = Label(parent_window, text="", font=("Arial", 12))
    page_label.pack(side="bottom", pady=5)

    def show_figure(i):
        nonlocal current_index
        current_index = i

        # Clear any old canvas in canvas_frame
        for widget in canvas_frame.winfo_children():
            widget.destroy()

        fig = figures[i]

        # Embed figure in Tk
        canvas = FigureCanvasTkAgg(fig, master=canvas_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(side="top", fill="both", expand=True)

        page_label.config(text=f"Page {i+1} of {len(figures)}")

    def next_page():
        if current_index < len(figures) - 1:
            show_figure(current_index + 1)

    def prev_page():
        if current_index > 0:
            show_figure(current_index - 1)

    # Navigation Buttons
    nav_frame = Frame(parent_window)
    nav_frame.pack(side="bottom")

    btn_prev = Button(nav_frame, text="<< Prev", command=prev_page)
    btn_prev.pack(side="left", padx=5)

    btn_next = Button(nav_frame, text="Next >>", command=next_page)
    btn_next.pack(side="left", padx=5)

    # Initially show the first page
    show_figure(0)

def generate_graphs(selected_products, df, parent_window):
    """Generate the 2-per-page figures and show them with Next/Prev navigation."""
    if selected_products:
        filtered_df = df[df['nickname'].isin(selected_products)]
    else:
        print("No products selected. Using all data.")
        filtered_df = df

    if filtered_df.empty:
        print("No data available for the selected products.")
        messagebox.showwarning("No Data", "No data available for the selected products.")
        return

    figures = create_pages(filtered_df)
    display_paginated_figures(figures, parent_window)

def product_gui():
    """
    Main GUI window with:
      - A listbox of products
      - A "Generate Graphs" button
      - A "Close Program" button
    """
    root = Tk()
    root.title("Product Graph Viewer")
    root.geometry("600x500")

    df = load_data('price_history.csv')

    Label(root, text="Select Products for Graphs:", font=("Arial", 14)).pack(pady=10)

    listbox = Listbox(root, selectmode=MULTIPLE, font=("Arial", 12), width=40, height=10)
    for product in df['nickname'].unique():
        listbox.insert('end', product)
    listbox.pack(pady=10)

    def on_generate_graphs():
        selected_indices = listbox.curselection()
        selected_products = [listbox.get(i) for i in selected_indices]
        generate_graphs(selected_products, df, root)

    generate_button = Button(root, text="Generate Graphs", font=("Arial", 12), command=on_generate_graphs)
    generate_button.pack(pady=5)

    def close_program():
        # Destroy the root window, ending the script
        root.quit()
        root.destroy()

    close_button = Button(root, text="Close Program", font=("Arial", 12), bg="red", fg="white", command=close_program)
    close_button.pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    product_gui()
