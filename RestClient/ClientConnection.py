from flask import Flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
import json
from env import *
from DBUtil.pushDataUtil import pushData
from RestClientHelper.ClientConnectionHelper import *
from flask import Blueprint

client = MongoClient(mongoClient)
db = client.INVENTORY

query_blueprint = Blueprint('queries', 'REST_API')

# pushing a company info into Mongo Collection


@query_blueprint.route("/add_query", methods=['POST'])
def push_Data():
    try:
        dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        status = db.LISTED_STOCKS.insert_one(dataToPush)
        return dumps({'message': 'SUCCESS'})
    except Exception as e:
        return dumps({'error': str(e)})


@query_blueprint.route("/get_query", methods=['GET'])
def get_data():
    try:
        status = db.LISTED_STOCKS.find()
        return dumps(status)
    except Exception as e:
        return dumps({'error': str(e)})
