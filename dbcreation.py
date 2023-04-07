from pymongo import MongoClient
from env import mongoClient
import sample_Company_Data
import json
from bson.json_util import dumps
from glob import glob
import os


client = MongoClient(mongoClient)

new_db = client["INVENTORY"]
new_collection = new_db["LISTED_STOCKS"]

# adding data to the newly created table


def add_data():
    try:

        ROOT_DIR = os.path.dirname(os.path.realpath('__file__'))
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
                status = new_collection.insert_one(file_data)
        print({'insert': 'SUCCESS'})

    except Exception as e:
        print({'error': str(e)})


# add_data()
print(client.list_database_names())
