from dotenv import load_dotenv
from os import getenv
from datetime import datetime,timedelta,timezone

load_dotenv()


RUNNING_ENV = getenv('RUNNING_ENV')
POSTGRES_URL = getenv('POSTGRES_URL')
IST = timezone(timedelta(hours=5, minutes=30))
JWT_SECRET= getenv('JWT_SECRET',"TESTING_SECRET")
AUTH_ALOGRITHM="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
