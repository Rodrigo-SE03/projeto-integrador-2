from pydantic import BaseModel, Field
from typing import Optional


class Dados(BaseModel):
    distancia:float = Field(..., description='Distância lida pelo sesnsor ultrasônico')
    latitude:float = Field(..., description='Latitude do sensor')
    longitude:float = Field(..., description='Longitude do sensor')
    mac:str = Field(..., description='MAC do sensor')

    #============= Dados extras passados para simulação do dataset ============================
    rua:Optional[str] = Field(default=None, description='Nome da rua (adquirido via simulação)')
    tipo_zona:Optional[str] = Field(default=None, description='Tipo de zona (adquirido via simulação)')
    rain_level:Optional[int] = Field(default=None, description='Nível de chuva (adquirido via simulação)')
    timestamp:Optional[str] = Field(default=None, description='Timestamp da leitura (adquirido via simulação)')