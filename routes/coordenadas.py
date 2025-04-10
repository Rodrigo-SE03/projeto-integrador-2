from database.mongo import collection_leituras, aggregate
from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def get_coordenadas():
    pipeline = [
        {
            "$project": {
                "lat": "$latitude",
                "long": "$longitude"
            }
        }
    ]

    dados = aggregate(collection_leituras, pipeline)
    return dados
