import requests
from apscheduler.schedulers.blocking import BlockingScheduler


def trigger_api():
    response = requests.post("http://api:8000/create-jobs/")
    print(f"Job enqueued: {response.json()}")


# Trigger the API as soon as the scheduler starts
trigger_api()

# Trigger the API every 5 minutes post that
scheduler = BlockingScheduler()
scheduler.scheduled_job("interval", minutes=5)(trigger_api)

if __name__ == "__main__":
    scheduler.start()
