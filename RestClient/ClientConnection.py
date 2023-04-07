from flask import Flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
import json
from env import *
from DBUtil.pushDataUtil import dataToPush
from RestClientHelper.ClientConnectionHelper import *
from flask import Blueprint

client = MongoClient(mongoClient)
db = client.INVENTORY

query_blueprint = Blueprint('queries', 'REST_API')

# pushing a company info into Mongo Collection


@query_blueprint.route("/add_query", methods=['POST'])
def push_Data():
    data_loader = json.loads(request.data)
    dataToPush = dataToPush({'ABC', '100'})
    add_information(db.LISTED_STOCKS, dataToPush)
