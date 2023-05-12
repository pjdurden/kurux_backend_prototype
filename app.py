# main function to call the APIs
from flask import Flask
from flask import Blueprint
from Company_List import LISTED_STOCKSAPIs
from Auth import AuthenticateAPI
from Wallet import UsersWalletAPI
from StocksManipAPII import BuyStocksAPI, SellStocksAPI


app = Flask('REST_API')

app.register_blueprint(LISTED_STOCKSAPIs.query_blueprint)
app.register_blueprint(AuthenticateAPI.authenticate_blueprint)
app.register_blueprint(UsersWalletAPI.wallet_blueprint)
app.register_blueprint(BuyStocksAPI.buy_stocks_blueprint)
app.register_blueprint(SellStocksAPI.sell_stocks_blueprint)

# app.run(debug=True, use_debugger=False, use_reloader=False)


@app.route('/status')
def restApiCaller():
    return "Application running"
