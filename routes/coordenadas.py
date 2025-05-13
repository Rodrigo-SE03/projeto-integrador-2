from database.mongo import get_collection, aggregate
from fastapi import APIRouter

router = APIRouter()

@router.get("")
async def get_coordenadas():
    pipeline = [
        {
            "$project": {
                "lat": "$latitude",
                "long": "$longitude",
                "mac": "$mac",
            }
        }
    ]

    dados = aggregate(get_collection(), pipeline)
    return dados
