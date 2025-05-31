from database.mongo import aggregate
from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()


@router.get("/")
async def get_coordenadas() -> JSONResponse:
    pipeline = [
        {
            "$project": {
                "lat": "$latitude",
                "long": "$longitude",
                "mac": "$mac",
            }
        }
    ]

    dados = aggregate(pipeline)
    return JSONResponse(content=dados)