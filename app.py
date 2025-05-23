# main function to call the APIs
from flask import Flask
from flask import Blueprint
from Company_List import LISTED_STOCKSAPIs
from Auth import AuthenticateAPI
from Wallet import UsersWalletAPI
from StocksManipAPII import BuyStocksAPI, SellStocksAPI, CancelOrders
from User_Details import User_Details_Apis
from flask_cors import CORS


app = Flask('REST_API')
CORS(app)  # This will enable CORS for all routes

app.register_blueprint(LISTED_STOCKSAPIs.query_blueprint)
app.register_blueprint(AuthenticateAPI.authenticate_blueprint)
app.register_blueprint(UsersWalletAPI.wallet_blueprint)
app.register_blueprint(BuyStocksAPI.buy_stocks_blueprint)
app.register_blueprint(SellStocksAPI.sell_stocks_blueprint)
app.register_blueprint(User_Details_Apis.user_details_blueprint)
app.register_blueprint(CancelOrders.cancel_orders_blueprint)

# app.run(debug=True, use_debugger=False, use_reloader=False)


@app.route('/status')
def restApiCaller():
    return "KuruX Portal running"
