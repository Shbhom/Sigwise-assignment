from fastapi import FastAPI,Request,Depends,HTTPException,status
from fastapi.responses import RedirectResponse
from starlette.responses import HTMLResponse
from db.session import init_db,get_session
from sqlmodel import Session
import uvicorn
from src.routes.events import router as eventRouter
from src.routes.trigger import router as triggerRouter
from src.routes.auth import router as authRouter
from src.scheduler.background import start_background_process
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from src.utils.jwt import get_current_user
import logging

logging.basicConfig(level=logging.INFO)


app = FastAPI(
    title="Sigwise Event Trigger Platform",
    description="API documentation for the Sigwise Event Trigger Platform. Use this API to manage triggers, test events, and view event logs.",
    version="1.0.0",
    docs_url="/docs",
)

app.mount("/static", StaticFiles(directory="template"), name="static")

templates = Jinja2Templates(directory="template")

@app.on_event("startup")
async def startup_event():
    init_db()
    start_background_process()

@app.get('/ping')
async def pong():
    return {"ping":"pong"}

app.include_router(authRouter, prefix="/auth", tags=["auth"])
app.include_router(triggerRouter,prefix="/api/v1/triggers",tags=["triggers"])
app.include_router(eventRouter,prefix="/api/v1/event_logs",tags=["event_logs"])


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request,session:Session = Depends(get_session)):
    try:
        current_user = await get_current_user(request,session)
        logging.info({"current_user":current_user})
    except HTTPException:
        logging.info("User not authenticated; redirecting to login.")
        return RedirectResponse(url="/auth/login",status_code=302)
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/logout")
def logout():
    resp = RedirectResponse(url="/auth/login", status_code=302)
    resp.delete_cookie("access_token")
    return resp

if __name__ == "__main__":
    uvicorn.run("main:app",host="0.0.0.0",port=8000,reload=True)