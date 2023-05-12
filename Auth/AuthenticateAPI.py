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
cred_db = client.Auth
cred_collection = cred_db.Auth_details

authenticate_blueprint = Blueprint('authenticate', 'REST_API')

# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "User_Pass": "Alien321"
# }


@authenticate_blueprint.route("/auth/validate", methods=['POST'])
def authenticate():
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_name = request_json["User_Id"]
            user_pass = request_json["User_Pass"]
            # print(user_name, user_pass)

            status_info = dumps(cred_collection.find({"User_Id": user_name}))

            status = json.loads(status_info)

            if(len(status) == 0):
                return dumps({'error': 'User does not exist'})
            # print(status[0])
            # for j in status:
            #     print(j)
            status_pass = status[0]['User_Pass']
            # print(status_pass)
            if(user_pass == status_pass):
                return dumps({'auth': 'SUCCESS'})
            else:
                return dumps({'error': 'FAIL'})
        else:
            return dumps({'error': 'Content-Type not supported'})
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "Old_Pass": "Alien321",
#     "New_Pass": "Temp321"
# }


def check_pin(user_id, pin):
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}

        status_info = dumps(cred_collection.find({"User_Id": user_id}))

        status = json.loads(status_info)

        if(len(status) == 0):
            return [False, 'User does not exist']
        # print(status[0])
        # for j in status:
        #     print(j)
        status_pass = status[0]['User_PIN']
        # print(status_pass)
        if(pin == status_pass):
            return [True, 'Correct PIN']
        else:
            return [False, 'Wrong PIN']

    except Exception as e:
        return [False, str({'error': str(e)})]


@authenticate_blueprint.route("/auth/change_pass", methods=['POST'])
def change_password():
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_name = request_json["User_Id"]
            old_pass = request_json["Old_Pass"]
            new_pass = request_json["New_Pass"]
            # print(user_name, user_pass)

            status_info = dumps(cred_collection.find({"User_Id": user_name}))

            status = json.loads(status_info)

            if(len(status) == 0):
                return dumps({'error': 'User does not exist'})
            # print(status[0])
            # for j in status:
            #     print(j)
            status_pass = status[0]['User_Pass']
            # print(status_pass)
            if(old_pass == status_pass):
                cred_collection.update_one(
                    {"User_Id": user_name},
                    {
                        "$set": {"User_Pass": new_pass}
                    }
                )
                return dumps({'Success': 'Password changed'})
            else:
                return dumps({'error': 'Old Password is wrong'})
        else:
            return dumps({'error': 'Content-Type not supported'})
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "Old_PIN": "003456",
#     "New_PIN": "003546"
# }


@authenticate_blueprint.route("/auth/change_pin", methods=['POST'])
def change_pin():
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_name = request_json["User_Id"]
            old_pin = request_json["Old_PIN"]
            new_pin = request_json["New_PIN"]
            # print(user_name, user_pass)

            status_info = dumps(cred_collection.find({"User_Id": user_name}))

            status = json.loads(status_info)

            if(len(status) == 0):
                return dumps({'error': 'User does not exist'})
            # print(status[0])
            # for j in status:
            #     print(j)
            status_pass = status[0]['User_PIN']
            # print(status_pass)
            if(old_pin == status_pass):
                cred_collection.update_one(
                    {"User_Id": user_name},
                    {
                        "$set": {"User_PIN": new_pin}
                    }
                )
                return dumps({'Success': 'PIN changed'})
            else:
                return dumps({'error': 'Old PIN is wrong'})
        else:
            return dumps({'error': 'Content-Type not supported'})
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "User_Pass": "Tempayyy",
#     "User_PIN": "003546"
# }


@authenticate_blueprint.route("/auth/add_user", methods=['POST'])
def add_user():
    try:
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_name = request_json["User_Id"]

            temp = json.loads(
                dumps(cred_collection.find({"User_Id": user_name})))

            if len(temp) != 0:
                return dumps({'error': 'User already exists'})

            status = cred_collection.insert_one(request.get_json())
            client.Wallet.Balances.insert(
                {
                    "User_Id": user_name,
                    "balance": 0
                }
            )
            return dumps({'Success': 'User Added'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})
