from sqlmodel import SQLModel, create_engine, Session
from src.config.config import POSTGRES_URL
from src.config.config import RUNNING_ENV

if RUNNING_ENV == "PROD":
    engine = create_engine(POSTGRES_URL)
elif RUNNING_ENV == "DEV":
    engine = create_engine(POSTGRES_URL, echo=True)

def init_db():
    from src.models import trigger
    from src.models import event
    from src.models import user
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine,expire_on_commit=False) as session:
        yield session