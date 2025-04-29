from pydantic import BaseModel


class Dados(BaseModel):
    distancia:float
    latitude:float
    longitude:float
    mac:str
    rua:str = None
