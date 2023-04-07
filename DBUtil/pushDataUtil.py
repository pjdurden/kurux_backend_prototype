

import json
from flask import request


def dataToPush(dataToSend):
    data = json.loads(request.data)
    stock_Name = data[dataToSend[0]]
    stock_Price = data[dataToSend[1]]
    return {"stock_Name": stock_Name, "stock_Price": stock_Price}
