import sys
from flask import request
from pymongo import MongoClient
from bson.json_util import dumps
import json
from Auth.AuthenticateAPI import check_pin
from env import *
from RestClientHelper.ClientConnectionHelper import *
from flask import Blueprint
from Wallet import UsersWalletUtils
from unique_id_generator import unique_id_generator


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
#     "Units": "2",
#     "Price_Per_Unit":"234"
# }


@buy_stocks_blueprint.route("/equity/buy_equity", methods=['POST'])
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
            units_to_buy = int(request_json["Units"])
            price_per_unit = int(request_json["Price_Per_Unit"])
            # print(user_name, user_pass)

            if not check_pin(buyer_id, buyer_pin)[0]:
                return dumps({'error': 'Pin entered is wrong'})

            company_info = dumps(inventory_collection.find(
                {"Ticker_Symbol": company_to_buy}))

            company_entry = json.loads(company_info)

            if(len(company_entry) == 0):
                return dumps({'error': 'Company does not exist'})

            if(int(units_to_buy) < 0):
                return dumps({'error': 'Invalid value in Units'})

            total_money_spent = int(units_to_buy) * int(price_per_unit)

            user_balance = UsersWalletUtils.check_balance(buyer_id, buyer_pin)
            if user_balance[0] == False:
                return dumps({'error':  user_balance[1]})

            if int(total_money_spent) > int(user_balance[1]):
                return dumps({'error': "Buyer has insufficient funds"})

            status = find_sell_order(
                company_to_buy, units_to_buy, price_per_unit, buyer_id, buyer_pin)

            if(status[0] == False):
                return dumps({'error': status[1]})

            seller_order_info = status[1]

            money_to_send_to_buyer = int(
                units_to_buy) * int(seller_order_info['Price_Per_Unit'])

            # send money to intermediary account
            UsersWalletUtils.send_money(
                buyer_id, "KuruX", buyer_pin, total_money_spent)

            # sending money from intermediary to seller
            UsersWalletUtils.send_money(
                "KuruX", seller_order_info['Seller_Id'], "379009", money_to_send_to_buyer)

            transfer_stock_status = transfer_stocks_buyorder(buyer_id, seller_order_info,
                                                             units_to_buy, company_to_buy, price_per_unit, company_entry[0]['Company_Name'], total_money_spent)

            if(transfer_stock_status[0] == False):
                return dumps(transfer_stock_status[1])
            # print(status[0])
            # for j in status:
            #     print(j)
            # print(status_pass)

            return dumps({'msg': transfer_stock_status[1]})

        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})


def transfer_stocks_buyorder(buyer_id, seller_order_info, units, company_to_buy, buying_price, company_name, total_spent):
    try:

        buyer_user_dump = dumps(
            client[buyer_id]['Portfolio'].find({'Ticker_Symbol': company_to_buy}))

        buyer_user_inf = json.loads(buyer_user_dump)

        # print(seller_user_inf[0]['Stocks']['0'])
        # print(seller_port_index)

        seller_remaining_units = int(
            seller_order_info['Units']) - int(units)

        # print(seller_order_info)

        # removing sell order
        seller_order_id = seller_order_info['_id']
        if seller_remaining_units != 0:

            client[seller_order_info['Seller_Id']]['Sell_Order'].update_one(
                {"_id": seller_order_id},
                {
                    "$set": {
                        "Units": seller_remaining_units
                    }
                }
            )

            client.Company_Sell_Order[company_to_buy].update_one(
                {"_id": seller_order_id},
                {
                    "$set": {
                        "Units": seller_remaining_units
                    }
                }
            )
        else:
            client[seller_order_info['Seller_Id']]['Sell_Order'].delete_one(
                {"_id": seller_order_id}
            )
            client.Company_Sell_Order[company_to_buy].delete_one(
                {"_id": seller_order_id}
            )

        # print(seller_remaining_units)

        # print(seller_user_inf[0]['Stocks'][seller_port_index])

        # dont subtract stocks from Seller
        # seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units'] = int(
        #     seller_user_inf[0]['Stocks'][seller_port_index]['Stock_Units']) - int(units)

        # print(seller_user_inf[0]['Stocks'][seller_port_index])

        # # transfering_Stocks
        # portfolio_collection.update_one(
        #     {"User_Id": seller_order_info['Seller_Id']},
        #     {
        #         "$set": {
        #             "Stocks": seller_user_inf[0]['Stocks']
        #         }
        #     }
        # )

        # print(buyer_user_inf[0]['Stocks'])

        # Transfering stock
        if len(buyer_user_inf) != 0:
            client[buyer_id]['Portfolio'].update_one(
                {"Ticker_Symbol": company_to_buy},
                {
                    "$inc": {"Units": units}
                }
            )
        else:
            client[buyer_id]['Portfolio'].insert_one(
                {
                    "Company_Name": company_name,
                    "Ticker_Symbol": company_to_buy,
                    "Units": units
                }
            )

        # add order_history
        client[buyer_id]['Order_History'].insert_one(
            {
                "Ticker_Symbol": company_to_buy,
                "Type": "Buy_Order",
                "Units": units,
                "Price_Per_Unit": buying_price
            }
        )

        client[seller_order_info['Seller_Id']]['Order_History'].insert_one(
            {
                "Ticker_Symbol": company_to_buy,
                "Type": "Sell_Order",
                "Units": units,
                "Price_Per_Unit": seller_order_info['Price_Per_Unit']
            }
        )

        return [True, "Stock Transfer Done"]

    except Exception as e:
        return [False, {'error': str(e)}]


# use Company_Sell_Order.company_ticker_number to find sell order
company_seller_db = client.Company_Sell_Order


def find_sell_order(company_to_buy, units_to_buy, price_per_unit, buyer_id, buyer_pin):
    try:
        sell_order_collection = company_seller_db[company_to_buy]
        sell_order_inf = dumps(sell_order_collection.find())

        company_entry = json.loads(sell_order_inf)

        if(int(units_to_buy) < 0):
            return [False, "Invalid value in Units"]

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
                          units_to_buy, buyer_id, buyer_pin)
            return [False, "No Sell order found , the order will be executed when a buyer arrives"]

        # print(chosen_sell_order)

        return [True, chosen_sell_order]

    except Exception as e:
        return dumps({'error': str(e)})


# adding buy order in buy order table
company_buyer_db = client.Company_Buy_Order


def add_buy_order(company_to_buy, price_per_unit, units_to_buy, buyer_id, buyer_pin):
    try:
        buy_order_collection = company_buyer_db[company_to_buy]

        id_stat = unique_id_generator.give_new_unique_id()

        if id_stat[0] != False:

            buy_order_collection.insert_one(
                {
                    "_id": id_stat[1],
                    "Units": units_to_buy,
                    "Price_Per_Unit": price_per_unit,
                    "Buyer_Id": buyer_id
                }
            )

            client[buyer_id].Buy_Order.insert_one(
                {
                    "_id": id_stat[1],
                    "Units": units_to_buy,
                    "Price_Per_Unit": price_per_unit,
                    "Buyer_Id": buyer_id,
                    "Ticker_Symbol": company_to_buy
                }
            )

        # sending money from user to Intermediate Wallet ( so that it can be used for fulfillment of order)
            UsersWalletUtils.send_money(
                buyer_id, "Intermediate", buyer_pin, int(int(units_to_buy) * int(price_per_unit)))
        return [True, "Success"]

    except Exception as e:
        return dumps({'error': str(e)})
