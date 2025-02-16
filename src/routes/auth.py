from fastapi import APIRouter,Request,Depends,HTTPException,status
from fastapi.responses import RedirectResponse
import bcrypt
from src.config.config import JWT_SECRET,IST,AUTH_ALOGRITHM,ACCESS_TOKEN_EXPIRE_MINUTES
from pydantic import BaseModel,EmailStr
from typing import Optional
from datetime import timedelta, datetime
from jose import jwt,JWTError
from sqlmodel import Session,select
from db.session import get_session
from src.models.user import User,UserRead
from starlette.responses import HTMLResponse
from src.utils.jwt import TokenData, hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

@router.get('/login',response_class=HTMLResponse)
def login_form():
    html_content = """
    <html>
      <head><title>Login</title></head>
      <body>
        <h2>Login</h2>
        <form action="/auth/login" method="post">
          <input name="email" type="text" placeholder="Email" required>
          <input name="password" type="password" placeholder="Password" required>
          <button type="submit">Login</button>
        </form>
        <p>Don't have an account? <a href="/auth/register">Register</a></p>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.get('/register',response_class=HTMLResponse)
def register_form():
    html_content = """
    <html>
      <head><title>Register</title></head>
      <body>
        <h2>Register</h2>
        <form action="/auth/register" method="post">
          <input name="email" type="text" placeholder="Email" required>
          <input name="password" type="password" placeholder="Password" required>
          <button type="submit">Register</button>
        </form>
        <p>Already have an account? <a href="/auth/login">Login</a></p>
      </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@router.post('/login')
async def login_user(request:Request,session:Session=Depends(get_session)):
    form = await request.form()
    email = form.get("email")
    password = form.get("password")
    user = session.exec(select(User).where(User.email==email)).first()
    if not user or not verify_password(password,user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="incorrect email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user.email},expires_delta=access_token_expires)
    resp = RedirectResponse(url="/",status_code=302)
    resp.set_cookie(key="access_token",value=access_token,expires=access_token_expires,httponly=True,secure=True)
    return resp


@router.post('/register')
async def register_user(request:Request,session:Session=Depends(get_session)):
    form = await request.form()
    email = form.get('email')
    if session.exec(select(User).where(User.email== email)).first():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="user with this email already exists")
    password = form.get('password')
    user = User(email=email,password=hash_password(password=password))
    session.add(user)
    session.commit()
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data= {"sub":user.email},expires_delta=access_token_expires)
    resp = RedirectResponse(url="/",status_code=302)
    resp.set_cookie(key="access_token",value=access_token,httponly=True, secure=True,expires=access_token_expires)
    return resp



    

    
