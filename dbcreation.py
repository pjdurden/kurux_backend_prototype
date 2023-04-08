from pymongo import MongoClient
from env import mongoClient
import sample_Company_Data
import json
from bson.json_util import dumps
from glob import glob
import os

ROOT_DIR = os.path.dirname(os.path.realpath('__file__'))

client = MongoClient(mongoClient)

company_db = client["INVENTORY"]
company_collection = company_db["LISTED_STOCKS"]

# adding data to the newly created table


company_collection.create_index(
    [('Ticket_Symbol', 1)], name='Ticket_Symbol', unique=True, sparse=True)


def add_data_companies():
    try:

        # print(ROOT_DIR)
        json_dir_name = '/sample_Company_Data'
        json_pattern = os.path.join(ROOT_DIR + json_dir_name, "*.json")
        # print(json_pattern)
        filelist = glob(json_pattern)
        # print(filelist)
        for filename in filelist:
            with open(filename) as f:
                file_data = json.load(f)
                # print(file_data)
                status = company_collection.insert_one(file_data)
        print({'insert': 'SUCCESS'})

    except Exception as e:
        print({'error': str(e)})


user_db = client["Users"]
user_collection = user_db["Portfolio"]
user_collection.create_index(
    [('User_Id', 1)], name='User_Id', unique=True, sparse=True)


def add_user_data():
    try:
        # print(ROOT_DIR)
        json_dir_name = '/sample_User_Data'
        json_pattern = os.path.join(ROOT_DIR + json_dir_name, "*.json")
        # print(json_pattern)
        filelist = glob(json_pattern)
        # print(filelist)
        for filename in filelist:
            with open(filename) as f:
                file_data = json.load(f)
                # print(file_data)
                status = user_collection.insert_one(file_data)
        print({'insert': 'SUCCESS'})

    except Exception as e:
        print({'error': str(e)})


add_data_companies()
add_user_data()
print(client.list_database_names())
