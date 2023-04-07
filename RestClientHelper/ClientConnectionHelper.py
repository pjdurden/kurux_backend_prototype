from pymongo import MongoClient
from bson.json_util import dumps
from flask import Flask


# GET Request

# @app.route("/get_query", methods=['GET'])
def get_information(collection, dataToGet):
    try:
        result = collection.find(dataToGet)
        return dumps(result)
    except Exception as e:
        return dumps({'error': str(e)})


# Post Request
def add_information(collection, dataToPost):
    try:
        status = collection.insert_one(dataToPost)
        return dumps({'message': 'SUCCESS'})
    except Exception as e:
        return dumps({'error': str(e)})
