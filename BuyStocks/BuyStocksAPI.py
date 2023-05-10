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
buy_stocks_blueprint = Blueprint('buy_ipo_equity', 'REST_API')

# pass the following info to this
# {
#     "Buyer_Id":"Amit22",
#     "PIN": "321455",
#     "Ticker_Symbol": "BSL",
#     "Units": "2"
#     "Price_Per_Unit":"234"
# }


@buy_stocks_blueprint.route("/buy_equity", methods=['POST'])
def buy_equity():
    try:
        # dataToPush = pushData('ABC', '100')
        # dataToPush = {'stock_Name': 'ABC', 'stock_Price': '100'}
        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            buyer_id = request_json["Buyer_Id"]
            buyer_pin = request_json["PIN"]
            company_to_buy = request_json["Ticker_Symbol"]
            units_to_buy = request_json["Units"]
            price_per_unit = request_json["Price_Per_Unit"]
            # print(user_name, user_pass)

            company_info = dumps(inventory_collection.find(
                {"Ticket_Symbol": company_to_buy}))

            company_entry = json.loads(company_info)

            if(len(company_entry) == 0):
                return dumps({'error': 'Company does not exist'})

            if(int(units_to_buy) < 0):
                return dumps({'error': 'Invalid value in Units'})

            status = find_sell_order(
                company_to_buy, units_to_buy, price_per_unit, buyer_id)

            if(status[0] == False):
                return dumps({'error': status[1]})

            seller_order_info = status[1]

            remaining_amount = int(
                units_to_buy) * int(int(price_per_unit) - int(seller_order_info['Price_Per_Unit']))

            total_money_sent = int(units_to_buy) * int(price_per_unit)

            user_balance = UsersWalletUtils.check_balance(buyer_id, buyer_pin)
            if user_balance[0] == False:
                return dumps({'error':  user_balance[1]})

            if int(total_money_sent) > int(user_balance[1]):
                return dumps({'error': "Buyer has insufficient funds"})

            # sending money from buyer to seller
            UsersWalletUtils.send_money(
                buyer_id, seller_order_info['Seller_Id'], buyer_pin, int(int(units_to_buy) * int(seller_order_info['Price_Per_Unit'])))

            # taking commision as difference
            UsersWalletUtils.send_money(
                buyer_id, "KuruX", buyer_pin, int(int(units_to_buy) * int(remaining_amount)))

            transfer_stock_status = transfer_stocks_buyorder(buyer_id, seller_order_info,
                                                             units_to_buy, company_to_buy, price_per_unit, company_entry[0]['Company_Name'])

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


def transfer_stocks_buyorder(buyer_id, seller_order_info, units, company_to_buy, buying_price, company_name):
    try:
        portfolio_collection = portfolio_db['Portfolio']
        buyer_user_dump = dumps(
            portfolio_collection.find({'User_Id': buyer_id}))
        seller_user_dump = dumps(portfolio_collection.find(
            {'User_Id': seller_order_info['Seller_Id']}))

        buyer_user_inf = json.loads(buyer_user_dump)
        seller_user_inf = json.loads(seller_user_dump)

        # print(seller_user_inf[0]['Stocks']['0'])

        seller_port_index = -1

        for seller_ind_stocks in seller_user_inf[0]['Stocks']:
            if seller_user_inf[0]['Stocks'][seller_ind_stocks]['Ticket_Symbol'] == company_to_buy:
                seller_port_index = seller_ind_stocks
                break
            print(seller_user_inf[0]['Stocks'][seller_ind_stocks])

        buyer_port_index = -1

        for buyer_ind_stocks in buyer_user_inf[0]['Stocks']:
            if buyer_user_inf[0]['Stocks'][buyer_ind_stocks]['Ticket_Symbol'] == company_to_buy:
                buyer_port_index = buyer_ind_stocks
                break
            print(buyer_user_inf[0]['Stocks'][buyer_ind_stocks])

        # print(buyer_port_index)

        # print("\n\n")

        # print(seller_port_index)

        seller_remaining_units = int(
            seller_order_info['Units']) - int(units)

        # print(seller_order_info)

        # removing sell order
        if seller_remaining_units != 0:
            client.Company_Sell_Order[company_to_buy].update_one(
                {"_id": ObjectId(seller_order_info['_id']['$oid'])},
                {
                    "$set": {
                        "Units": str(seller_remaining_units)
                    }
                }
            )
        else:
            client.Company_Sell_Order[company_to_buy].delete_one(
                {"_id": ObjectId(seller_order_info['_id']['$oid'])})

        # print(seller_remaining_units)

        # print(seller_user_inf[0]['Stocks'][seller_port_index])

        seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units'] = int(
            seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units']) - int(units)

        print(seller_user_inf[0]['Stocks'][seller_port_index])

        # transfering_Stocks
        portfolio_collection.update_one(
            {"User_Id": seller_order_info['Seller_Id']},
            {
                "$set": {
                    "Stocks": seller_user_inf[0]['Stocks']
                }
            }
        )

        # print(buyer_user_inf[0]['Stocks'])

        if buyer_port_index != -1:
            buyer_user_inf[0]['Stocks'][buyer_port_index]['Stock_Units'] = int(
                buyer_user_inf[0]['Stocks'][buyer_port_index]['Stock_Units']) + int(units)
        else:
            size_buyer = str(len(buyer_user_inf[0]['Stocks']))
            buyer_user_inf[0]['Stocks'][size_buyer] = {
                'Company_Name': company_name, 'Ticket_Symbol': company_to_buy, 'Stock_Units': units, 'Buying_Price': buying_price}

        # print("\n\n")
        # print(buyer_user_inf[0]['Stocks'])

        portfolio_collection.update_one(
            {"User_Id": buyer_id},
            {
                "$set": {
                    "Stocks": buyer_user_inf[0]['Stocks']
                }
            }
        )

        return [True, "Stock Transfer Done"]

    except Exception as e:
        return [False, {'error': str(e)}]


# use Company_Sell_Order.company_ticker_number to find sell order
company_seller_db = client.Company_Sell_Order


def find_sell_order(company_to_buy, units_to_buy, price_per_unit, buyer_id):
    try:
        sell_order_collection = company_seller_db[company_to_buy]
        sell_order_inf = dumps(sell_order_collection.find())

        company_entry = json.loads(sell_order_inf)

        if(int(units_to_buy) < 0):
            return dumps({'error': 'Invalid value in Units'})

        chosen_sell_order = []
        current_price_min = sys.maxsize

        for ind_sell_order in company_entry:
            if int(ind_sell_order['Price_Per_Unit']) < int(current_price_min):

                if int(ind_sell_order['Units']) == int(units_to_buy):
                    chosen_sell_order = ind_sell_order
                    current_price_min = ind_sell_order['Price_Per_Unit']

                if int(ind_sell_order['Is_Owner']) == int(1):
                    chosen_sell_order = ind_sell_order
                    current_price_min = ind_sell_order['Price_Per_Unit']

        if(chosen_sell_order == [] or int(chosen_sell_order['Units']) < int(units_to_buy) or int(chosen_sell_order['Price_Per_Unit']) > int(price_per_unit)):
            add_buy_order(company_to_buy, price_per_unit,
                          units_to_buy, buyer_id)
            return [False, "No Sell order found , the order will be executed when a buyer arrives"]

        # print(chosen_sell_order)

        return [True, chosen_sell_order]

    except Exception as e:
        return dumps({'error': str(e)})


# adding buy order in buy order table
company_buyer_db = client.Company_Buy_Order


def add_buy_order(company_to_buy, price_per_unit, units_to_buy, buyer_id):
    try:
        buy_order_collection = company_buyer_db[company_to_buy]
        buy_order_inf = dumps(buy_order_collection.find())

        status = buy_order_collection.insert_one(
            {
                "Units": units_to_buy,
                "Price_Per_Unit": price_per_unit,
                "Buyer_Id": buyer_id
            }
        )
    except Exception as e:
        return dumps({'error': str(e)})
