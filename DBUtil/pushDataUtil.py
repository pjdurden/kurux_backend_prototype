

import json
from flask import request


def pushData(stock_Name, stock_Price):
    return {'stock_Name': stock_Name, 'stock_Price': stock_Price}
