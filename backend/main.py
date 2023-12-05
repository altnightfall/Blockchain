from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import backend.src.bchain


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://localhost",],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return "Hello!"
