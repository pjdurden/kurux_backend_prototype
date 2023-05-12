from flask import Flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
import json
from env import *
from DBUtil.pushDataUtil import pushData
from RestClientHelper.ClientConnectionHelper import *
from flask import Blueprint
from Wallet import UsersWalletUtils

user_details_blueprint = Blueprint('user_details', 'REST_API')
client = MongoClient(mongoClient)

# pass the following info to this
# {
#     "User_Id":"Amit22"
# }


@user_details_blueprint.route("/user/portfolio", methods=['POST'])
def portfolio():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]

            status = json.loads(dumps(client[user_id].Portfolio.find()))

            if len(status) == 0:
                return dumps({'status': 'User has no portfolio'})

            return status
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22"
# }


@user_details_blueprint.route("/user/buy_orders", methods=['POST'])
def buy_orders():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]

            status = json.loads(dumps(client[user_id].Buy_Order.find()))

            if len(status) == 0:
                return dumps({'status': 'User has no Buy Orders'})

            return status
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22"
# }


@user_details_blueprint.route("/user/sell_orders", methods=['POST'])
def sell_orders():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]

            status = json.loads(dumps(client[user_id].Sell_Order.find()))

            if len(status) == 0:
                return dumps({'status': 'User has no Sell Orders'})

            return status
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22"
# }


@user_details_blueprint.route("/user/order_history", methods=['POST'])
def order_history():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]

            status = json.loads(dumps(client[user_id].Order_History.find()))

            if len(status) == 0:
                return dumps({'status': 'User has no Order History'})

            return status
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22"
# }


@user_details_blueprint.route("/user/tran_history", methods=['POST'])
def tran_history():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]

            status = json.loads(dumps(client[user_id].Tran_History.find()))

            if len(status) == 0:
                return dumps({'status': 'User has no Transaction History'})

            return status
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22"
# }


@user_details_blueprint.route("/user/get_user_details", methods=['POST'])
def get_user_details():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]

            status = json.loads(dumps(client[user_id].User_Details.find()))

            if len(status) == 0:
                return dumps({'status': 'User has no User Details'})

            return status
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})
