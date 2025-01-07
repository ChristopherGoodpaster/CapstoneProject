import pandas as pd
import sqlite3

def clean_price_data_excel(
    input_csv='price_history.csv',
    output_excel='cleaned_price_history.xlsx'
):
    """
    Reads price_history.csv, cleans the data using an in-memory SQLite database,
    then writes a Master sheet and per-product-type sheets to an Excel file.
    """

    # 1. Load the CSV into a DataFrame
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found.")
        return
    except Exception as e:
        print(f"Error reading {input_csv}: {e}")
        return

    # 2. Create an in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()

    # 3. Write the DataFrame to a temporary SQL table
    df.to_sql('price_history', conn, if_exists='replace', index=False)

    # 4. Remove invalid or incomplete rows
    cursor.execute("""
        DELETE FROM price_history
        WHERE nickname IS NULL
           OR nickname = ''
           OR price IS NULL
           OR price <= 0
    """)

    # 5. Remove exact duplicates (keep only first occurrence)
    cursor.execute("""
        DELETE FROM price_history
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM price_history
            GROUP BY nickname, title, price, url, date_only, time_only
        )
    """)

    # 6. Read the cleaned data back into a Pandas DataFrame
    df_cleaned = pd.read_sql_query("SELECT * FROM price_history", conn)
    conn.close()

    # 7. Optional: Map nicknames to product types (adjust as needed)
    product_type_map = {
        "KEYBOARD": "Electronics",
        "CLOCK":    "Home Decor",
        "LION":     "Toys",
        # Add more as needed...
    }
    df_cleaned['product_type'] = df_cleaned['nickname'].map(product_type_map).fillna("Other")

    # 8. Reorder columns (adjust as needed)
    desired_columns = [
        'product_type',
        'nickname',
        'title',
        'price',
        'url',
        'date_only',
        'time_only'
    ]
    df_cleaned = df_cleaned[[col for col in desired_columns if col in df_cleaned.columns]]

    # 9. Sort the data (adjust sort columns as you like)
    if 'date_only' in df_cleaned.columns:
        df_cleaned = df_cleaned.sort_values(by=['product_type', 'nickname', 'date_only'])

    # 10. Write data to an Excel file with multiple sheets
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        # 10a. Write a "Master" sheet with all cleaned data
        df_cleaned.to_excel(writer, sheet_name='Master', index=False)

        # 10b. For each product type, create a separate sheet
        grouped = df_cleaned.groupby('product_type')
        for product_type, group_df in grouped:
            # Excel sheet names can't exceed 31 characters and must be unique
            # So we create a safe sheet name
            safe_sheet_name = str(product_type)[:31].strip()

            # Write this subset to a new sheet
            group_df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

    print(f"Cleaned data has been saved to '{output_excel}' with multiple sheets.")

if __name__ == "__main__":
    clean_price_data_excel()
