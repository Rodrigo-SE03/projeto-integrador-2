from pydantic import BaseModel


class Dados(BaseModel):
    distancia:float
    horario:str
    latitude:float
    longitude:float
