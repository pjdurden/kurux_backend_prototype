from pymongo import MongoClient
from bson.json_util import dumps

app = Flask(__name__)

# GET Request


@app.route("/get_query", methods=['GET'])
def get_information(db, collection, dataToGet):
    try:
        result = db.collection.find(dataToGet)
        return dumps(result)
    except Exception as e:
        return dumps({'error': str(e)})


# Post Request
@app.route("/add_query", methods=['POST'])
def add_information(db, collection, dataToPost):
    try:
        status = db.collection.insert_one(dataToPost)
        return dumps({'message': 'SUCCESS'})
    except Exception as e:
        return dumps({'error': str(e)})
