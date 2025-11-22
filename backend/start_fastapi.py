from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router
import json

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Для разработки
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)

@app.get("/")
async def root():
    file_path = "./data/data.json"
    with open(file_path, 'r') as f:
        data = json.load(f)
    return data




