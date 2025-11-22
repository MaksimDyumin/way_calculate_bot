import json
from fastapi import APIRouter


router = APIRouter()

@router.get("/ping")
async def ping():
    return {"message": "pong"}

@router.get("/some-data")
async def getSomeData():
    file_path = "./data/data.json"
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data

@router.post("/webapp-data")
async def receive_webapp_data(payload: dict):
    print("Received data:", payload)
    return {"status": "ok", "echo": payload}