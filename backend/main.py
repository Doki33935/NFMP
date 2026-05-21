from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import admin, auth, users, fire, references


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(users.router)
app.include_router(auth.router)
app.include_router(fire.router)
app.include_router(references.router)
