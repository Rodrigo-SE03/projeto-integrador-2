from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from routes import leituras, coordenadas, lstm, rotas
from database.mongo import init_database
from ia.GA.model import genetic_algorithm
from ia.LSTM.model import load_model

from contextlib import asynccontextmanager
from typing import AsyncIterator
from loguru import logger


@asynccontextmanager
async def lifespan(_:FastAPI) -> AsyncIterator[None]:
    init_database()
    try: lstm.lstm_model, lstm.lstm_scaler, lstm.lstm_le = load_model()
    except Exception as e:
        logger.warning(f"Failed to load LSTM model: {e}")
        lstm.create_lstm_model()

    population = [(float(i), float(i)) for i in range(3)]
    origin = (3.0, 3.0)
    genetic_algorithm(population, origin, initial=True)
    yield


app = FastAPI(lifespan=lifespan)
app.add_middleware( CORSMiddleware, allow_origins=["http://localhost:5173"], 
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

app.include_router(leituras.router, prefix="/leituras", tags=["leituras"])
app.include_router(coordenadas.router, prefix="/coordenadas", tags=["coordenadas"])
app.include_router(lstm.router, prefix="/lstm", tags=["lstm"])
app.include_router(rotas.router, prefix="/rotas", tags=["rotas"])


@app.get("/")
async def home() -> Response: return Response(content="Hello World", media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=81, reload=True)