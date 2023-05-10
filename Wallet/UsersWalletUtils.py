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
cred_collection = cred_db.User_balance

# pass the following info to this , amount should only be integer
# {
#     "Snd_Acc_ID":"Amit22",
#     "Rcv_Acc_ID": "Alien321",
#     "Amount":"22"
# }


def send_money(sender_addr, reciever_addr, sender_pin, amount):
    try:

        sender = json.loads(
            dumps(cred_collection.find({"User_Id": sender_addr})))

        if(len(sender) == 0):
            return [False, "Sender Address does not exist"]
        if(sender[0]['PIN'] != sender_pin):
            return [False, "Pin is wrong"]

        reciever = json.loads(
            dumps(cred_collection.find({"User_Id": reciever_addr})))
        if(len(reciever) == 0):
            return [False, "Reciever Address does not exist"]

        if(amount < 0):
            return [False, "Invalid amount"]

        # print(sender[0]['balance'])

        if (int(sender[0]['balance']) < int(amount)):
            return [False, str("sender: "+sender_addr + " doesnt have enough balance")]

        # print(reciever[0]['balance'])

        final_balance_sender: int = int(sender[0]['balance']) - int(amount)
        final_balance_reciever: int = int(reciever[0]['balance']) + int(amount)

        cred_collection.update_one(
            {"User_Id": sender_addr},
            {
                "$set": {
                    "balance": str(final_balance_sender)
                }
            }
        )

        cred_collection.update_one(
            {"User_Id": reciever_addr},
            {
                "$set": {
                    "balance": str(final_balance_reciever)
                }
            }
        )
        return [True, "Transaction Success"]
    except Exception as e:
        return [False, "Unable to do Transaction mongo error"]


def check_balance(addr, pin):
    try:
        addr_inf = json.loads(dumps(cred_collection.find({"User_Id": addr})))
        if(len(addr_inf) == 0):
            return [False, "User Does not Exist"]
        # print(addr_inf)
        # print(pin)
        if(addr_inf[0]['PIN'] != pin):
            return [False, "Pin is wrong"]
        return [True, addr_inf[0]['balance']]

    except:
        return [False, "Unable to fetch balance mongo error"]
