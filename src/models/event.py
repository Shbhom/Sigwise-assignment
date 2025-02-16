from typing import Optional
from .trigger import Trigger, TriggerType
from uuid import UUID, uuid4
from enum import Enum
from datetime import datetime
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index, Column, JSON


class EventStatus(str,Enum):
    ACTIVE= "active"
    ARCHIVED = "archived"

class EventLog(SQLModel,table=True):
    __tablename__ = "event_logs"
    id: UUID = Field(default_factory=uuid4,primary_key=True)
    trigger_id: UUID = Field(foreign_key="triggers.id",nullable=False)
    trigger_type: TriggerType
    payload: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    is_manual_test: bool = Field(default=False)
    status: EventStatus = Field(default=EventStatus.ACTIVE)
    created_at: datetime = Field(default_factory=datetime.now,nullable=False)
    trigger: Optional[Trigger] = Relationship(back_populates="event_logs")

Index("ix_event_logs_created_at",EventLog.created_at)
Index("ix_event_logs_status",EventLog.status)