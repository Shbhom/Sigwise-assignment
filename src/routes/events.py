from fastapi import APIRouter,Depends,Request
from typing import List
from src.models.event import EventLog
from sqlmodel import Session,select
from db.session import get_session
from datetime import datetime,timedelta
from src.config.config import IST
from fastapi.templating import Jinja2Templates
from starlette.responses import HTMLResponse
from src.utils.jwt import get_current_user
from src.models.user import User
from src.models.trigger import Trigger

router = APIRouter()
templates = Jinja2Templates(directory="template")

@router.get('/',response_model=List[EventLog])
def get_logs(status:str="active",session:Session=Depends(get_session),current_user:User=Depends(get_current_user)):
    match status:
        case "active":
            threshold = datetime.now(IST) - timedelta(hours=2)
            #query = select(EventLog).where(EventLog.created_at >= threshold)
            query=(
            select(EventLog)
            .join(Trigger, EventLog.trigger_id == Trigger.id)
            .where(Trigger.owner_id == current_user.id, EventLog.created_at >= threshold)
        )
        case "archived":
            threshold = datetime.now(IST) - timedelta(hours=2)
            #query = select(EventLog).where(EventLog.created_at >= threshold)
            query = (
            select(EventLog)
            .join(Trigger, EventLog.trigger_id == Trigger.id)
            .where(Trigger.owner_id == current_user.id, EventLog.created_at < threshold)
        )
        case _:
            #query = select(EventLog)
            query = (
            select(EventLog)
            .join(Trigger, EventLog.trigger_id == Trigger.id)
            .where(Trigger.owner_id == current_user.id)
            )
    events = session.exec(query).all()
    return events

@router.get('/aggregated')
def get_aggregated_logs(session:Session= Depends(get_session), current_user = Depends(get_current_user)):
    threshold = datetime.now(IST) - timedelta(hours=48)
    #events = session.exec(select(EventLog).where(EventLog.created_at>=threshold)).all()
    query = (
        select(EventLog)
        .join(Trigger, EventLog.trigger_id == Trigger.id)
        .where(Trigger.owner_id == current_user.id, EventLog.created_at >= threshold)
    )
    events= session.exec(query).all()
    aggregated = {}
    for event in events:
        key = str(event.trigger_id)
        aggregated[key]= aggregated.get(key,0)+1
    return aggregated

@router.get("/event_logs_html", response_class=HTMLResponse)
def get_event_logs_html(
    request: Request,
    status: str = "active",
    session: Session = Depends(get_session)
):
    # Query events based on status
    now = datetime.now()
    if status == "active":
        threshold = now - timedelta(hours=2)
        query = select(EventLog).where(EventLog.created_at >= threshold)
    elif status == "archived":
        threshold = now - timedelta(hours=2)
        query = select(EventLog).where(EventLog.created_at < threshold)
    else:
        query = select(EventLog)
    events = session.exec(query).all()

    return templates.TemplateResponse(
        "event_table.html",
        {"request": request, "events": events}
    )
