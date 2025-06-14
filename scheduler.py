import time
import schedule
import configparser
from tools.tools import generate_summary, send_email

# Load configuration
config = configparser.ConfigParser()
config.read("config.ini")
domain = config["settings"]["domain"]

def job():
    """
    Fetches a unified news summary for the configured domain,
    then emails it out with an appropriate subject line.
    """
    try:
        summary_text = generate_summary(domain)
        timestamp = time.strftime("%Y-%m-%d %H:%M")
        subject = f"News Summary for {domain} on {timestamp}"
        send_email(subject, summary_text)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] Successfully sent summary email for {domain}.")
    except Exception as e:
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] ERROR in job(): {e}")

# Schedule the job at 08:00 and 16:00 each day
schedule.every().day.at("08:00").do(job)
schedule.every().day.at("16:00").do(job)

if __name__ == "__main__":
    print("Scheduler started. Will send news summary at 8 am / 4 pm daily.")
    while True:
        schedule.run_pending()
        time.sleep(60)
