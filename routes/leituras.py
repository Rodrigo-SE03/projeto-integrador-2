from routes.models import Dados, Tick
from database.mongo import collection_leituras, DESCENDING

from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Response, BackgroundTasks
from utils import obter_endereco
from openweather import get_rain

import datetime
import asyncio
import json

router = APIRouter()
clients: List[WebSocket] = []


is_simulation = False
simulation_time = None

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


async def add_leitura(dados:Dados):
    if dados.rua is None:
        dados.rua, dados.tipo_zona = obter_endereco(dados.latitude, dados.longitude)
    
    if dados.is_simulation:
        global is_simulation, simulation_time
        if not is_simulation:
            is_simulation = True
            simulation_time = datetime.datetime.now()
        timestamp = simulation_time
        rain_level = dados.rain_level
    else:
        timestamp = datetime.datetime.now()
        rain_level = get_rain(dados.latitude, dados.longitude)

    
    leitura_com_mac = collection_leituras.find_one({"rua": dados.rua, "mac": dados.mac})
    if leitura_com_mac:
        rua_id = leitura_com_mac.get('rua_id', 1)
    else:
        max_id_document = list(collection_leituras.find({"rua": dados.rua}).sort("rua_id", DESCENDING).limit(1))
        max_id = max_id_document[0].get('rua_id', 0) if max_id_document else 0
        rua_id = max_id + 1

    dado = {
        "distancia": dados.distancia,
        "timestamp": timestamp.strftime("%d-%m-%Y %H:%M:%S"),
        "latitude": dados.latitude,
        "longitude": dados.longitude,
        "rain_level": rain_level,
        "rua": dados.rua,
        "tipo_zona": dados.tipo_zona,
        "rua_id": rua_id,
        "mac": dados.mac
    }
    collection_leituras.insert_one(dado)
    dado.pop("_id")
    await notify_clients(json.dumps(dado))


@router.post("")
async def post_leitura(dados:Dados, background_tasks: BackgroundTasks):
    background_tasks.add_task(add_leitura, dados)
    return Response(status_code=200)


@router.post("/end_simulation")
async def end_simulation():
    global is_simulation, simulation_time
    if is_simulation:
        is_simulation = False
        simulation_time = None
        return {"message": "Simulação encerrada com sucesso."}
    else:
        return {"message": "Nenhuma simulação em andamento."}
    

@router.post("/tick_simulation")
async def tick_simulation(tick:Tick):
    global is_simulation, simulation_time
    if is_simulation:
        simulation_time = simulation_time + datetime.timedelta(days=tick.days, hours=tick.hours, minutes=tick.minutes, seconds=tick.seconds)
        return {
            "message": "Simulação avançada com sucesso.",
            "simulation_time": simulation_time.strftime("%d-%m-%Y %H:%M:%S")
        }
    else:
        return {"message": "Nenhuma simulação em andamento."}
