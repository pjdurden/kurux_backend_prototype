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

wallet_blueprint = Blueprint('wallet_api', 'REST_API')


# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "PIN": "5432122"
# }
@wallet_blueprint.route("/wallet/check_balance", methods=['POST'])
def check_balance():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]
            user_pin = request_json["PIN"]

            status = UsersWalletUtils.check_balance(user_id, user_pin)
            if(status[0] == True):
                return dumps({'balance': status[1]})
            else:
                return dumps({'error': status[1]})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


# pass the following info to this
# {
#     "Sender_User_Id":"Amit22",
#     "Reciever_User_Id":"Amit22",
#     "PIN": "5432122"
#     "Amount": "133"
# }
@wallet_blueprint.route("/wallet/send_money", methods=['POST'])
def send_money():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            sender_user_id = request_json["Sender_User_Id"]
            reciever_user_id = request_json["Reciever_User_Id"]
            sender_pin = request_json["PIN"]
            amount = request_json["Amount"]

            if(sender_user_id == reciever_user_id):
                return dumps({'error': 'Sender and Reciever cannot be the same'})

            status = UsersWalletUtils.send_money(
                sender_user_id, reciever_user_id, sender_pin, amount)
            if(status[0] == True):
                return dumps({'msg': status[1]})
            else:
                return dumps({'error': status[1]})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "PIN": "5432122"
#     "Amount": "133",
#     "Master_Pass": "M4ST3R9A55"
# }
@wallet_blueprint.route("/wallet/add_money", methods=['POST'])
def add_money():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]
            pin = request_json["PIN"]
            amount = request_json["Amount"]
            master_pass = request_json["Master_Pass"]

            status = UsersWalletUtils.add_money(
                user_id, pin, amount, master_pass)
            if(status[0] == True):
                return dumps({'msg': status[1]})
            else:
                return dumps({'error': status[1]})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})
