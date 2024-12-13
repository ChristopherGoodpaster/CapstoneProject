# Amazon Product Price Tracker

This project tracks the prices of Amazon products and provides visualizations of price trends over time. It uses a combination of Python scripts and a Tkinter GUI to manage product URLs, collect price data, and generate graphs for analysis.

## Project Files

### 1. `user_interface.py`
The `user_interface.py` script provides a GUI for managing the products to track.

#### Features:
- **Add Product:** Add a product URL and nickname to the tracking list.
- **Delete Product:** Remove an existing product from the tracking list.
- **Scheduler:** Start and stop a scheduler to automatically fetch price data at regular intervals.

#### How to Use:
1. Run `user_interface.py` using `python user_interface.py`.
2. Enter a nickname and the product's Amazon URL in the provided fields and click "Add Product."
3. To remove a product, select it from the list and click "Delete Selected Product."
4. Use the "Start Scheduler" button to fetch data periodically.

### 2. `generate_data.py`
The `generate_data.py` script fetches price data from Amazon and saves it in a local SQLite database and a CSV file for historical analysis.

#### Features:
- Fetch product titles and prices from Amazon.
- Save data to a SQLite database and append new records to a CSV file (`price_history.csv`).

#### How to Use:
1. Run `generate_data.py` using `python generate_data.py`.
2. Ensure the `product_urls.json` file contains valid product URLs.
3. The script updates the database and CSV file with the latest price data.

### 3. `graph.py`
The `graph.py` script generates visualizations of the collected price data.

#### Features:
- **Graph Types:**
  - Line plot for price trends.
  - Bar chart of average prices.
  - Box plot for price distribution.
  - Pivot table for last 24-hour price trends.
- **Interactive Hover:** Hover over data points to view detailed information.

#### How to Use:
1. Run `graph.py` using `python graph.py`.
2. Select one or more products from the displayed list.
3. Click "Generate Graphs" to display visualizations.

## How to Run the Project
1. Start by running `user_interface.py` to add product URLs and manage your tracking list.
2. Run `generate_data.py` periodically to fetch and save the latest price data.
3. Use `graph.py` to visualize the data and analyze price trends.

## Dependencies

The project requires the following Python libraries:
- pandas
- matplotlib
- seaborn
- mplcursors
- tkinter
- requests
- beautifulsoup4

### Installing Dependencies
Create a `requirements.txt` file with the following content:

```
pandas
matplotlib
seaborn
mplcursors
tkinter
requests
beautifulsoup4
```

Run the following command to install all required libraries:

```bash
pip install -r requirements.txt
```

## Project Structure
```
.
|-- user_interface.py  # GUI for managing products
|-- generate_data.py   # Script to fetch and store price data
|-- graph.py           # Script to generate graphs for analysis
|-- product_urls.json  # JSON file to store product nicknames and URLs
|-- price_history.csv  # CSV file containing historical price data
|-- requirements.txt   # Dependencies for the project
```

## Notes
- Ensure valid Amazon product URLs are added to the tracker.
- The `generate_data.py` script requires a user-agent header to scrape Amazon pages.
- The `price_history.csv` file is automatically updated with new price data after each fetch.
- The hover feature in `graph.py` is interactive and provides detailed information on data points.

For questions or issues, feel free to contact the project maintainer.

Chris Goodpaster
Chris.Goodpaster83@gmail.com
