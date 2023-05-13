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
cred_db = client.INVENTORY
cred_collection = cred_db.ID_Generator


def give_new_unique_id():
    try:
        if json.loads(dumps(cred_collection.find())) == []:
            cred_collection.insert(
                {
                    "_id": "Unique_Count_Document_Identifier",
                    "COUNT": 2
                }
            )
            return 1
        else:

            temp = cred_collection.find_and_modify(
                {"_id": "Unique_Count_Document_Identifier"},
                {
                    "$inc": {"COUNT": 1}
                }
            )
            return [True, temp['COUNT']]
    except Exception as e:
        return [False, "Unable to generate unique id mongo error"]
