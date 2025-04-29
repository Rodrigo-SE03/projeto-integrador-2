import asyncio
import random
import httpx
from loguru import logger

from utils import obter_endereco
# URL do servidor
API_URL = 'http://localhost:81'

# Configurações do sensor
MAX_DIST = 110
MIN_DIST_TO_CLEAN = 10

MAX_DIST_GAIN_PER_READING = 5
MIN_DIST_GAIN_PER_READING = -1
PCT_TO_CLEAN = 0.3

NUM_SENSORS = 2
WAIT_TIME = 5

VERBOSE = True

## Configurações de Localização
# Coordenadas de Goiânia
LAT = -16.6869
LON = -49.2648

# Variação em torno de Goiânia (em graus)
LAT_RANGE = 0.02
LON_RANGE = 0.01

class Sensor:
    def __init__(self, mac, lat, lon, rua, verbose=False):
        self.verbose = verbose
        self.mac = mac
        self.lat = lat
        self.lon = lon
        self.rua = rua
        self.dist = MAX_DIST
    
    async def send_reading(self):
        if self.verbose:
            logger.info(f"Enviando leitura de {self.mac}: {self.dist}m, ({self.lat}, {self.lon})")

        data = {
            'distancia': round(self.dist, 3),
            'latitude': self.lat,
            'longitude': self.lon,
            'mac': self.mac,
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(f'{API_URL}/leituras', json=data)
                if response.status_code != 200:
                    response.raise_for_status()
            except httpx.RequestError as e:
                logger.error(f"Erro ao enviar leitura: {e}")
            except httpx.HTTPStatusError as e:
                logger.error(f"Erro de status HTTP: {e}")
            except Exception as e:
                logger.error(f"Erro inesperado: {e}")


    async def update_dist(self):
        self.dist += random.uniform(-MAX_DIST_GAIN_PER_READING, -MIN_DIST_GAIN_PER_READING)

        if self.dist > MAX_DIST:
            self.dist = MAX_DIST

        if self.dist <= MIN_DIST_TO_CLEAN:
            if random.random() < PCT_TO_CLEAN:
                self.dist = MAX_DIST
            else:
                self.dist = max(self.dist, 0)
        await self.send_reading()


existing_macs = set()
def gerar_mac_unico():
    while True:
        mac = ''.join(f"{random.randint(0, 255):02x}" for _ in range(6))
        if mac not in existing_macs:
            existing_macs.add(mac)
            return mac
        
async def main():
    sensores = []
    logger.info("Iniciando simulação de sensores...")
    for _ in range(NUM_SENSORS):
        mac = gerar_mac_unico()
        while True:
            lat = random.uniform(LAT - LAT_RANGE, LAT + LAT_RANGE)
            lon = random.uniform(LON - LON_RANGE, LON + LON_RANGE)
            rua = obter_endereco(lat, lon)
            if rua != 'Rua não encontrada': break
        sensores.append(Sensor(mac, lat, lon, rua, verbose=VERBOSE))

    while True:
        await asyncio.gather(*(s.update_dist() for s in sensores))
        await asyncio.sleep(WAIT_TIME)


if __name__ == '__main__':
    asyncio.run(main())