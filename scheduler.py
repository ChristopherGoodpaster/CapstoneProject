import time
import schedule
import subprocess

def run_price_script():
    """Run generate_data.py using its absolute path."""
    try:
        # Print the current time so you know when it ran
        print(f"Running generate_data.py at {time.strftime('%Y-%m-%d %H:%M:%S')}...")
        
        # Update this path to point exactly to your generate_data.py
        subprocess.run([
            "python",
            r"C:\Users\Chris\Documents\code_u\Capstone\CapstoneProject\CapstoneProject\generate_data.py"
        ], check=True)
        
        print("Script executed successfully.\n")
    except Exception as e:
        print(f"Error running script: {e}\n")

# Schedule it to run every 1 minute
schedule.every(1).minutes.do(run_price_script)

print("Scheduler is running. Press Ctrl+C to stop.")

# Keep the scheduler running indefinitely
while True:
    schedule.run_pending()
    time.sleep(60)
