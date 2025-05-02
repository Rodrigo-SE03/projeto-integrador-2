from pydantic import BaseModel


class Dados(BaseModel):
    distancia:float
    latitude:float
    longitude:float
    mac:str
    rua:str = None
    tipo_zona:str = None
    is_simulation:bool = False
    rain_level:int = 0


class Tick(BaseModel):
    seconds:int = 0
    minutes:int = 0
    hours:int = 0
    days:int = 0