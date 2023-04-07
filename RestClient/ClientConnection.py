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

# All the units are in Dollars


@query_blueprint.route("/add_query", methods=['POST'])
# stock_Name, stock_Price,stock_Sold,stock_Sold,TVL,netIncome,revenue,Asset
# the company info needs to be send as a json object for POST request body for it to work with this
def add_company():
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            status = db.LISTED_STOCKS.insert_one(request.get_json())
            return dumps({'message': 'SUCCESS'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


@query_blueprint.route("/get_query", methods=['GET'])
def get_data():
    try:
        status = db.LISTED_STOCKS.find()
        return dumps(status)
    except Exception as e:
        return dumps({'error': str(e)})
