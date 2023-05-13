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

cancel_orders_blueprint = Blueprint('cancel_orders', 'REST_API')

client = MongoClient(mongoClient)


# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "PIN": "5432122",
#     "Order_Id":"4"
# }
@cancel_orders_blueprint.route("/cancel/buy_order", methods=['POST'])
def cancel_buy_order():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]
            user_pin = request_json["PIN"]
            order_id = int(request_json["Order_Id"])

            if not UsersWalletUtils.check_pin(user_id, user_pin)[0]:
                return dumps({'error': 'Pin is Wrong'})

            temp = json.loads(
                dumps(client[user_id].Buy_Order.find({"_id": order_id})))
            if len(temp) != 0:
                money_to_refund = int(
                    temp[0]['Price_Per_Unit']*temp[0]['Units'])
                company_name = temp[0]['Ticker_Symbol']
                UsersWalletUtils.send_money(
                    "Intermediate", user_id, "8008135", money_to_refund)

                client[user_id].Buy_Order.delete_one({"_id": order_id})
                client.Company_Buy_Order[company_name].delete_one(
                    {"_id": order_id})
                return dumps('Order cancelled')

            return dumps({'error': 'Order does not exist'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "User_Id":"Amit22",
#     "PIN": "5432122",
#     "Order_Id":"4"
# }


@cancel_orders_blueprint.route("/cancel/sell_order", methods=['POST'])
def cancel_sell_order():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            user_id = request_json["User_Id"]
            user_pin = request_json["PIN"]
            order_id = request_json["Order_Id"]

            if not UsersWalletUtils.check_pin(user_id, user_pin)[0]:
                return dumps({'error': 'Pin is Wrong'})

            temp = json.loads(
                dumps(client[user_id].Sell_Order.find({"_id": order_id})))
            if len(temp) != 0:
                units_to_refund = int(temp[0]['Units'])
                company_ticker = temp[0]['Ticker_Symbol']

                money_to_add_in_total_spent = int(
                    temp[0]['Price_Per_Unit']*temp[0]['Units'])

                # Transfering stock
                refund_user_dump = dumps(
                    client[user_id]['Portfolio'].find({'Ticker_Symbol': company_ticker}))

                company_info = dumps(client.INVENTORY.LISTED_STOCKS.find(
                    {"Ticker_Symbol": company_ticker}))
                refund_user_inf = json.loads(refund_user_dump)
                company_entry = json.loads(company_info)
                company_name = company_entry[0]['Company_Name']

                if len(refund_user_inf) != 0:
                    client[user_id]['Portfolio'].update_one(
                        {"Ticker_Symbol": company_ticker},
                        {
                            "$inc": {"Units": units_to_refund}
                        }
                    )
                else:
                    client[user_id]['Portfolio'].insert_one(
                        {
                            "Company_Name": company_name,
                            "Ticker_Symbol": company_ticker,
                            "Units": units_to_refund
                        }
                    )

                client[user_id].Sell_Order.delete_one({"_id": order_id})
                client.Company_Sell_Order[company_ticker].delete_one(
                    {"_id": order_id})
                return dumps('Order Cancelled')

            return dumps({'error': 'Order does not exist'})
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "Ticker_Symbol":"BSL"
# }


@cancel_orders_blueprint.route("/price/avg_buy_price", methods=['POST'])
def avg_buy_price():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            ticker_symbol = request_json["Ticker_Symbol"]

            ipeo_price = json.loads(
                dumps(client.INVENTORY.LISTED_STOCKS.find({"Ticker_Symbol": ticker_symbol})))

            all_buy_orders = json.loads(
                dumps(client.Company_Buy_Order[ticker_symbol].find()))

            total_price: int = int(ipeo_price[0]['IPEO_Price'])
            total_div: int = 1

            for ind_buy_order in all_buy_orders:
                total_price += int(ind_buy_order['Price_Per_Unit']
                                   * ind_buy_order['Units'])
                total_div += int(ind_buy_order['Units'])
                # print(ind_buy_order)

                # temp = json.loads(

            return dumps(total_price/total_div)
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})

# pass the following info to this
# {
#     "Ticker_Symbol":"BSL"
# }


@cancel_orders_blueprint.route("/price/avg_sell_price", methods=['POST'])
def avg_sell_price():
    try:

        content_type = request.headers.get('Content-Type')
        if (content_type == 'application/json'):
            request_json = request.get_json()
            ticker_symbol = request_json["Ticker_Symbol"]

            ipeo_price = json.loads(
                dumps(client.INVENTORY.LISTED_STOCKS.find({"Ticker_Symbol": ticker_symbol})))

            all_sell_orders = json.loads(
                dumps(client.Company_Sell_Order[ticker_symbol].find()))

            total_price: int = int(ipeo_price[0]['IPEO_Price'])
            total_div: int = 1

            for ind_sell_order in all_sell_orders:
                total_price += int(ind_sell_order['Price_Per_Unit']
                                   * ind_sell_order['Units'])
                total_div += int(ind_sell_order['Units'])
                # print(ind_sell_order)

                # temp = json.loads(

            return dumps(total_price/total_div)
        else:
            return 'Content-Type not supported'
    except Exception as e:
        return dumps({'error': str(e)})
