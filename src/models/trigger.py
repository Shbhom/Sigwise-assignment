from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
from uuid import UUID,uuid4
from enum import Enum
from datetime import datetime
from sqlalchemy import Column, JSON
from typing import List
from pydantic import BaseModel
from src.config.config import IST
from functools import partial

class TriggerType(str, Enum):
    SCHEDULED = "scheduled"
    API = "api"

class ScheduleDetails(BaseModel):
    run_at: str


class Trigger(SQLModel,table=True):
    __tablename__ = "triggers"
    id: UUID = Field(default_factory=uuid4,primary_key=True)
    type: TriggerType
    schedule_details: Optional[ScheduleDetails] = Field(default=None, sa_column=Column(JSON))
    api_payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    is_test: bool = False
    created_at: datetime
    expires_at:datetime
    event_logs: Optional[List["EventLog"]] = Relationship(back_populates="trigger")
    owner_id: UUID = Field(foreign_key="user.id")
    owner: Optional["User"] = Relationship(back_populates="triggers")


class TriggerCreate(SQLModel):
    type: TriggerType
    schedule_details: Optional[ScheduleDetails] = Field(default=None, sa_column=Column(JSON))
    api_payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    is_test: bool = False
    expires_at: datetime

class TriggerRead(SQLModel):
    id: UUID
    type: TriggerType
    schedule_details: Optional[ScheduleDetails] = None
    api_payload: Optional[dict] = None
    is_test: bool
    created_at: datetime
    expires_at: datetime
