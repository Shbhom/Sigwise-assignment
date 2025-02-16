from apscheduler.schedulers.background import BackgroundScheduler
from db.session import engine
from sqlmodel import Session,select
from datetime import datetime, timedelta
from src.models.event import EventLog,EventStatus
import logging
from src.config.config import IST

logging.basicConfig(level=logging.INFO)

scheduler = BackgroundScheduler(timezone=IST)

def archive_old_logs():
    with Session(engine) as session:
        threshold = datetime.now(IST) - timedelta(hours=2)
        events = session.exec(select(EventLog).where((EventLog.created_at < threshold) & (EventLog.status == EventStatus.ACTIVE))).all()
        for event in events:
            event.status = EventStatus.ARCHIVED
            session.add(event)
        session.commit()
        logging.info("successfully, archived logs older than 2hrs")

def cleanup_archived_logs():
    with Session(engine) as session:
        threshold = datetime.now(IST) - timedelta(hours=48)
        events = session.exec(select(EventLog).where((EventLog.created_at < threshold) & (EventLog.status == EventStatus.ARCHIVED))).all()
        for event in events:
            session.delete(event)
        session.commit()
        logging.info('successfully cleaned up the logs older than 48 hrs')

def start_background_process():
    scheduler.add_job(archive_old_logs,'interval', minutes=5)
    scheduler.add_job(cleanup_archived_logs,'interval', minutes=5)
    scheduler.start()