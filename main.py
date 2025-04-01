from models import Dados
from fastapi import FastAPI, Query
import pymongo
import json

app = FastAPI()
client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['projeto_integrador']
collection = db['leituras']

@app.post("/")
async def root(dados:Dados):
    print(dados)
    collection.insert_one({
        "distancia": dados.distancia,
        "timestamp": dados.horario,
        "latitude": dados.latitude,
        "longitude": dados.longitude
    })
    return "ok"

@app.get("/")
async def home():
    print("Hello World")
    return "Hello World"
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=81, reload=True)