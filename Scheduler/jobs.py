# scheduler/jobs.py
from apscheduler.schedulers.background import BackgroundScheduler
from database.connection import get_db
from services.stage import update_current_stage


def start_scheduler():
    scheduler = BackgroundScheduler()

    # @scheduler.scheduled_job("cron", hour=0, minute=1)  # Every day at 00:01 AM
    @scheduler.scheduled_job("interval", minutes=1)
    def update_stage_job():
        print("Scheduled job running...")
        db = next(get_db())
        try:
            update_current_stage(db)
        finally:
            db.close()

    scheduler.start()
