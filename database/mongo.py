from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from pymongo import DESCENDING
from loguru import logger

MONGO_USER = 'user_pi'
MONGO_PASSWORD = 'XpIAmprxBkT59jet'
uri = f"mongodb+srv://{MONGO_USER}:{MONGO_PASSWORD}@cluster0.b77cm.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
local_uri = "mongodb://localhost:27017/"

db = None
collection_leituras = None
def init_db():
    global db, collection_leituras
    try: 
        logger.info("Connecting to MongoDB Atlas...")
        client = MongoClient(uri, server_api=ServerApi('1'))
        client.admin.command('ping')
        logger.info("MongoDB Atlas connection successful")
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {e}")
        logger.warning("Using local MongoDB instance")
        client = MongoClient(local_uri)

    db = client['projeto_integrador']
    collection_leituras = db['leituras']


def aggregate(collection, pipeline):
    if not db: raise Exception("Database not initialized. Call init_db() first.")
    result = list(collection.aggregate(pipeline))
    for doc in result:
        doc['_id'] = str(doc['_id'])
    return result