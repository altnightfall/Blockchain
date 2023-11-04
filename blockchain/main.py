from fastapi import FastAPI
import blockchain.src.bchain

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}
