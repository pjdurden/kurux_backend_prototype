# main function to call the APIs
from flask import Flask
from flask import Blueprint
from RestClient.ClientConnection import *


app = Flask('REST_API')

app.register_blueprint(query_blueprint)


@app.route('/status')
def restApiCaller():
    return "Application running"
