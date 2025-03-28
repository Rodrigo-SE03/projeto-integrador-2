
from models import Dados
from fastapi import FastAPI, Query
app = FastAPI()


@app.post("/")
async def root(dados:Dados):
    print(dados)
    return "ok"

@app.get("/")
async def home():
    print("Hello World")
    return "Hello World"
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=81, reload=True)