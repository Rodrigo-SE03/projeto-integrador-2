from .configs import SimulationModel
from .sensor_creation import  get_sensores_from_db, criar_sensores_faltantes

from datetime import datetime, timedelta
from loguru import logger
import asyncio, random, json, os


pause_event = asyncio.Event()
pause_event.set()

async def monitor_commands():
    loop = asyncio.get_event_loop()
    while True:
        cmd = await loop.run_in_executor(None, input, "")
        if cmd == 'pause':
            pause_event.clear()
            logger.info("Simulação pausada.")
        elif cmd == 'resume':
            pause_event.set()
            logger.info("Simulação retomada.")


def simular_chuva():
    p = random.random()
    return (
        0 if p < 0.6 else
        1 if p < 0.85 else
        2 if p < 0.97 else 3
    )


async def run_simulation():

    logger.info("Iniciando simulação...")
    json_file = os.path.join(os.path.dirname(__file__), 'configs.json')
    with open(json_file, 'r') as f:
        configs_json = json.load(f)

    sim_model = SimulationModel(**configs_json)
    sensores, timestamp = await get_sensores_from_db(sim_model)
    if len(sensores) < sim_model.configs.num_sensors:
        await criar_sensores_faltantes(sensores, sim_model)

    asyncio.create_task(monitor_commands())
    logger.warning("Digite 'pause' para pausar a simulação e 'resume' para retomar.")

    if not timestamp: timestamp = datetime.now()
    
    while True:
        await pause_event.wait()
        logger.info("Iniciando envio de leituras...")
        chuva = simular_chuva()
        await asyncio.gather(*(s.update_dist(chuva, timestamp) for s in sensores))
        timestamp += timedelta(days=sim_model.ticks.tick_days, hours=sim_model.ticks.tick_hours, 
                        minutes=sim_model.ticks.tick_minutes, seconds=sim_model.ticks.tick_seconds)
        
        await asyncio.sleep(sim_model.configs.wait_time)