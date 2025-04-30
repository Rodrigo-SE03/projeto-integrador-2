from routes.models import Dados
from database.mongo import collection_leituras, DESCENDING

from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Response
from utils import obter_endereco

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
        dado["rua"] = str(dado["rua"]) + " [" + str(dado["rua_id"]) + "]"
        dado.pop("rua_id")
    return dados


@router.post("")
async def root(dados:Dados):
    if dados.rua is None:
        dados.rua = obter_endereco(dados.latitude, dados.longitude)

    
    leitura_com_mac = collection_leituras.find_one({"rua": dados.rua, "mac": dados.mac})
    if leitura_com_mac:
        rua_id = leitura_com_mac.get('rua_id', 1)
    else:
        max_id_document = list(collection_leituras.find({"rua": dados.rua}).sort("rua_id", DESCENDING).limit(1))
        max_id = max_id_document[0].get('rua_id', 0) if max_id_document else 0
        rua_id = max_id + 1

    dado = {
        "distancia": dados.distancia,
        "timestamp": datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "latitude": dados.latitude,
        "longitude": dados.longitude,
        "rua": dados.rua,
        "rua_id": rua_id,
        "mac": dados.mac
    }
    collection_leituras.insert_one(dado)
    dado.pop("_id")
    await notify_clients(json.dumps(dado))
    return Response(status_code=200)