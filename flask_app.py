

from flask import Flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
import json

client = MongoClient('localhost:27017')
db = client.INVENTORY

app = Flask(__name__)


@app.route("/add_contact", methods=['POST'])
def add_contact():
    try:
        comment_doc = {'movie_id': 'heya'}
        db.LISTED_STOCKS.insert(comment_doc)
        return dumps({'message': 'SUCCESS'})
    except Exception as e:
        return dumps({'error': str(e)})


@app.route("/get_all_contact", methods=['GET'])
def get_all_contact():
    try:
        contacts = db.LISTED_STOCKS.find()
        return dumps(contacts)
    except Exception as e:
        return dumps({'error': str(e)})
