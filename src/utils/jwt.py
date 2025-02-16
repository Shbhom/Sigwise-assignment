from typing import Optional
from pydantic import BaseModel
import bcrypt
from datetime import timedelta,datetime
from src.config.config import IST,JWT_SECRET,AUTH_ALOGRITHM
from jose import JWTError,jwt
from fastapi import Request,Depends,HTTPException,status
from sqlmodel import Session,select
from db.session import get_session
from src.models.user import User
import logging

logging.basicConfig(level=logging.INFO)


class TokenData(BaseModel):
    email: Optional[str] = None

def hash_password(password:str)->str:
    return bcrypt.hashpw(password=password.encode(),salt=bcrypt.gensalt()).decode()

def verify_password(password:str,hashed_pass:str)->str:
    return bcrypt.checkpw(password=password.encode(),hashed_password=hashed_pass.encode())

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode = data.copy()
    expire = datetime.now(IST) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp":expire})
    encode_jwt = jwt.encode(to_encode,JWT_SECRET,algorithm=AUTH_ALOGRITHM)
    return encode_jwt

async def get_current_user(request:Request,session:Session=Depends(get_session)):
    token = request.cookies.get("access_token")
    if not token:
        logging.error("Token not found")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authenticated")
    try:
        payload = jwt.decode(token,JWT_SECRET,algorithms=[AUTH_ALOGRITHM])
        email = payload.get('sub')
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Not Authenticated")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not Authticated")
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    return user