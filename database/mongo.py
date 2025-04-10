import pymongo


client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client['projeto_integrador']
collection_leituras = db['leituras']


def aggregate(collection, pipeline):
    result = list(collection.aggregate(pipeline))
    for doc in result:
        doc['_id'] = str(doc['_id'])
    return result