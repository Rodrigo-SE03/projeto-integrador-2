import requests
import asyncio
import random

API_URL = 'http://localhost:81'
MAX_DIST = 110
WAIT_TIME = 5
NUM_SENSORS = 10

class sensor:
    def __init__(self, mac, lat, lon):
        self.mac = mac
        self.lat = lat
        self.lon = lon
        self.dist = MAX_DIST
    
    def send_leitura(self):
        data = {
            'distancia': self.dist,
            'latitude': self.lat,
            'longitude': self.lon,
            'mac': self.mac,
        }
        try:
            response = requests.post(f'{API_URL}/leituras', json=data)
            if response.status_code != 200:
                print(f"Erro ao enviar leitura de {self.mac}: {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Erro ao enviar leitura de {self.mac}: {e}")


    def update_dist(self):
        self.dist += random.uniform(-5, 1)
        if self.dist <= 10:
            if random.choice([True, False]):
                self.dist = MAX_DIST
            else:
                self.dist = max(self.dist, 0)
        self.send_leitura()


# Coordenadas de Goiânia
lat_goiania = -16.6869
lon_goiania = -49.2648

# Definir uma variação em torno de Goiânia (em graus)
lat_range = 0.5
lon_range = 0.5

async def main():
    sensores = []
    for i in range(NUM_SENSORS):
        lat = random.uniform(lat_goiania - lat_range, lat_goiania + lat_range)
        lon = random.uniform(lon_goiania - lon_range, lon_goiania + lon_range)
        mac = f'{i+1:012d}'
        sensores.append(sensor(mac, lat, lon))

    while True:
        for s in sensores:
            s.update_dist()
        await asyncio.sleep(WAIT_TIME)


if __name__ == '__main__':
    asyncio.run(main())