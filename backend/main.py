from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import backend.src.bchain
from tortoise import Tortoise

from backend.src.database.register import register_tortoise
from backend.src.database.config import TORTOISE_ORM


Tortoise.init_models(["backend.src.database.models"], "models")

from backend.src.routes import users # Must be after Tortoise

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(users.router)

register_tortoise(app, config=TORTOISE_ORM, generate_schemas=False)

@app.get("/")
async def root():
    return "Hello!"
