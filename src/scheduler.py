import requests
from apscheduler.schedulers.blocking import BlockingScheduler


def trigger_api():
    response = requests.post("http://api:8000/create-jobs/")
    print(f"Job enqueued: {response.json()}")


scheduler = BlockingScheduler()
# Trigger the API every minute
scheduler.scheduled_job("interval", minutes=1)(trigger_api)

if __name__ == "__main__":
    scheduler.start()
