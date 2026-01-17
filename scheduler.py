import schedule
import time
import subprocess
import os

def job():
    print("Running Weekly Update Check...")
    try:
        subprocess.run(["python3", "check_updates.py"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Update check failed: {e}")

# Check environment for frequency
# Default to every Monday at 8 AM
schedule.every().monday.at("08:00").do(job)

# Also run once on startup (optional, for verification)
if os.environ.get('RUN_ON_STARTUP'):
    print("Running startup check...")
    job()

print("Scheduler started. Waiting for jobs...")
while True:
    schedule.run_pending()
    time.sleep(60)
