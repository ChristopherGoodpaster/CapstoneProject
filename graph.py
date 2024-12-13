import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from tkinter import Tk, Listbox, Button, Label, MULTIPLE, messagebox
import mplcursors

def load_data(csv_file):
    """Loads historical price data from the CSV and removes rows with NaN nicknames."""
    try:
        # Load CSV
        df = pd.read_csv(csv_file)
        df['date_only'] = pd.to_datetime(df['date_only'])

        # Remove rows with NaN in the nickname column
        if df['nickname'].isna().any():
            print("Found rows with NaN in the 'nickname' column. Removing them...")
            df = df.dropna(subset=['nickname'])
            df.to_csv(csv_file, index=False)  # Save cleaned data back to the CSV
            print("Cleaned dataset saved back to the CSV.")

        return df
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{csv_file}' not found!")
        exit()
    except Exception as e:
        print(f"Error loading data: {e}")
        messagebox.showerror("Error", "Failed to load data.")
        exit()

def generate_graphs(selected_products, df):
    """Generates graphs for the selected products."""
    if selected_products:
        # Filter the DataFrame based on selected products
        filtered_df = df[df['nickname'].isin(selected_products)]
    else:
        print("No products selected. Using all data.")
        filtered_df = df

    if filtered_df.empty:
        print("No data available for the selected products.")
        return

    # Create a figure with a 2x2 grid layout
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))

    # Visualization 1: Line Plot for Price Trends Over Time
    axes[0, 0].set_title("Price Trends Over Time", fontsize=16)
    for product in filtered_df['nickname'].unique():
        product_data = filtered_df[filtered_df['nickname'] == product].sort_values(by='date_only')
        line, = axes[0, 0].plot(
            product_data['date_only'], 
            product_data['price'], 
            marker='o', 
            linestyle='-', 
            label=product
        )

        # Add hover functionality
        cursor = mplcursors.cursor(line, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"{product}\nDate: {pd.to_datetime(sel.target[0]).strftime('%Y-%m-%d')}\nPrice: ${sel.target[1]:.2f}"
        ))
        cursor.connect("remove", lambda sel: sel.annotation.set_visible(False))

    axes[0, 0].set_xlabel("Date", fontsize=12)
    axes[0, 0].set_ylabel("Price ($)", fontsize=12)
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, linestyle='--', alpha=0.7)
    axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[0, 0].legend(title="Products", loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)

    # Visualization 2: Bar Chart of Average Prices
    avg_price = filtered_df.groupby('nickname')['price'].mean().reset_index()
    bar = sns.barplot(data=avg_price, x='nickname', y='price', hue='nickname', dodge=False, palette='viridis', ax=axes[0, 1])
    axes[0, 1].set_title("Average Price per Product", fontsize=16)
    axes[0, 1].set_xlabel("Product", fontsize=12)
    axes[0, 1].set_ylabel("Average Price ($)", fontsize=12)
    axes[0, 1].tick_params(axis='x', rotation=45)

    # Add hover functionality
    cursor = mplcursors.cursor(bar.patches, hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"Product: {avg_price.iloc[int(sel.index)].nickname}\nAverage Price: ${avg_price.iloc[int(sel.index)].price:.2f}"
    ))
    cursor.connect("remove", lambda sel: sel.annotation.set_visible(False))

    # Visualization 3: Boxplot of Price Distribution
    box = sns.boxplot(data=filtered_df, x='nickname', y='price', hue='nickname', dodge=False, palette='Set2', ax=axes[1, 0])
    axes[1, 0].set_title("Price Distribution per Product", fontsize=16)
    axes[1, 0].set_xlabel("Product", fontsize=12)
    axes[1, 0].set_ylabel("Price ($)", fontsize=12)
    axes[1, 0].tick_params(axis='x', rotation=45)

    # Add hover functionality
    cursor = mplcursors.cursor(box.get_lines(), hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(
        f"Product: {filtered_df.iloc[int(sel.index)].nickname}\nPrice: ${filtered_df.iloc[int(sel.index)].price:.2f}"
    ))
    cursor.connect("remove", lambda sel: sel.annotation.set_visible(False))

    # Visualization 4: Pivot Table with Price Trends (Last 24 Hours)
    last_24_hours = filtered_df[filtered_df['date_only'] > (filtered_df['date_only'].max() - pd.Timedelta(hours=24))]
    pivot_table = pd.pivot_table(last_24_hours, values='price', index='date_only', columns='nickname', aggfunc='mean')
    for column in pivot_table.columns:
        line, = axes[1, 1].plot(pivot_table.index, pivot_table[column], marker='o', label=column)

        # Add hover functionality
        cursor = mplcursors.cursor(line, hover=True)
        cursor.connect("add", lambda sel: sel.annotation.set_text(
            f"Product: {column}\nDate: {pd.to_datetime(sel.target[0]).strftime('%Y-%m-%d %H:%M:%S')}\nPrice: ${sel.target[1]:.2f}"
        ))
        cursor.connect("remove", lambda sel: sel.annotation.set_visible(False))

    axes[1, 1].set_title("Pivot Table: Price Trends (Last 24 Hours)", fontsize=16)
    axes[1, 1].set_xlabel("Time", fontsize=12)
    axes[1, 1].set_ylabel("Average Price ($)", fontsize=12)
    axes[1, 1].tick_params(axis='x', rotation=45)
    axes[1, 1].grid(True, linestyle='--', alpha=0.7)
    axes[1, 1].legend(title="Products", loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)

    # Adjust spacing and show the graphs
    plt.tight_layout()
    plt.show()

def product_selection_gui(df):
    """GUI to select products for graph generation."""
    def generate_graphs_callback():
        selected_indices = listbox.curselection()
        selected_products = [listbox.get(i) for i in selected_indices]
        root.destroy()
        generate_graphs(selected_products, df)

    root = Tk()
    root.title("Select Products for Graphs")
    root.geometry("400x400")

    Label(root, text="Select products to include in graphs:", font=("Arial", 14)).pack(pady=10)

    listbox = Listbox(root, selectmode=MULTIPLE, font=("Arial", 12), width=50, height=15)
    for product in df['nickname'].unique():
        listbox.insert('end', product)
    listbox.pack(pady=10)

    Button(root, text="Generate Graphs", command=generate_graphs_callback, font=("Arial", 12)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    # Load the data
    csv_file = 'price_history.csv'
    data = load_data(csv_file)

    # Launch the product selection GUI
    product_selection_gui(data)
