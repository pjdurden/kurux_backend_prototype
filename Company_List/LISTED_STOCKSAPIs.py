from flask import Flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
import json
from env import *
from DBUtil.pushDataUtil import pushData
from RestClientHelper.ClientConnectionHelper import *
from flask import Blueprint

from unique_id_generator.unique_id_generator import give_new_unique_id

client = MongoClient(mongoClient)
db = client.INVENTORY

query_blueprint = Blueprint('queries', 'REST_API')

# pushing a company info into Mongo Collection

# All the units are in Rs


# {
#   "Company_Name": "Bisleri Ltd",
#   "Owner": "Amit22",
#   "Ticker_Symbol": "BSL",
#   "IPEO_Price": "55",
#   "Company_Website": "https://www.google.com",
#   "Company_Linkedin": "linkedin id",
#   "Product_Service_Desc": "para over the company's desc",
#   "Earlier_Fund_Raised": "",
#   "Revenue": "",
#   "Is_Profitable": "",
#   "Company_Size": "",
#   "Existing_Liabilities": "",
#   "Pitch_Link": ""
# }

# the company info needs to be send as a json object for POST request body for it to work with this

@query_blueprint.route("/crud/add_company", methods=['POST'])
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


# pass the following info to this
# {
#     "Ticker_Symbol":"BSL"
# }

@query_blueprint.route("/crud/get_company_details", methods=['POST'])
def get_company_details():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            ticker_symbol = request_json["Ticker_Symbol"]

            status = json.loads(
                dumps(db.LISTED_STOCKS.find({"Ticker_Symbol": ticker_symbol})))

            if len(status) == 0:
                return dumps({'status': 'Company does not exist'})

            return status[0]
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


@query_blueprint.route("/crud/get_company_list", methods=['GET'])
def get_data():
    try:
        status = db.LISTED_STOCKS.find()
        return dumps(status)
    except Exception as e:
        return dumps({'error': str(e)})


# the Json should be in this format to update_data ,this query updates the info given in the set
# { "Ticker_Symbol": "ABC" , "Update_Value": "100" , "Update_Key": "Stock_Price" }
# this function will set stock price to 100
@query_blueprint.route("/crud/update_company", methods=['POST'])
def update_data():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            company_symbol = request_json['Ticker_Symbol']
            update_key = request_json['Update_Key']
            update_value = request_json['Update_Value']
            status = db.LISTED_STOCKS.update_one(
                {"Ticker_Symbol": company_symbol},
                {
                    "$set": {
                        update_key: update_value
                    }
                }
            )
            return dumps({'update': 'SUCCESS'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


# for deletion the request json should be in this format
# {"Ticker_Symbol": "ABC" }
@ query_blueprint.route("/crud/delete_company", methods=['POST'])
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


# pass following info into this
# {
#     "Owner_Id": "Amit22",
#     "Ticker_Symbol": "BSL",
#     "Price_Per_Unit": 323,
#     "Units": 444
# }


@query_blueprint.route("/ipeo/add_ipeo_sell_order", methods=['POST'])
def add_owner_sell_order():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            ticker_symbol = request_json["Ticker_Symbol"]
            owner_id = request.json["Owner_Id"]
            price_per_unit = int(request.json["Price_Per_Unit"])
            units = int(request_json["Units"])

            id_stat = give_new_unique_id()

            # add sell order
            if id_stat[0] != False:

                client.Company_Sell_Order[ticker_symbol].insert_one(
                    {
                        "_id": id_stat[1],
                        "Units": units,
                        "Price_Per_Unit": price_per_unit,
                        "Seller_Id": owner_id,
                        "Is_Owner": 1

                    }
                )

                client[owner_id].Sell_Order.insert_one(
                    {
                        "_id": id_stat[1],
                        "Units": units,
                        "Price_Per_Unit": price_per_unit,
                        "Seller_Id": owner_id,
                        "Is_Owner": 1,
                        "Ticker_Symbol": ticker_symbol
                    }
                )

            # print(request.get_json())
            return dumps({'ipeo': 'SUCCESS'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})
