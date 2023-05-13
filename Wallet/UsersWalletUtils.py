from flask import Flask
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
import json
from Auth.AuthenticateAPI import check_pin
from env import *
from DBUtil.pushDataUtil import pushData
from RestClientHelper.ClientConnectionHelper import *
from flask import Blueprint

client = MongoClient(mongoClient)
cred_db = client.Wallet
wallet_collection = cred_db.Balances

# pass the following info to this , amount should only be integer
# {
#     "Snd_Acc_ID":"Amit22",
#     "Rcv_Acc_ID": "Alien321",
#     "Amount":"22"
# }


def send_money(sender_addr, reciever_addr, sender_pin, amount):
    try:

        status = check_pin(sender_addr, sender_pin)
        if not status[0]:
            return [False, status[1]]

        reciever = json.loads(
            dumps(client.Auth.Auth_details.find({"User_Id": reciever_addr})))
        if(len(reciever) == 0):
            return [False, "Reciever Address does not exist"]

        if(int(amount) < 0):
            return [False, "Invalid amount"]

        # print(sender[0]['balance'])

        sender_wallet_inf = json.loads(
            dumps(wallet_collection.find({"User_Id": sender_addr})))

        reciever_wallet_inf = json.loads(dumps(wallet_collection.find(
            {"User_Id": reciever_addr})))

        if (int(sender_wallet_inf[0]['balance']) < int(amount)):
            return [False, str("sender: "+sender_addr + " doesnt have enough balance")]

        # print(reciever[0]['balance'])

        final_balance_sender: int = int(
            sender_wallet_inf[0]['balance']) - int(amount)
        final_balance_reciever: int = int(
            reciever_wallet_inf[0]['balance']) + int(amount)

        wallet_collection.update_one(
            {"User_Id": sender_addr},
            {
                "$set": {
                    "balance": final_balance_sender
                }
            }
        )

        wallet_collection.update_one(
            {"User_Id": reciever_addr},
            {
                "$set": {
                    "balance": final_balance_reciever
                }
            }
        )

        # add transaction history
        client[sender_addr]['Tran_History'].insert(
            {
                "User_Id": sender_addr,
                "Amount": int(amount),
                "Type": "Sent",
                "Message": "Sent money to "+str(reciever_addr)
            }
        )
        client[reciever_addr]['Tran_History'].insert(
            {
                "User_Id": reciever_addr,
                "Amount": int(amount),
                "Type": "Recieved",
                "Message": "Recieved money from "+str(sender_addr)
            }
        )
        return [True, "Transaction Success"]
    except Exception as e:
        return [False, "Unable to do Transaction mongo error"]


def check_balance(addr, pin):
    try:
        status = check_pin(addr, pin)
        if not status[0]:
            return [False, status[1]]
        addr_inf = json.loads(dumps(wallet_collection.find({"User_Id": addr})))
        if(len(addr_inf) == 0):
            return [False, "User Does not Exist"]
        # print(addr_inf)
        # print(pin)
        return [True, addr_inf[0]['balance']]

    except:
        return [False, "Unable to fetch balance mongo error"]


def add_money(addr, pin, amount, master_pass):
    try:

        status = check_pin(addr, pin)
        if not status[0]:
            return [False, status[1]]

        if master_pass != "M4ST3R9A55":
            return [False, "Master pass is wrong"]

        if(int(amount) < 0):
            return [False, "Invalid amount"]

        # print(sender[0]['balance'])

        sender_wallet_inf = json.loads(
            dumps(wallet_collection.find({"User_Id": addr})))
        # print(reciever[0]['balance'])

        final_balance_sender: int = int(
            sender_wallet_inf[0]['balance']) + int(amount)

        wallet_collection.update_one(
            {"User_Id": addr},
            {
                "$set": {
                    "balance": final_balance_sender
                }
            }
        )

        # add transaction history
        client[addr]['Tran_History'].insert(
            {
                "User_Id": addr,
                "Amount": int(amount),
                "Type": "Recieved",
                "Message": "added money into wallet"
            }
        )

        return [True, "Money Added"]
    except Exception as e:
        return [False, "Unable to do Transaction mongo error"]
