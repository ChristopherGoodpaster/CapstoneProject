import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.dates as mdates
from tkinter import Tk, Listbox, Button, Label, MULTIPLE, messagebox

def load_data(csv_file):
    """Loads historical price data from the CSV and removes rows with NaN nicknames."""
    try:
        df = pd.read_csv(csv_file)
        df['date_only'] = pd.to_datetime(df['date_only'])

        # Check for NaN in the nickname column
        if df['nickname'].isna().any():
            print("Found rows with NaN in the 'nickname' column. Removing them...")
            df = df.dropna(subset=['nickname'])

            # Save the cleaned data back to the CSV
            df.to_csv(csv_file, index=False)
            print("Cleaned dataset saved back to the CSV.")

        return df
    except FileNotFoundError:
        messagebox.showerror("Error", f"File '{csv_file}' not found!")
        exit()

def generate_graphs(selected_products, df):
    """Generates graphs for the selected products."""
    # Filter the DataFrame based on selected products
    filtered_df = df[df['nickname'].isin(selected_products)]

    # Create a figure with a 2x2 grid layout
    fig, axes = plt.subplots(2, 2, figsize=(16, 16))  # 2 rows, 2 columns

    # Visualization 1: Line Plot for Price Trends Over Time
    axes[0, 0].set_title("Price Trends Over Time", fontsize=16)
    for product in selected_products:
        product_data = filtered_df[filtered_df['nickname'] == product].sort_values(by='date_only')
        axes[0, 0].plot(product_data['date_only'], product_data['price'], marker='o', linestyle='-', label=product)

    axes[0, 0].set_xlabel("Date", fontsize=12)
    axes[0, 0].set_ylabel("Price ($)", fontsize=12)
    axes[0, 0].tick_params(axis='x', rotation=45)
    axes[0, 0].grid(True, linestyle='--', alpha=0.7)
    axes[0, 0].xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    axes[0, 0].legend(title="Products", loc='upper left', bbox_to_anchor=(1.05, 1), fontsize=10)

    # Visualization 2: Bar Chart of Average Prices
    avg_price = filtered_df.groupby('nickname')['price'].mean().reset_index()
    sns.barplot(data=avg_price, x='nickname', y='price', palette='viridis', ax=axes[0, 1])
    axes[0, 1].set_title("Average Price per Product", fontsize=16)
    axes[0, 1].set_xlabel("Product", fontsize=12)
    axes[0, 1].set_ylabel("Average Price ($)", fontsize=12)
    axes[0, 1].tick_params(axis='x', rotation=45)

    # Visualization 3: Boxplot of Price Distribution
    sns.boxplot(data=filtered_df, x='nickname', y='price', palette='Set2', ax=axes[1, 0])
    axes[1, 0].set_title("Price Distribution per Product", fontsize=16)
    axes[1, 0].set_xlabel("Product", fontsize=12)
    axes[1, 0].set_ylabel("Price ($)", fontsize=12)
    axes[1, 0].tick_params(axis='x', rotation=45)

    # Visualization 4: Pivot Table with Price Trends
    pivot_table = pd.pivot_table(filtered_df, values='price', index='date_only', columns='nickname', aggfunc='mean')
    for column in pivot_table.columns:
        axes[1, 1].plot(pivot_table.index, pivot_table[column], marker='o', label=column)

    axes[1, 1].set_title("Pivot Table: Price Trends Over Time", fontsize=16)
    axes[1, 1].set_xlabel("Date", fontsize=12)
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
        if not selected_indices:
            messagebox.showerror("Error", "No products selected!")
            return

        selected_products = [listbox.get(i) for i in selected_indices]
        root.destroy()  # Close the GUI
        generate_graphs(selected_products, df)

    root = Tk()
    root.title("Select Products for Graphs")
    root.geometry("400x400")

    Label(root, text="Select products to include in graphs:", font=("Arial", 14)).pack(pady=10)

    listbox = Listbox(root, selectmode=MULTIPLE, font=("Arial", 12), width=50, height=15)
    for product in df['nickname'].unique():
        listbox.insert('end', product)  # Use 'end' instead of 'tk.END'
    listbox.pack(pady=10)

    Button(root, text="Generate Graphs", command=generate_graphs_callback, font=("Arial", 12)).pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    # Load the data
    csv_file = 'price_history.csv'
    data = load_data(csv_file)

    # Launch the product selection GUI
    product_selection_gui(data)
