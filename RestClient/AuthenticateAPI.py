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
cred_db = client.Users
cred_collection = cred_db.User_cred

authenticate_blueprint = Blueprint('authenticate', 'REST_API')

# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "User_Pass": "Alien321"
# }


@authenticate_blueprint.route("/auth", methods=['POST'])
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
                return dumps({'auth': 'FAIL'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})
