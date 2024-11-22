from fastapi import FastAPI
from src.endpoint import api

app = FastAPI()

app.include_router(api.router)

@app.get("/")
async def root():
    return {"message":"Hello"}