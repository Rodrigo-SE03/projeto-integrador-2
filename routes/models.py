from pydantic import BaseModel
from datetime import datetime


class Dados(BaseModel):
    distancia:float
    latitude:float
    longitude:float
    mac:str
    rua:str = None
    tipo_zona:str = None
    rain_level:int = 0
    timestamp:str = None


class Tick(BaseModel):
    seconds:int = 0
    minutes:int = 0
    hours:int = 0
    days:int = 0


class RotaLimiar(BaseModel):
    limiar:float