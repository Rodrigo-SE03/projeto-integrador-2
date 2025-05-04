from database.mongo import aggregate, collection_leituras
from ia.GA.genetic_algorithm_model import genetic_algorithm
from ia.GA.routing_utils import two_opt, route_distance
from routes.models import RotaLimiar
from fastapi import APIRouter, BackgroundTasks, Response
from loguru import logger

router = APIRouter()

rota = None
flag_training = False
origin = (-16.6869, -49.2648)

def calculate(limiar:float):
    global rota, flag_training
    if flag_training:  return
    flag_training = True
    try:
        pipeline = [
            {
                "$addFields": {
                    "timestamp": {
                        "$dateFromString": {
                            "dateString": "$timestamp",
                            "format": "%d-%m-%Y %H:%M:%S"
                        }
                    }
                }
            },
            {
                "$sort": {
                    "mac": 1,
                    "timestamp": -1
                }
            },
            {
                "$group": {
                    "_id": "$mac",
                    "distancia": {"$first": "$distancia"},
                    "latitude": {"$first": "$latitude"},
                    "longitude": {"$first": "$longitude"},
                },
            },
            {
                "$match": {
                    "distancia": {"$lt": limiar}
                }
            }
        ]
        resultados = aggregate(collection_leituras, pipeline)
        resultados_dict = {(p['latitude'], p['longitude']): p for p in resultados}
        points = list(resultados_dict.keys())
        rota_tmp = genetic_algorithm(points, origin, use_nn_start=True)
        rota_tmp = two_opt(rota_tmp, points, origin)
        rota =[resultados_dict[(points[i][0], points[i][1])] for i in rota_tmp]
        logger.info(f"Rota calculada")
        
    except Exception as e:
        logger.exception(f"Error in calculate: {e}")
    flag_training = False


@router.post("")
def calculate_route(rota_limiar:RotaLimiar, background_tasks: BackgroundTasks):
    limiar = rota_limiar.limiar
    limiar = 2000.0
    if limiar < 0:
        return Response(status_code=400, content="Limiar must be greater than 0.")

    global flag_training
    if flag_training:
        return Response(status_code=503, content="Model is already calculating an route, please try again later.")
    
    background_tasks.add_task(calculate, limiar)
    return Response(status_code=200, content="Route calculation started.")



@router.get("")
def get_rota():
    global rota, flag_training
    if flag_training:
        return Response(status_code=503, content="Model is already calculating an route, please try again later.")
    elif rota is None:
        return Response(status_code=503, content="Route not calculated yet.")
    
    
    points = [(p['latitude'], p['longitude']) for p in rota]
    distancia = route_distance(range(len(points)), points, origin)
    return {"distancia": distancia, "rota": rota}


@router.post("/origin")
def update_origin(new_origin: tuple[float, float]):
    global origin
    if not isinstance(new_origin, tuple) or len(origin) != 2:
        return Response(status_code=400, content="Origin must be a tuple of (latitude, longitude).")
    
    if not (-90 <= origin[0] <= 90) or not (-180 <= origin[1] <= 180):
        return Response(status_code=400, content="Invalid latitude or longitude values.")
    
    origin = new_origin
    return Response(status_code=200, content="Origin updated successfully.")