from sqlmodel import SQLModel,Field,Relationship
from uuid import UUID,uuid4
from pydantic import EmailStr
from typing import List
from src.models.trigger import Trigger

class User(SQLModel,table=True):
    __tablename__="user"
    id: UUID = Field(primary_key=True,default_factory=uuid4)
    email:str = Field(index=True,unique=True)
    password:str
    triggers:List[Trigger] = Relationship(back_populates="owner")

class UserCreate(SQLModel):
    email:EmailStr
    password:str = Field(min_length=8,max_length=10)

class UserRead(SQLModel):
    id:UUID
    email:str
