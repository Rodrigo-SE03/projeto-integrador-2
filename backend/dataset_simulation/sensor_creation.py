from .configs import SimulationModel
from .sensor import Sensor

from database.mongo import get_collection
from utils.localization import obter_endereco

from networkx import MultiGraph
import geopandas as gpd
import osmnx as ox

from typing import Tuple, List, Set, Optional
from datetime import datetime
from loguru import logger
from tqdm import tqdm
import random

existing_macs:Set[str] = set()


async def get_sensores_from_db(sim_model: SimulationModel) -> Tuple[list[Sensor], Optional[datetime]]:

    logger.info("Lendo sensores do banco de dados...")
    sensores:list[Sensor] = []
    cursor = get_collection().find()
    timestamp = None
    for item in cursor:

        tmp_timestamp = datetime.strptime(item['timestamp'], "%d-%m-%Y %H:%M:%S")
        if timestamp is None:
            timestamp = tmp_timestamp
        else:
            timestamp = max(timestamp, tmp_timestamp)

        mac = item['mac']
        lat = item['latitude']
        lon = item['longitude']
        rua = item['rua']
        tipo_zona = item['tipo_zona']

        if mac not in existing_macs:
            existing_macs.add(mac)
            sensores.append(Sensor(mac, lat, lon, rua, tipo_zona, sim_model.reading_configs, sim_model.configs.verbose))
    
    return sensores, timestamp


async def gerar_mac_unico():
    while (mac := ''.join(f"{random.randint(0, 255):02x}" for _ in range(6))) in existing_macs:
        print('.', end='')
    existing_macs.add(mac)
    return mac


async def sample_points_projected(G_proj: MultiGraph, num_points: int) -> List[Tuple[float, float]]:
    points_proj: gpd.GeoDataFrame = ox.utils_geo.sample_points(G_proj, num_points)  # type: ignore
    points_geo: gpd.GeoDataFrame = points_proj.to_crs(epsg=4326)  # type: ignore
    return [(point.x, point.y) for point in points_geo.geometry]  # type: ignore


async def criar_sensores_faltantes(sensores: List[Sensor], sim_model: SimulationModel) -> bool:
    logger.info("Iniciando criação de sensores...")

    total_para_criar = sim_model.configs.num_sensors - len(sensores)
    margem = int(total_para_criar * 0.3) + 5

    place = "Goiânia, Goiás, Brasil"
    G = ox.graph_from_place(place, network_type='drive')
    G_proj = ox.project_graph(G)
    G_proj = G_proj.to_undirected()

    pontos = await sample_points_projected(G_proj, total_para_criar + margem)

    idx = 0
    max_tentativas = 5
    progress = tqdm(total=total_para_criar, desc="Criando sensores")

    while len(sensores) < sim_model.configs.num_sensors and idx < len(pontos):
        
        for _ in range(max_tentativas):
            lon, lat = pontos[idx]
            idx += 1

            rua, tipo_zona = await obter_endereco(lat, lon)
            if rua.startswith('.'): rua = rua[1:]
            if rua != 'Rua não encontrada': break
            if idx >= len(pontos): break

        else: continue

        mac = await gerar_mac_unico()
        sensores.append(Sensor(mac, lat, lon, rua, tipo_zona, sim_model.reading_configs, sim_model.configs.verbose))
        progress.update(1)
    
    progress.close()
    if len(sensores) < sim_model.configs.num_sensors:
        logger.warning(f"Quantidade de sensores criada ({len(sensores)}) menor que o alvo ({sim_model.configs.num_sensors})")
    
    return True