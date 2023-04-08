# Kurux-Backend-Prototype
Prototype Backend for Kurux Based on Flask and MongoDB for a Scalable DB and Rest APIs

The following commands need to be run before running the application. 

make sure python is installed and Mongo DB is setup

pip install flask
pip install pymongo

before running the flask application
first set your mongodb link in env.py
and then run this - 
python3 dbcreation.py
(to create tables and collection and insert mock data) 

To run the app do this 
$ flask --app hello run

to run the app in debug mode in VSCODE
$ flask --app hello run --debug --no-debugger --no-reload

