from fastapi import FastAPI
from api import admin
from api import auth


app = FastAPI()

app.include_router(admin.router)

app.include_router(auth.router)