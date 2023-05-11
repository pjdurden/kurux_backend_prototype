import sys
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
from bson.objectid import ObjectId


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


@sell_stocks_blueprint.route("/sell_equity", methods=['POST'])
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
            units_to_sell = request_json["Units"]
            price_per_unit = request_json["Price_Per_Unit"]
            # print(user_name, user_pass)

            company_info = dumps(inventory_collection.find(
                {"Ticket_Symbol": company_to_sell}))

            company_entry = json.loads(company_info)

            if(len(company_entry) == 0):
                return dumps({'error': 'Company does not exist'})

            if(int(units_to_sell) < 0):
                return dumps({'error': 'Invalid value in Units'})

            is_owner = (company_entry[0]['Owner'] == seller_id)

            status = find_buy_order(
                company_to_sell, units_to_sell, price_per_unit, seller_id, is_owner)

            if(status[0] == False):
                return dumps({'error': status[1]})

            buyer_order_info = status[1]

            amount_to_transfer = int(units_to_sell) * int(price_per_unit)

            # sending money
            UsersWalletUtils.send_money(
                "KuruX", seller_id, "003579", amount_to_transfer)

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
        portfolio_collection = portfolio_db['Portfolio']
        seller_user_dump = dumps(
            portfolio_collection.find({'User_Id': seller_id}))
        buyer_user_dump = dumps(portfolio_collection.find(
            {'User_Id': buyer_order_info['Buyer_Id']}))

        seller_user_inf = json.loads(seller_user_dump)
        buyer_user_inf = json.loads(buyer_user_dump)

        # print(seller_user_inf[0]['Stocks']['0'])

        buyer_port_index = -1

        for buyer_ind_stocks in buyer_user_inf[0]['Stocks']:
            if buyer_user_inf[0]['Stocks'][buyer_ind_stocks]['Ticket_Symbol'] == company_to_sell:
                buyer_port_index = buyer_ind_stocks
                break
            print(buyer_user_inf[0]['Stocks'][buyer_ind_stocks])

        seller_port_index = -1

        for seller_ind_stocks in seller_user_inf[0]['Stocks']:
            if seller_user_inf[0]['Stocks'][seller_ind_stocks]['Ticket_Symbol'] == company_to_sell:
                seller_port_index = seller_ind_stocks
                break
            print(seller_user_inf[0]['Stocks'][seller_ind_stocks])

        # print(buyer_port_index)

        # print("\n\n")

        # print(seller_port_index)

        # print(seller_order_info)

        # removing buy order
        client.Company_Buy_Order[company_to_sell].delete_one(
            {"_id": ObjectId(buyer_order_info['_id']['$oid'])})

        # print(seller_remaining_units)

        # print(seller_user_inf[0]['Stocks'][seller_port_index])

        buying_price = buyer_order_info['Price_Per_Unit']

        if buyer_port_index != -1:
            buyer_user_inf[0]['Stocks'][buyer_port_index]['Stock_Units'] = int(
                buyer_user_inf[0]['Stocks'][buyer_port_index]['Stock_Units']) + int(units)
        else:
            size_buyer = str(len(buyer_user_inf[0]['Stocks']))
            buyer_user_inf[0]['Stocks'][size_buyer] = {
                'Company_Name': company_name, 'Ticket_Symbol': company_to_sell, 'Stock_Units': units, 'Buying_Price': buying_price}
        portfolio_collection.update_one(
            {"User_Id": buyer_order_info['Buyer_Id']},
            {
                "$set": {
                    "Stocks": buyer_user_inf[0]['Stocks']
                }
            }
        )

        remove_stock_seller(seller_id, units, company_to_sell)

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
        current_price_min = -sys.maxsize + 1

        for ind_buy_order in company_entry:
            if int(ind_buy_order['Price_Per_Unit']) > int(current_price_min):

                if int(ind_buy_order['Units']) == int(units_to_sell):
                    chosen_buy_order = ind_buy_order
                    current_price_min = ind_buy_order['Price_Per_Unit']

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
        sell_order_collection = company_seller_db[company_to_sell]

        sell_capacity = check_company_units_in_portfolio(
            seller_id, company_to_sell)

        if int(sell_capacity[1]) < int(units_to_sell):
            return [False, "User Doesn't have enough Units to sell"]

        status = sell_order_collection.insert_one(
            {
                "Units": units_to_sell,
                "Price_Per_Unit": price_per_unit,
                "Seller_Id": seller_id,
                "Is_Owner": int(is_owner)

            }
        )

        seller_user_inf = json.loads(
            dumps(client.Users.Portfolio.find({'User_Id': seller_id})))

        seller_port_index = sell_capacity[2]

        seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units'] = int(
            seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units']) - int(units_to_sell)

        temp = {}

        counter: int = 0

        print(type(seller_user_inf[0]['Stocks']))

        # print(type(seller_user_inf['Stocks']))

        for seller_ind in seller_user_inf[0]['Stocks']:
            if int(seller_user_inf[0]['Stocks'][seller_ind]['Stock_Units']) != 0:
                print(seller_user_inf[0]['Stocks'][seller_ind])
                temp[str(counter)] = seller_user_inf[0]['Stocks'][seller_ind]
                counter += 1
            print(seller_ind)

        # updating portfolio
        client.Users.Portfolio.update_one(
            {"User_Id": seller_id},
            {
                "$set": {
                    "Stocks": temp
                }
            }
        )

        return [True, "Sell Order Added"]
    except Exception as e:
        return [False, {'error': str(e)}]


def remove_stock_seller(seller_id, units_to_sell, company_to_sell):
    try:
        # remove Stocks from Seller portfolio
        seller_user_inf = json.loads(
            dumps(client.Users.Portfolio.find({'User_Id': seller_id})))
        sell_capacity = check_company_units_in_portfolio(
            seller_id, company_to_sell)

        seller_port_index = sell_capacity[2]

        seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units'] = int(
            seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units']) - int(units_to_sell)

        temp = {}

        counter: int = 0

        print(type(seller_user_inf[0]['Stocks']))

        # print(type(seller_user_inf['Stocks']))

        for seller_ind in seller_user_inf[0]['Stocks']:
            if int(seller_user_inf[0]['Stocks'][seller_ind]['Stock_Units']) != 0:
                print(seller_user_inf[0]['Stocks'][seller_ind])
                temp[str(counter)] = seller_user_inf[0]['Stocks'][seller_ind]
                counter += 1
            print(seller_ind)

        # updating portfolio
        client.Users.Portfolio.update_one(
            {"User_Id": seller_id},
            {
                "$set": {
                    "Stocks": temp
                }
            }
        )
        return [True, "Success"]
    except Exception as e:
        return [False, {'error': str(e)}]


def check_company_units_in_portfolio(user_id, company_id):
    try:
        portfolio_collection = portfolio_db['Portfolio']
        user_dump = dumps(
            portfolio_collection.find({'User_Id': user_id}))

        user_inf = json.loads(user_dump)

        # print(user_inf[0]['Stocks']['0'])

        port_index = -1

        for ind_stocks in user_inf[0]['Stocks']:
            if user_inf[0]['Stocks'][ind_stocks]['Ticket_Symbol'] == company_id:
                port_index = ind_stocks
                break
            # print(user_inf[0]['Stocks'][ind_stocks])

        result = 0

        if port_index != -1:
            result = user_inf[0]['Stocks'][ind_stocks]['Stock_Units']

        return [True, result, port_index]
    except Exception as e:
        return [False, {'error': str(e)}]
