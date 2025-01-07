# Amazon Product Price Tracker

This project tracks the prices of Amazon products and provides visualizations of price trends over time. It uses a combination of Python scripts and a Tkinter GUI to manage product URLs, collect price data, clean and organize the dataset, and generate graphs for analysis.

## Project Files

### 1. `user_interface.py`
Provides a GUI for managing the products to track.

**Features:**
- **Add Product:** Add a product URL and nickname to the tracking list.  
- **Delete Product:** Remove an existing product from the tracking list.  
- **Scheduler:** Start and stop a scheduler to automatically fetch price data at regular intervals.

**How to Use:**
1. Run `user_interface.py` using:
   ```bash
   python user_interface.py
   ```
2. Enter a nickname and the product's Amazon URL in the provided fields, then click **"Add Product"**.
3. To remove a product, select it from the list and click **"Delete Selected Product"**.
4. Use the **"Start Scheduler"** button to fetch data periodically.

---

### 2. `generate_data.py`
Fetches price data from Amazon and saves it in a local SQLite database and a CSV file for historical analysis.

**Features:**
- Fetch product titles and prices from Amazon (using BeautifulSoup for web scraping).
- Save data to a SQLite database and append new records to a CSV file (`price_history.csv`).

**How to Use:**
1. Run `generate_data.py`:
   ```bash
   python generate_data.py
   ```
2. Ensure the `product_urls.json` file contains valid product URLs.
3. The script updates the database and CSV file with the latest price data.

---

### 3. `graph.py`
Generates visualizations of the collected price data.

**Features:**
- **Graph Types:**
  - Line plot for price trends  
  - Bar chart of average prices  
  - Box plot for price distribution  
  - Pivot table for last 24-hour price trends
- **Interactive Hover:** Hover over data points to view detailed information.

**How to Use:**
1. Run `graph.py`:
   ```bash
   python graph.py
   ```
2. Select one or more products from the displayed list.
3. Click **"Generate Graphs"** to display visualizations.

---

### 4. `scheduler.py`
Automates regular data fetching by running `generate_data.py` on a schedule.

**Features:**
- Uses the `schedule` library to run `generate_data.py` every X minutes (configurable).
- Runs in a loop until manually stopped (Ctrl + C).

**How to Use:**
1. Update `scheduler.py` if needed, to point to the correct path of `generate_data.py`.
2. Run `scheduler.py`:
   ```bash
   python scheduler.py
   ```
   This starts the scheduler loop.

---

### 5. `clean_data.py`
Cleans and organizes the `price_history.csv` data. Options include:
- Removing invalid rows (e.g., missing or zero/negative prices).
- Removing duplicates using SQL logic.
- Mapping nicknames to product types.
- Sorting and reorganizing columns for presentation.
- Optionally outputting the cleaned dataset to Excel with multiple sheets (requires **xlsxwriter**).

**How to Use:**
1. Run `clean_data.py`:
   ```bash
   python clean_data.py
   ```
2. A cleaned version of the data (e.g., `cleaned_price_history.csv` or `cleaned_price_history.xlsx`) will be generated in the project folder.

---

### 6. `setup.py` (Optional)
Allows you to package the project and install dependencies via a single command.

**How to Use:**
1. In your console, navigate to the folder containing `setup.py`.
2. Run:
   ```bash
   pip install .
   ```
   This installs all required libraries listed in the `install_requires` section of `setup.py`.

---

## How to Run the Project

1. **Manage Products**  
   - Run `user_interface.py` to add product URLs, provide nicknames, and manage your tracking list.  
2. **Fetch Latest Data**  
   - Run `generate_data.py` (manually or via the `scheduler.py` script) to fetch and store the latest price data.  
3. **Clean and Organize Data**  
   - (Optional) Run `clean_data.py` to create a cleaned/organized version of your `price_history.csv`, possibly split by product type or exported to an Excel file.  
4. **Visualize Trends**  
   - Run `graph.py` to visualize the data in various plots and charts.  

---

## Dependencies

The project requires the following Python libraries:
- `pandas`
- `matplotlib`
- `seaborn`
- `mplcursors`
- `tkinter` (usually included with standard Python installations)
- `requests`
- `beautifulsoup4`
- `schedule`
- `xlsxwriter` (required for exporting to Excel files in `clean_data.py`)

### Installing Dependencies

There are two main ways to install the dependencies:

1. **Using `requirements.txt`**  
   Create or update a `requirements.txt` file with the following:
   ```txt
   pandas
   matplotlib
   seaborn
   mplcursors
   tkinter
   requests
   beautifulsoup4
   schedule
   xlsxwriter
   ```
   Then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Using `setup.py`** (Optional, if you want a package-like installation)  
   Run:
   ```bash
   pip install .
   ```
   in the directory containing `setup.py`. This will install all listed dependencies.

---

## Project Structure

```
.
|-- user_interface.py      # GUI for managing products
|-- generate_data.py       # Script to fetch and store price data
|-- graph.py               # Script to generate graphs for analysis
|-- scheduler.py           # Script to schedule repeated data fetch
|-- clean_data.py          # Script to clean and organize collected data
|-- product_urls.json      # JSON file to store product nicknames and URLs
|-- price_history.csv      # CSV file containing historical price data
|-- requirements.txt       # Dependencies for the project
|-- setup.py               # Optional packaging and dependency installation file
|-- readme.md              # (This README file)
```

---

## Notes

- Ensure valid Amazon product URLs are added to the tracker before running `generate_data.py`.
- The `generate_data.py` script uses a custom **User-Agent** header when scraping Amazon (necessary to avoid request blocks).
- The `price_history.csv` file is automatically updated with new price data after each fetch.  
- `clean_data.py` can also export to Excel (`.xlsx`) if `xlsxwriter` is installed.  
- The hover feature in `graph.py` is interactive, providing detailed information when you hover over data points.  
- If you have issues installing **tkinter** (on some Linux distros), install it via your package manager (e.g., `sudo apt-get install python3-tk`).

---

## Contact

For questions or issues, feel free to contact the project maintainer:

**Chris Goodpaster**  
[Chris.Goodpaster83@gmail.com](mailto:Chris.Goodpaster83@gmail.com)
