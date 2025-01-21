import pandas as pd
import sqlite3

def clean_price_data_tableau(
    input_csv='price_history.csv',
    output_excel='tableau_ready.xlsx'
):
    """
    Reads price_history.csv, cleans data in an in-memory SQLite database,
    merges date_only & time_only into a single 'timestamp' column,
    and writes a single sheet 'Master' (plus optionally 'ByTimestamp') for Tableau.
    """

    # 1. Load raw CSV
    try:
        df = pd.read_csv(input_csv)
    except FileNotFoundError:
        print(f"Error: The file '{input_csv}' was not found.")
        return
    except Exception as e:
        print(f"Error reading {input_csv}: {e}")
        return

    # 2. In-memory SQLite for cleaning
    conn = sqlite3.connect(':memory:')
    df.to_sql('price_history', conn, if_exists='replace', index=False)

    cur = conn.cursor()
    # Remove invalid rows
    cur.execute("""
        DELETE FROM price_history
        WHERE nickname IS NULL
           OR nickname = ''
           OR price IS NULL
           OR price <= 0
    """)

    # Deduplicate exact duplicates
    cur.execute("""
        DELETE FROM price_history
        WHERE rowid NOT IN (
            SELECT MIN(rowid)
            FROM price_history
            GROUP BY nickname, title, price, url, date_only, time_only
        )
    """)

    df_clean = pd.read_sql_query("SELECT * FROM price_history", conn)
    conn.close()

    # 3. Combine date_only + time_only into a single 'timestamp' column
    #    If you only have date_only, skip this step. If you only have date/time in one column, skip too.
    if 'date_only' in df_clean.columns:
        # Convert to datetime
        df_clean['date_only'] = pd.to_datetime(df_clean['date_only'], errors='coerce')

    if 'time_only' in df_clean.columns:
        # If time_only is a string like 'HH:MM:SS', convert to timedelta
        # or parse it as a time. Example approach:
        df_clean['time_only'] = pd.to_timedelta(df_clean['time_only'].astype(str), errors='coerce')
    else:
        df_clean['time_only'] = pd.to_timedelta(0)  # if missing, just 0

    # Now create a combined 'timestamp'
    # If date_only is a full date and time_only is a timedelta, we can add them:
    df_clean['timestamp'] = df_clean['date_only'] + df_clean['time_only']

    # 4. Drop the old columns if you like
    columns_to_drop = []
    if 'date_only' in df_clean.columns:
        columns_to_drop.append('date_only')
    if 'time_only' in df_clean.columns:
        columns_to_drop.append('time_only')
    df_clean.drop(columns=columns_to_drop, inplace=True)

    # 5. (Optional) Reorder or rename columns for clarity
    #    Example: rename columns to simpler ones for Tableau
    rename_map = {
        'nickname': 'Product',
        'title': 'Title',
        'price': 'Price',
        'url': 'URL',
        'timestamp': 'Timestamp'
    }
    df_clean.rename(columns=rename_map, inplace=True)

    # 6. Sort the final DataFrame by Timestamp ascending for the Master sheet
    if 'Timestamp' in df_clean.columns:
        df_clean = df_clean.sort_values(by=['Timestamp'])

    # 7. Optionally create a "ByTimestamp" version sorted descending
    df_by_ts = df_clean.copy()
    if 'Timestamp' in df_by_ts.columns:
        df_by_ts = df_by_ts.sort_values(by=['Timestamp'], ascending=False)

    # 8. Write to Excel with only numeric Price
    #    We'll skip special currency formatting so Tableau sees it as a measure
    with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
        # Master sheet
        df_clean.to_excel(writer, sheet_name='Master', index=False)

        # ByTimestamp sheet if you want it
        df_by_ts.to_excel(writer, sheet_name='ByTimestamp', index=False)

    print(f"Created '{output_excel}' for Tableau with sheets 'Master' and 'ByTimestamp'.")
    print("Contains a combined 'Timestamp' column instead of date_only/time_only, and a numeric 'Price'.")
