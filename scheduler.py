import time
import schedule
import subprocess

def run_price_script():
    """Run the generate_data.py script."""
    try:
        print(f"Running generate_data.py at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
        subprocess.run(["python", "generate_data.py"], check=True)
        print("Script executed successfully.\n")
    except Exception as e:
        print(f"Error running script: {e}\n")

# Schedule the job to run every 1 minute, change here to set it to run longer thatn 1 minute, be aware if you run this too many times Amazon will ban you from accessing their website
schedule.every(1).minutes.do(run_price_script)

# Keep the script running indefinitely
print("Scheduler is running. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)  # Check every minute
