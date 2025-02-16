from fastapi import APIRouter, Depends, HTTPException, Request
from starlette.responses import HTMLResponse
from src.models.trigger import TriggerRead,TriggerCreate, Trigger,TriggerType
from src.models.event import EventLog,EventStatus
from src.models.user import User
from src.utils.jwt import get_current_user
from sqlmodel import Session,select
from db.session import get_session
from datetime import datetime,timezone,timedelta
from src.scheduler.scheduler import schedule_trigger_execution
from typing import List
from uuid import UUID,uuid4
from src.config.config import IST
from fastapi.templating import Jinja2Templates
from dateutil import parser
import logging

logging.basicConfig(level=logging.INFO)

router = APIRouter()

templates = Jinja2Templates(directory="template")

@router.post("/",response_model=TriggerRead,summary="Create a New Trigger", tags=["triggers"])
def create_trigger(trigger: TriggerCreate, session: Session = Depends(get_session),current_user:User = Depends(get_current_user)):
    now = datetime.now(IST)
    logging.info({"tz":now.tzinfo,"time":now.time()})

    # Validate expires_at: must be in the future relative to IST
    expires_at = datetime.fromisoformat(trigger.expires_at.isoformat())
    if expires_at.tzinfo is None:
        logging.error("no timezone info")
        expires_at = expires_at.replace(tzinfo=now.tzinfo)
    if expires_at <= now:
        logging.error("expires_at is not in future")
        raise HTTPException(status_code=400, detail="expires_at must be in the future")
    
    # For scheduled triggers, validate schedule_details includes a valid future run_at
    if trigger.type == TriggerType.SCHEDULED:
        if not trigger.schedule_details:
            raise HTTPException(status_code=400, detail="Scheduled triggers require a 'run_at' in schedule_details")
        run_at_str = trigger.schedule_details.run_at
        try:
            run_at = datetime.fromisoformat(run_at_str)
            # If run_at is naive, assume IST
            if run_at.tzinfo is None:
                run_at = run_at.replace(tzinfo=now.tzinfo)
        except ValueError:
            logging.error({"not in ISO format"})
            raise HTTPException(status_code=400, detail="Invalid ISO format for run_at")
        if run_at <= now:
            raise HTTPException(status_code=400, detail="run_at must be a future date/time")
    
    new_trigger = Trigger(
        **trigger.dict(exclude_unset=True),
        owner_id=current_user.id,
        created_at=now  
    )
    logging.info({"trigger":new_trigger})
    session.add(new_trigger)
    session.commit()
    session.refresh(new_trigger)
    
    # For scheduled triggers, either immediately log a test event or schedule future execution
    if new_trigger.type == TriggerType.SCHEDULED and new_trigger.schedule_details:
        if new_trigger.is_test:
            event = EventLog(
                id=uuid4(),
                trigger_id=new_trigger.id,
                trigger_type=new_trigger.type,
                payload=new_trigger.api_payload if new_trigger.type == TriggerType.API else new_trigger.schedule_details,
                is_manual_test=True,
                status=EventStatus.ACTIVE,
                created_at=datetime.now(IST)
            )
            session.add(event)
            session.commit()
        else:
            # Schedule the trigger to execute at the future run_at time
            schedule_trigger_execution(new_trigger.id, run_at)
    
    return new_trigger

@router.get('/',response_model=List[TriggerRead],summary="Get All Triggers", tags=["triggers"])
def get_triggers(session:Session= Depends(get_session),current_user: User = Depends(get_current_user)):
    triggers = session.exec(select(Trigger).where(Trigger.owner_id == current_user.id)).all()
    return triggers

@router.get("/triggers_html", response_class=HTMLResponse)
def get_triggers_html(request: Request, session: Session = Depends(get_session),current_user: User = Depends(get_current_user)):
    triggers = session.exec(select(Trigger).where(Trigger.owner_id == current_user.id)).all()
    return templates.TemplateResponse(
        "trigger_table.html",
        {
            "request": request,
            "triggers": triggers
        }
    )

@router.get('/{trigger_id}',response_model=TriggerRead,summary="Get Trigger by ID", tags=["triggers"])
def get_trigger(trigger_id:UUID,session:Session= Depends(get_session),current_user: User = Depends(get_current_user)):
    trigger = session.get(Trigger,trigger_id)
    if not trigger or trigger.owner_id != current_user.id:
        raise HTTPException(404, "Trigger not found")
    return trigger

@router.put("/{trigger_id}",response_model=TriggerRead,summary="Update Trigger by ID", tags=["triggers"])
def update_trigger(trigger_id:UUID, trigger_update: TriggerCreate, session: Session= Depends(get_session),current_user: User = Depends(get_current_user)):
    trigger = session.get(Trigger, trigger_id)
    if not trigger or trigger.owner_id != current_user.id:
        raise HTTPException(404, "Trigger not found")
    updated_data = trigger_update.dict(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(trigger,key, value)
    session.add(updated_data)
    session.commit()
    session.refresh(trigger)
    return trigger

@router.delete('/{trigger_id}',summary="Delete Trigger By ID", tags=["triggers"])
def delete_trigger(trigger_id:UUID,session:Session=Depends(get_session),current_user: User = Depends(get_current_user)):
    trigger = session.get(Trigger, trigger_id)
    if not trigger or trigger.owner_id != current_user.id:
        raise HTTPException(404, "Trigger not found")
    session.delete(trigger)
    session.commit()
    return {"message":"Trigger deleted successfully"}

@router.post('/{trigger_id}/test')
def test_trigger(trigger_id:UUID,session:Session= Depends(get_session),current_user: User = Depends(get_current_user)):
    trigger = session.get(Trigger,trigger_id)
    if not trigger or trigger.owner_id != current_user.id:
        raise HTTPException(404, "Trigger not found")
    event = EventLog(
        id= uuid4(),
        trigger_id=trigger.id,
        trigger_type=trigger.type,
        payload= trigger.api_payload if trigger.type == TriggerType.API else trigger.schedule_details,
        is_manual_test=True,
        status=EventStatus.ACTIVE,
        created_at=datetime.now(IST)
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return {"message":"Test Event Triggered", "event_id":event.id}

@router.post('/{trigger_id}/fire')
def fire_trigger(trigger_id:UUID,payload:dict,session:Session= Depends(get_session),current_user: User = Depends(get_current_user)):
    trigger = session.get(Trigger,trigger_id)
    if not trigger or trigger.owner_id != current_user.id:
        raise HTTPException(404, "Trigger not found")
    if trigger.type != TriggerType.API:
        raise HTTPException(400, "Not An API trigger")
    event = EventLog(
        id= uuid4(),
        trigger_id=trigger_id,
        trigger_type= trigger.type,
        payload= payload,
        is_manual_test=False,
        status= EventStatus.ACTIVE,
        created_at=datetime.now(IST)
    )
    session.add(event)
    session.commit()
    session.refresh(event)
    return {"message":"API Trigger Fired","event_id":event.id}
