import sys
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
from Wallet import UsersWalletUtils
from bson.objectid import ObjectId

from unique_id_generator.unique_id_generator import give_new_unique_id


client = MongoClient(mongoClient)
user_db = client.Users
user_collection = user_db.User_balance

temp = 'LISTED_STOCKS'

inventory_db = client.INVENTORY
inventory_collection = inventory_db[temp]
sell_stocks_blueprint = Blueprint('sell_ipo_equity', 'REST_API')

# pass the following info to this
# {
#     "Seller_Id":"Amit22",
#     "PIN": "321455",
#     "Ticker_Symbol": "BSL",
#     "Units": "2"
#     "Price_Per_Unit":"234"
# }


@sell_stocks_blueprint.route("/equity/sell_equity", methods=['POST'])
def sell_equity():
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            seller_id = request_json["Seller_Id"]
            seller_pin = request_json["PIN"]
            company_to_sell = request_json["Ticker_Symbol"]
            units_to_sell = int(request_json["Units"])
            price_per_unit = int(request_json["Price_Per_Unit"])
            # print(user_name, user_pass)

            if not check_pin(seller_id, seller_pin)[0]:
                return dumps({'error': 'Pin entered is wrong'})

            company_info = dumps(inventory_collection.find(
                {"Ticker_Symbol": company_to_sell}))

            company_entry = json.loads(company_info)

            if(len(company_entry) == 0):
                return dumps({'error': 'Company does not exist'})

            if(int(units_to_sell) < 0):
                return dumps({'error': 'Invalid value in Units'})

            portfolio_details = json.loads(
                dumps(client[seller_id]['Portfolio'].find({"Ticker_Symbol": company_to_sell})))

            if len(portfolio_details) == 0 or int(portfolio_details[0]['Units']) < units_to_sell:
                return dumps({'error': "User does not have enough equity units to sell"})

            is_owner = (company_entry[0]['Owner'] == seller_id)

            status = find_buy_order(
                company_to_sell, units_to_sell, price_per_unit, seller_id, is_owner)

            if(status[0] == False):
                return dumps({'error': status[1]})

            buyer_order_info = status[1]

            amount_to_transfer = int(units_to_sell) * int(price_per_unit)

            # sending money
            UsersWalletUtils.send_money(
                "Intermediate", seller_id, "8008135", amount_to_transfer)

            transfer_stock_status = transfer_stocks_sellorder(seller_id, buyer_order_info,
                                                              units_to_sell, company_to_sell, price_per_unit, company_entry[0]['Company_Name'])

            if(transfer_stock_status[0] == False):
                return transfer_stock_status[1]
            # print(status[0])
            # for j in status:
            #     print(j)
            # print(status_pass)

            return transfer_stock_status[1]

        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


portfolio_db = client.Users


def transfer_stocks_sellorder(seller_id, buyer_order_info, units, company_to_sell, selling_price, company_name):
    try:

        buyer_id = buyer_order_info['Buyer_Id']

        buyer_user_dump = dumps(
            client[buyer_id]['Portfolio'].find({'Ticker_Symbol': company_to_sell}))

        buyer_user_inf = json.loads(buyer_user_dump)

        seller_user_dump = dumps(
            client[seller_id]['Portfolio'].find(
                {"Ticker_Symbol": company_to_sell})
        )
        seller_user_inf = json.loads(seller_user_dump)

        # remove buy order
        client.Company_Buy_Order[company_to_sell].delete_one(
            {
                "_id": buyer_order_info['_id']
            }
        )

        client[buyer_id].Buy_Order.delete_one(
            {
                "_id": buyer_order_info['_id']
            }
        )

        # Transfering stock

        # increasing stock Buyer
        money_spent = int(units * buyer_order_info['Price_Per_Unit'])
        if len(buyer_user_inf) != 0:
            client[buyer_id]['Portfolio'].update_one(
                {"Ticker_Symbol": company_to_sell},
                {
                    "$inc": {"Units": units}
                }
            )
        else:
            client[buyer_id]['Portfolio'].insert_one(
                {
                    "Company_Name": company_name,
                    "Ticker_Symbol": company_to_sell,
                    "Units": units
                }
            )

        # decreasing stock seller
        seller_portfolio_units = seller_user_inf[0]['Units']
        if seller_portfolio_units == units:
            client[seller_id]['Portfolio'].delete_one(
                {
                    "Ticker_Symbol": company_to_sell
                }
            )
        else:
            client[seller_id]['Portfolio'].update_one(
                {"Ticker_Symbol": company_to_sell},
                {
                    "$inc": {"Units": -units}
                }
            )

        # adding order_history
        client[buyer_id]['Order_History'].insert_one(
            {
                "Ticker_Symbol": company_to_sell,
                "Type": "Buy_Order",
                "Units": units,
                "Price_Per_Unit": buyer_order_info['Price_Per_Unit']
            }
        )

        client[seller_id]['Order_History'].insert_one(
            {
                "Ticker_Symbol": company_to_sell,
                "Type": "Sell_Order",
                "Units": units,
                "Price_Per_Unit": selling_price
            }
        )

        return [True, "Stock Transfer Done"]

    except Exception as e:
        return [False, {'error': str(e)}]


# use Company_Buy_Order.company_ticker_number to find buy order
company_buy_db = client.Company_Buy_Order


def find_buy_order(company_to_sell, units_to_sell, price_per_unit, seller_id, is_owner):
    try:
        buy_order_collection = company_buy_db[company_to_sell]
        buy_order_inf = dumps(buy_order_collection.find())

        company_entry = json.loads(buy_order_inf)

        if(int(units_to_sell) < 0):
            return [False, "Invalid value in Units"]

        chosen_buy_order = []
        current_price_max = -sys.maxsize + 1

        for ind_buy_order in company_entry:
            # print(ind_buy_order)
            if int(ind_buy_order['Price_Per_Unit']) > int(current_price_max):

                if int(ind_buy_order['Units']) == int(units_to_sell):
                    chosen_buy_order = ind_buy_order
                    current_price_max = ind_buy_order['Price_Per_Unit']

        if(chosen_buy_order == [] or int(chosen_buy_order['Units']) < int(units_to_sell) or int(chosen_buy_order['Price_Per_Unit']) < int(price_per_unit)):
            status = add_sell_order(company_to_sell, price_per_unit,
                                    units_to_sell, seller_id, is_owner)
            if not status[0]:
                return [False, status[1]]
            return [False, "No Buy order found , the order will be executed when a seller arrives"]

        # print(chosen_sell_order)

        return [True, chosen_buy_order]

    except Exception as e:
        return dumps({'error': str(e)})


# adding buy order in buy order table
company_seller_db = client.Company_Sell_Order


def add_sell_order(company_to_sell, price_per_unit, units_to_sell, seller_id, is_owner):
    try:

        # remove stock from portfolio
        status_port = json.loads(
            dumps(client[seller_id]['Portfolio'].find({"Ticker_Symbol": company_to_sell})))

        money_recieved = -(price_per_unit * units_to_sell)

        decrement_stocks = -units_to_sell
        # print(status_port[0]['Units'])
        if int(status_port[0]['Units']) == units_to_sell:
            client[seller_id]['Portfolio'].delete_one(
                {"Ticker_Symbol": company_to_sell})
        else:
            client[seller_id]['Portfolio'].update_one(
                {"Ticker_Symbol": company_to_sell},
                {
                    "$inc": {"Units": decrement_stocks}
                }
            )

        id_stat = give_new_unique_id()

        # add sell order
        if id_stat[0] != False:

            client.Company_Sell_Order[company_to_sell].insert_one(
                {
                    "_id": id_stat[1],
                    "Units": units_to_sell,
                    "Price_Per_Unit": price_per_unit,
                    "Seller_Id": seller_id,
                    "Is_Owner": is_owner

                }
            )

            client[seller_id].Sell_Order.insert_one(
                {
                    "_id": id_stat[1],
                    "Units": units_to_sell,
                    "Price_Per_Unit": price_per_unit,
                    "Seller_Id": seller_id,
                    "Is_Owner": is_owner,
                    "Ticker_Symbol": company_to_sell
                }
            )

        return [True, "Sell Order Added"]
    except Exception as e:
        return [False, {'error': str(e)}]
