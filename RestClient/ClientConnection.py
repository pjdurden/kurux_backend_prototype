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


@query_blueprint.route("/crud/add_query", methods=['POST'])
# stock_Name, stock_Price,stock_Sold,stock_Sold,TVL,netIncome,revenue,Asset
# the company info needs to be send as a json object for POST request body for it to work with this
def add_data():
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            status = db.LISTED_STOCKS.insert_one(request.get_json())
            return dumps({'insert': 'SUCCESS'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


@query_blueprint.route("/crud/get_query", methods=['GET'])
def get_data():
    try:
        status = db.LISTED_STOCKS.find()
        return dumps(status)
    except Exception as e:
        return dumps({'error': str(e)})


# the Json should be in this format to update_data ,this query updates the info given in the set
# { "Stock_Name": "Google" , "Stock_Price": "100"}
# this function will set stock price to 100
@query_blueprint.route("/crud/update_stock_price", methods=['POST'])
def update_data():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            company_name = request_json['Stock_Name']
            price_to_update = request_json['Stock_Price']
            status = db.LISTED_STOCKS.update_one(
                {"Stock_Name": company_name},
                {
                    "$set": {
                        "Stock_Price": str(price_to_update)
                    }
                }
            )
            print(price_to_update)
            return dumps({'update': 'SUCCESS'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


# for deletion the request json should be in this format
# {"Stock_Name":criteria}
@ query_blueprint.route("/crud/delete_query", methods=['POST'])
def delete_data():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            status = db.LISTED_STOCKS.delete_many(request.get_json())
            # print(request.get_json())
            return dumps({'delete': 'SUCCESS'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})
