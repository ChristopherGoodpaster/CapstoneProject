import pandas as pd
import sqlite3

def clean_price_data_excel(
    input_csv='price_history.csv',
    output_excel='cleaned_price_history.xlsx'
):
    """
    Reads price_history.csv, cleans the data using an in-memory SQLite database,
    then writes multiple sheets to an Excel file:
      1. 'Master' sheet: All cleaned data.
      2. One sheet per product type.
      3. 'ByTimestamp' sheet: Data sorted so the most recent timestamps appear first.
    The 'price' column is formatted as currency ($).
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

    # 6. Pull the cleaned data back into a Pandas DataFrame
    df_cleaned = pd.read_sql_query("SELECT * FROM price_history", conn)
    conn.close()

    # 7. Map nicknames to product types (adjust as needed)
    product_type_map = {
        "KEYBOARD":  "Electronics",
        "CLOCK":     "Home Decor",
        "LION":      "Toys",
        "RAM":       "Electronics",
        "CORSAIR":   "Electronics",
        "ROHIOUE":   "Home Decor",
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

    # 9. Sort the main DataFrame (for the Master sheet)
    if 'date_only' in df_cleaned.columns:
        df_cleaned = df_cleaned.sort_values(by=['product_type', 'nickname', 'date_only'])

    # 9b. Create a separate copy for the "ByTimestamp" sheet.
    #     Sort descending by date_only, then time_only (if present),
    #     so the most recent entries appear at the top.
    df_by_timestamp = df_cleaned.copy()
    if 'date_only' in df_by_timestamp.columns:
        # If time_only doesn't exist, we just sort by date_only descending
        sort_cols = ['date_only']
        if 'time_only' in df_by_timestamp.columns:
            sort_cols.append('time_only')
        df_by_timestamp = df_by_timestamp.sort_values(by=sort_cols, ascending=False)

    # 10. Write data to an Excel file with multiple sheets, applying currency format to the 'price' column
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        # 10a. Write a "Master" sheet with all cleaned data
        df_cleaned.to_excel(writer, sheet_name='Master', index=False)

        # Access the workbook and the "Master" worksheet
        workbook = writer.book
        worksheet_master = writer.sheets['Master']

        # Create a currency format ($#,##0.00)
        price_format = workbook.add_format({'num_format': '$#,##0.00'})

        # The 'price' column is index 3 in the desired_columns
        worksheet_master.set_column(3, 3, 12, price_format)

        # 10b. For each product type, create a separate sheet
        grouped = df_cleaned.groupby('product_type')
        for product_type, group_df in grouped:
            safe_sheet_name = str(product_type)[:31].strip()
            group_df.to_excel(writer, sheet_name=safe_sheet_name, index=False)

            worksheet_pt = writer.sheets[safe_sheet_name]
            worksheet_pt.set_column(3, 3, 12, price_format)

        # 10c. Create a "ByTimestamp" sheet that shows data by descending timestamps
        #      (the most recent entries at the top).
        df_by_timestamp.to_excel(writer, sheet_name='ByTimestamp', index=False)

        worksheet_time = writer.sheets['ByTimestamp']
        worksheet_time.set_column(3, 3, 12, price_format)

    print(f"Cleaned data has been saved to '{output_excel}' with multiple sheets:")
    print(" - Master (sorted by product_type, nickname, date_only)")
    print(" - Sheets for each product_type")
    print(" - ByTimestamp (most recent first)")

if __name__ == "__main__":
    clean_price_data_excel()
