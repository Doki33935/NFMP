from fastapi import FastAPI
from api import admin

app = FastAPI()

app.include_router(admin.router)