from fastapi import FastAPI
from api import admin, auth, users


app = FastAPI()

app.include_router(admin.router)
app.include_router(users.router)
app.include_router(auth.router)