from routes.models import Dados
from database.mongo import collection_leituras

from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Response

import datetime
import asyncio
import json

router = APIRouter()

# Lista para manter os clientes conectados
clients: List[WebSocket] = []

async def notify_clients(data):
    for client in clients:
        try:
            await client.send_json(data)
        except:
            clients.remove(client)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    clients.append(websocket)
    try:
        while True:
            await asyncio.sleep(1)  # mantém a conexão aberta sem travar
    except WebSocketDisconnect:
        clients.remove(websocket)


@router.get("")
async def get_leituras():
    dados = collection_leituras.find()
    dados = list(dados)
    for dado in dados:
        dado["_id"] = str(dado["_id"])
    return dados


@router.post("")
async def root(dados:Dados):
    dado = {
        "distancia": dados.distancia,
        "timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "latitude": dados.latitude,
        "longitude": dados.longitude,
        "mac": dados.mac
    }
    collection_leituras.insert_one(dado)
    dado.pop("_id")
    await notify_clients(json.dumps(dado))
    return Response(status_code=200)