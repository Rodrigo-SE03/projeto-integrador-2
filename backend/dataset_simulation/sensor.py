from .configs import ReadingsModel

from httpx import AsyncClient, RequestError, HTTPStatusError
from typing import Dict, Any

from loguru import logger
from datetime import datetime
import random


class Sensor:
    def __init__(self, mac:str, latitude:float, longitude:float, rua:str, regiao:str, configs:ReadingsModel, verbose:bool=False):
        self.verbose:bool = verbose
        self.mac:str = mac
        self.latitude:float = latitude
        self.longitude:float = longitude
        self.rua:str = rua
        self.regiao:str = regiao
        self.distancia:float = configs.max_distance
        self.configs:ReadingsModel = configs
    

    async def send_reading(self, nivel_chuva:int, timestamp:datetime):
        if self.verbose:
            logger.info(f"Enviando leitura de {self.mac}: {self.distancia}m, ({self.latitude}, {self.longitude})")

        data:Dict[str, Any] = {
            "distancia":round(self.distancia, 3),
            "latitude":self.latitude,
            "longitude":self.longitude,
            "rain_level":nivel_chuva,
            "rua":self.rua,
            "tipo_zona":self.regiao,
            "mac":self.mac,
            "timestamp":timestamp.strftime("%d-%m-%Y %H:%M:%S"),
        }

        url = f"{self.configs.api_url}/leituras"
        try:
            async with AsyncClient() as client:
                response = await client.post(url, json=data, timeout=10)
                response.raise_for_status()
        except (RequestError, HTTPStatusError) as e: logger.error(f"Erro ao enviar leitura ({type(e).__name__}): {e}")
        except Exception as e: logger.error(f"Erro inesperado: {e}")


    async def update_dist(self, nivel_chuva:int, timestamp:datetime):

        chuva_fator = [0.5, 1.0, 1.5, 2.0][nivel_chuva]
        max_reading, min_reading = self.configs.region_modificator.get(self.regiao, self.configs.region_modificator_default)

        ganho = random.uniform(-max_reading, -min_reading) * chuva_fator
        self.distancia += ganho

        self.distancia = min(self.distancia, self.configs.max_distance)

        if self.distancia <= self.configs.min_distance_to_clean:
            if random.random() < self.configs.pct_to_clean:
                self.distancia = self.configs.max_distance
            else:
                self.distancia = max(self.distancia, 0)

        await self.send_reading(nivel_chuva, timestamp)