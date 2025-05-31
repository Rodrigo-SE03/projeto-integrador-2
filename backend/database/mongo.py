from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo.collection import Collection
from pymongo.database import Database
from loguru import logger
from typing import Any, Optional, Dict

MONGO_USER = 'user_pi'
MONGO_PASSWORD = 'XpIAmprxBkT59jet'
MONGO_ATLAS_URI = (
    f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}"
    "@cluster0.b77cm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)
LOCAL_URI  = "mongodb://localhost:27017/"
USE_LOCAL  = True

DATABASE_NAME = 'projeto_integrador'
COLLECTION_NAME = 'leituras'


database: Optional[Database[Any]] = None
collection_leituras: Optional[Collection[Any]] = None

def init_database() -> Collection[Any]:
    global database, collection_leituras

    if USE_LOCAL:
        logger.info("Tentando conectar ao MongoDB local...")
        client: MongoClient[Any]= MongoClient(LOCAL_URI)
        logger.info("Conexão com o MongoDB local bem-sucedida")

    else:
        logger.info("Tentando conectar ao MongoDB Atlas...")
        client: MongoClient[Any] = MongoClient(MONGO_ATLAS_URI, server_api=ServerApi('1'))
        logger.info("Conexão com o MongoDB Atlas bem-sucedida")

    database = client[DATABASE_NAME]
    collection_leituras = database[COLLECTION_NAME]
    return collection_leituras


def get_collection() -> Collection[Any]:
    if collection_leituras is None: return init_database()
    return collection_leituras


def aggregate(pipeline: list[dict[str, Any]]) -> list[Dict[str, Any]]:
    if database == None or collection_leituras == None: init_database()
    if collection_leituras == None: return []

    result = list(collection_leituras.aggregate(pipeline))
    for doc in result: doc['_id'] = str(doc['_id'])
    return result