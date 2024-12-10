import time
import schedule
import subprocess

# Function to run your generate_data.py script
def run_price_script():
    # Replace with the actual path to your Python interpreter and script if needed
    subprocess.run(["python", "generate_data.py"], check=True)

# Schedule the job at 7:00 AM, 1:00 PM, 7:00 PM, and 1:00 AM EST every day
# This assumes your server/computer is set to EST. If not, adjust accordingly or use a fixed timezone solution.
schedule.every().day.at("09:00").do(run_price_script)
schedule.every().day.at("13:00").do(run_price_script)
schedule.every().day.at("19:00").do(run_price_script)
schedule.every().day.at("01:00").do(run_price_script)

# Keep the script running indefinitely
while True:
    schedule.run_pending()
    time.sleep(60)  # check every minute
