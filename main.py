from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import leituras, coordenadas

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return {"message": "Hello World"}
    
app.include_router(leituras.router, prefix="/leituras", tags=["leituras"])
app.include_router(coordenadas.router, prefix="/coordenadas", tags=["coordenadas"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=81, reload=True)