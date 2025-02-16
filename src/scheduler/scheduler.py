# scheduler/scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from db.session import engine
from sqlmodel import Session
from src.models.event import EventLog, EventStatus
from src.models.trigger import Trigger
from uuid import uuid4
from src.config.config import IST

scheduler = BackgroundScheduler(timezone=IST)

def schedule_trigger_execution(trigger_id, run_at: datetime):
    scheduler.add_job(func=execute_scheduled_trigger, trigger="date", run_date=run_at, args=[trigger_id])
    if not scheduler.running:
        scheduler.start()

def execute_scheduled_trigger(trigger_id):
    with Session(engine) as session:
        trigger = session.get(Trigger, trigger_id)
        if not trigger:
            print(f"Trigger {trigger_id} not found.")
            return
        event = EventLog(
            id=uuid4(),
            trigger_id=trigger.id,
            trigger_type=trigger.type,
            payload=trigger.schedule_details,
            is_manual_test=False,
            status=EventStatus.ACTIVE,
            created_at=datetime.now(IST)
        )
        session.add(event)
        session.commit()
        print(f"Executed scheduled trigger {trigger_id} at {datetime.now(IST)}")
