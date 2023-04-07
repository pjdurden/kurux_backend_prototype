from flask import Flask
app = Flask('New_app')


@app.route("/")
def hello():
    return "Welcome to Python Flask!"
