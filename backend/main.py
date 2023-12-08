import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import backend.crud
from backend.core.models import Base, db_helper
from backend.views import address_router, block_router, chain_router, transaction_router
from backend.lifespan import lifespan


app = FastAPI(lifespan=lifespan)
app.include_router(address_router)
app.include_router(transaction_router)
app.include_router(block_router)
app.include_router(chain_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return "Hello!"


if __name__ == "__main__":
    uvicorn.run("main:app")
